from django.contrib import admin
from django.urls import path
from makale import views
from django.conf import settings
from django.conf.urls.static import static
from makale.views import (
    hakem_degerlendirme,
    degerlendirme_basarili,
    hakem_panel,
    makale_degerlendir,
    hakem_panel_isim,
    hakem_panel_by_id
)

urlpatterns = [
    # Admin Paneli
    path('admin/', admin.site.urls),

    # Kullanıcı (Yazar) İşlemleri
    path('', views.makale_yukle, name='makale_yukle'),
    path('durum/', views.durum_sorgula, name='durum_sorgula'),

    # Editör İşlemleri
    path('editor/', views.editore_panel, name='editore_panel'),
    path('editor/anonimlestir/<int:makale_id>/', views.anonimlestir, name='anonimlestir'),
    path('editor/hakeme-yolla/<int:makale_id>/', views.hakeme_yolla, name='hakeme_yolla'),

    # Hakem İşlemleri
    path('hakem/', views.hakem_listesi, name='hakem_listesi'),  # Hakem listesi
    path('hakem/id/<int:hakem_id>/', hakem_panel_by_id, name='hakem_panel_by_id'),  # Hakem paneli (ID ile)
    path('hakem/<str:isim>/', hakem_panel_isim, name='hakem_panel_isim'),  # Hakem özel paneli
    path('hakem/<int:hakem_id>/degerlendir/<int:makale_id>/', makale_degerlendir, name='makale_degerlendir'),  # Hakem değerlendirme

    # Takip Numarası ile Hakem Paneli
    path('hakem/takip/<str:takip_numarasi>/', views.hakem_panel, name='hakem_panel_takip'),

    # Hakem Değerlendirme İşlemleri
    path('hakem-degerlendirme/<int:makale_id>/', hakem_degerlendirme, name='hakem_degerlendirme'),
    path('degerlendirme-basarili/', degerlendirme_basarili, name='degerlendirme_basarili'),

    # Hakem Genel Paneli
    path('hakem-paneli/', views.hakem_panel, name='hakem_panel'),
]

# Statik ve medya dosyaları için
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
