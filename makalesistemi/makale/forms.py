from django import forms
from .models import Makale, Mesaj, AnonimlestirmeSecimi, HakemDegerlendirmesi
from .models import Makale, AnonimlestirmeSecimi, Mesaj, HakemeYollamaKaydi
from .models import Hakem
from django import forms
from .models import HakemDegerlendirme

# Kullanıcı makale yükleme formu
class MakaleYukleForm(forms.ModelForm):
    class Meta:
        model = Makale
        fields = ['email', 'pdf']  # sadece e-posta ve PDF

# Durum sorgulama formu
class DurumSorgulaForm(forms.Form):
    takip_numarasi = forms.CharField(label="Takip Numarası", max_length=10)
    email = forms.EmailField(label="E-posta")

# Mesaj formları (kullanıcı ve editör aynı modeli kullanıyor)
class MesajForm(forms.ModelForm):
    class Meta:
        model = Mesaj
        fields = ['icerik']
        widgets = {
            'icerik': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Mesajınızı yazınız...'})
        }

class KullaniciMesajForm(forms.ModelForm):
    class Meta:
        model = Mesaj
        fields = ['icerik']
        widgets = {
            'icerik': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Editöre mesajınızı yazınız...'})
        }

# Editörün anonimleştirme ayar formu
class AnonimlestirmeForm(forms.ModelForm):
    class Meta:
        model = AnonimlestirmeSecimi
        fields = ['ad_soyad', 'e_posta', 'kurum']
        labels = {
            'ad_soyad': 'Yazar Ad-Soyad',
            'e_posta': 'E-posta Adresi',
            'kurum': 'Kurum Bilgisi'
        }

# Revize edilen makale için yeniden yükleme formu
class RevizeMakaleForm(forms.ModelForm):
    class Meta:
        model = Makale
        fields = ['pdf']
        labels = {
            'pdf': 'Revize PDF'
        }

class HakemeYollaForm(forms.ModelForm):
    class Meta:
        model = HakemeYollamaKaydi
        fields = ['hakem']
        labels = {
            'hakem': 'Hakem Seçin'
        }

class HakemDegerlendirmeForm(forms.ModelForm):
    class Meta:
        model = HakemDegerlendirme
        fields = ['yorum']
        labels = {'yorum': "Değerlendirme Yorumunuz"}
        widgets = {
            'yorum': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Hakem yorumunuzu giriniz...'})
        }