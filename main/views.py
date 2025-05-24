from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string, get_template
from django.db.models import Sum, F
from django.utils.timezone import now, timedelta
from .models import MenuItem, Order
from .forms import OrderForm
from xhtml2pdf import pisa
from io import BytesIO
import csv
import json
from django.db.models.functions import TruncDate

# Home Page
def home(request):
    return render(request, 'main/home.html')

# Menu Page with Search & Filter
def menu(request):
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    items = MenuItem.objects.all()

    if query:
        items = items.filter(name__icontains=query)
    if category:
        items = items.filter(category=category)

    return render(request, 'main/menu.html', {
        'items': items,
        'query': query,
        'category': category,
        'no_results': not items.exists()
    })

# Place Order@login_required
def place_order(request):
    item_id = request.GET.get('item')
    item = get_object_or_404(MenuItem, pk=item_id)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.menu_item = item
            order.user = request.user
            order.save()
            return redirect('thank_you', order_id=order.id)
    else:
        form = OrderForm()

    return render(request, 'main/place_order.html', {'form': form, 'item': item})

# Thank You + Email Receipt@login_required
def thank_you(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    total_price = order.menu_item.price * order.quantity
    user_email = request.user.email

    html = render_to_string('main/receipt.html', {
        'order': order,
        'total_price': total_price,
        'user_email': user_email,
    })

    pdf_file = BytesIO()
    pisa.CreatePDF(BytesIO(html.encode("UTF-8")), dest=pdf_file)
    pdf_file.seek(0)

    email = EmailMessage(
        subject='Your Dearborn Coffee Receipt',
        body='Thank you for your order! Please find the receipt attached.',
        from_email='noreply@dearborncoffee.com',
        to=[user_email],
    )
    email.attach('receipt.pdf', pdf_file.read(), 'application/pdf')
    email.send(fail_silently=True)

    return render(request, 'main/thank_you.html', {
        'order': order,
        'total_price': total_price,
        'user_email': user_email,
    })

# My Orders@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'main/my_orders.html', {'orders': orders})

# Static Pages
def about(request):
    return render(request, 'main/about.html')

def contact(request):
    return render(request, 'main/contact.html')

def locations(request):
    return render(request, 'main/locations.html')

# Download Receipt@login_required
def download_receipt(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    total_price = order.menu_item.price * order.quantity
    context = {'order': order, 'total_price': total_price}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_order_{order.id}.pdf"'

    template = get_template('main/receipt.html')
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had errors generating the PDF <pre>' + html + '</pre>')
    return response

# Export CSV@staff_member_required
def export_orders_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Order ID', 'User', 'Menu Item', 'Quantity', 'Price per Item', 'Total', 'Date'])

    orders = Order.objects.select_related('menu_item', 'user').all()
    for order in orders:
        writer.writerow([
            order.id,
            order.user.username,
            order.menu_item.name,
            order.quantity,
            order.menu_item.price,
            order.menu_item.price * order.quantity,
            order.created_at.strftime('%Y-%m-%d %H:%M')
        ])

    return response

# Admin Dashboard@staff_member_required
def admin_dashboard(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    product = request.GET.get('product', '')
    min_revenue = request.GET.get('min_revenue')

    orders = Order.objects.select_related('menu_item').all()

    if start_date:
        orders = orders.filter(created_at__date__gte=start_date)
    if end_date:
        orders = orders.filter(created_at__date__lte=end_date)
    if product:
        orders = orders.filter(menu_item__name__icontains=product)

    if min_revenue:
        orders = [o for o in orders if o.menu_item.price * o.quantity >= float(min_revenue)]

    total_orders = len(orders)
    total_revenue = sum(o.menu_item.price * o.quantity for o in orders)

    today = now().date()
    today_revenue = sum(
        o.menu_item.price * o.quantity for o in orders if o.created_at.date() == today
    )

    top_items = (
        Order.objects.values('menu_item__name')
        .annotate(total=Sum('quantity'))
        .order_by('-total')[:5]
    )

    recent_orders = Order.objects.filter(created_at__gte=now() - timedelta(days=7))

    # Revenue Chart Data
    revenue_qs = (
        Order.objects.filter(created_at__gte=now() - timedelta(days=7))
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(total=Sum(F('menu_item__price') * F('quantity')))
        .order_by('day')
    )

    chart_labels = [entry['day'].strftime('%b %d') for entry in revenue_qs]
    chart_data = [float(entry['total']) for entry in revenue_qs]  

    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'today_revenue': today_revenue,
        'top_items': top_items,
        'recent_orders': recent_orders,
        'start_date': start_date,
        'end_date': end_date,
        'product': product,
        'min_revenue': min_revenue,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }

    return render(request, 'main/admin_dashboard.html', context)

# Search View (if needed)
def search_view(request):
    query = request.GET.get('q', '')
    results = MenuItem.objects.filter(name__icontains=query)
    return render(request, 'main/search_view.html', {'results': results, 'query': query})
