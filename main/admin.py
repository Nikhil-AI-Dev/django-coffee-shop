from django.contrib import admin
from .models import MenuItem, Order

class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'is_available', 'category')  # ✅ include category
    list_filter = ('category', 'is_available', 'is_featured', 'is_discounted')
    search_fields = ('name', 'description')
admin.site.register(MenuItem, MenuItemAdmin)
