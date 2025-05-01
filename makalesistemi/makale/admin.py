from django.contrib import admin
from .models import Makale, Mesaj, AnonimlestirmeSecimi, HakemDegerlendirmesi, LogKaydi

@admin.register(Makale)
class MakaleAdmin(admin.ModelAdmin):
    list_display = ("takip_numarasi", "email", "yukleme_tarihi", "guncellendi")
    search_fields = ("takip_numarasi", "email", "ad_soyad", "kurum")
    list_filter = ("guncellendi", "yukleme_tarihi")

@admin.register(Mesaj)
class MesajAdmin(admin.ModelAdmin):
    list_display = ("makale", "tarih")
    search_fields = ("icerik",)
    list_filter = ("tarih",)

@admin.register(AnonimlestirmeSecimi)
class AnonimlestirmeSecimiAdmin(admin.ModelAdmin):
    list_display = ("makale", "ad_soyad", "e_posta", "kurum")

@admin.register(HakemDegerlendirmesi)
class HakemDegerlendirmesiAdmin(admin.ModelAdmin):
    list_display = ("makale", "tarih")
    search_fields = ("yorum",)

@admin.register(LogKaydi)
class LogKaydiAdmin(admin.ModelAdmin):
    list_display = ("makale", "tarih", "aciklama")
    search_fields = ("aciklama",)
