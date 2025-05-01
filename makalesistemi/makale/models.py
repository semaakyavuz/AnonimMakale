from django.db import models
import random
import string

# Otomatik benzersiz takip numarası üret
def benzersiz_takip_no_uret():
    while True:
        kod = 'PDF' + ''.join(random.choices(string.digits, k=5))
        if not Makale.objects.filter(takip_numarasi=kod).exists():
            return kod

# Kullanıcının yüklediği makale
class Makale(models.Model):
    takip_numarasi = models.CharField(max_length=10, unique=True, editable=False, default=benzersiz_takip_no_uret)
    email = models.EmailField()
    ad_soyad = models.CharField(max_length=100, blank=True, null=True)
    kurum = models.CharField(max_length=150, blank=True, null=True)
    pdf = models.FileField(upload_to='makaleler/')
    anonim_pdf = models.FileField(upload_to='anonim/', blank=True, null=True)
    degerlendirme_pdf = models.FileField(upload_to='degerlendirmeler/', blank=True, null=True)
    yukleme_tarihi = models.DateTimeField(auto_now_add=True)
    guncellendi = models.BooleanField(default=False)

    def __str__(self):
        return self.takip_numarasi

# Kullanıcının editörle mesajlaşma sistemi
class Mesaj(models.Model):
    makale = models.ForeignKey(Makale, on_delete=models.CASCADE)
    icerik = models.TextField()
    tarih = models.DateTimeField(auto_now_add=True)
    kullanici_gonderdi = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.makale.takip_numarasi} - {self.tarih.strftime('%d.%m.%Y %H:%M')}"

# Editörün anonimleştirme seçenekleri (hangi bilgiler sansürlenecek)
class AnonimlestirmeSecimi(models.Model):
    makale = models.OneToOneField(Makale, on_delete=models.CASCADE)
    ad_soyad = models.BooleanField(default=False)
    e_posta = models.BooleanField(default=False)
    kurum = models.BooleanField(default=False)

    def __str__(self):
        return f"Anonim Ayarları - {self.makale.takip_numarasi}"

# Hakem değerlendirmesi
class HakemDegerlendirmesi(models.Model):
    makale = models.OneToOneField(Makale, on_delete=models.CASCADE)
    yorum = models.TextField()
    degerlendirme_pdf = models.FileField(upload_to='degerlendirme/', blank=True, null=True)
    tarih = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Hakem Yorumu - {self.makale.takip_numarasi}"

# Süreç log kaydı
class LogKaydi(models.Model):
    makale = models.ForeignKey(Makale, on_delete=models.CASCADE)
    aciklama = models.TextField()
    tarih = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log - {self.makale.takip_numarasi} - {self.tarih.strftime('%d.%m.%Y %H:%M')}"

class Hakem(models.Model):
    isim = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return f"{self.isim} ({self.email})"

class HakemeYollamaKaydi(models.Model):
    makale = models.OneToOneField(Makale, on_delete=models.CASCADE, unique=True)
    hakem = models.ForeignKey(Hakem, on_delete=models.CASCADE)
    degerlendirme_pdf = models.FileField(upload_to='degerlendirmeler/', blank=True, null=True)
    tarih = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Hakem Atama Kaydı"
        verbose_name_plural = "Hakem Atama Kayıtları"

    def __str__(self):
        return f"{self.makale.takip_numarasi} → {self.hakem.isim}"

class HakemDegerlendirme(models.Model):
    makale = models.OneToOneField(Makale, on_delete=models.CASCADE)
    hakem = models.ForeignKey(Hakem, on_delete=models.CASCADE)
    yorum = models.TextField()
    tarih = models.DateTimeField(auto_now_add=True)
    tamamlandi = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Hakem Değerlendirmesi"
        verbose_name_plural = "Hakem Değerlendirmeleri"

    def __str__(self):
        return f"{self.hakem.isim} - {self.makale.takip_numarasi}"

