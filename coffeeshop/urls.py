from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import Sitemap
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from main.models import MenuItem

# Sitemap for MenuItems
class MenuItemSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return MenuItem.objects.all()

    def location(self, item):
        return f"/menu/{item.id}/"

sitemaps = {
    'menuitems': MenuItemSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('accounts/', include('accounts.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]

# For media file serving during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
