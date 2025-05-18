from django import forms
from .models import Order, MenuItem

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['menu_item', 'quantity']

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        # ✅ Only include items with stock > 0
        self.fields['menu_item'].queryset = MenuItem.objects.filter(stock__gt=0)


