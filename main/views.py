from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import MenuItem, Order  # ✅ Include your models
from .forms import OrderForm
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template.loader import get_template

import tempfile

# Home Page
def home(request):
    return render(request, 'main/home.html')

# ✅ Updated Menu View with Search Support
def menu(request):
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')

    items = MenuItem.objects.all()

    if query:
        items = items.filter(name__icontains=query)

    if category:
        items = items.filter(category=category)

    no_results = not items.exists()

    return render(request, 'main/menu.html', {
        'items': items,
        'query': query,
        'category': category,
        'no_results': no_results,
    })


# Place Order View
@login_required
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

# Thank You Page
@login_required
def thank_you(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    total_price = order.menu_item.price * order.quantity
    user_email = request.user.email

    # Render HTML to string
    html = render_to_string('main/receipt.html', {
        'order': order,
        'total_price': total_price,
        'user_email': user_email,
    })

    # Generate PDF
    pdf_file = BytesIO()
    pisa.CreatePDF(BytesIO(html.encode("UTF-8")), dest=pdf_file)
    pdf_file.seek(0)

    # Send Email
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

# My Orders
@login_required
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

# Optional: Placeholder Search View (if needed elsewhere)
def search_view(request):
    return render(request, 'main/search_view.html')

@login_required
def download_receipt(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    total_price = order.menu_item.price * order.quantity
    template_path = 'main/receipt.html'
    context = {'order': order, 'total_price': total_price}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_order_{order.id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had errors generating the PDF <pre>' + html + '</pre>')
    return response
