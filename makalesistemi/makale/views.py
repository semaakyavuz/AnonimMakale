from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings
import os
from .models import HakemDegerlendirme
from .forms import HakemDegerlendirmeForm
from .utils import anonymize_pdf, append_text_to_pdf

from .models import Makale, Mesaj, AnonimlestirmeSecimi, Hakem, HakemeYollamaKaydi
from .forms import (
    MakaleYukleForm, DurumSorgulaForm, MesajForm,
    RevizeMakaleForm, AnonimlestirmeForm,
    KullaniciMesajForm, HakemeYollaForm
)
from django.db import models
from .models import Makale  # varsa
from .utils import anonymize_pdf
from .models import HakemeYollamaKaydi

def makale_yukle(request):
    takip_no = None
    if request.method == 'POST':
        form = MakaleYukleForm(request.POST, request.FILES)
        if form.is_valid():
            makale = form.save()
            takip_no = makale.takip_numarasi
    else:
        form = MakaleYukleForm()
    
    return render(request, 'makale/yukle.html', {
        'form': form,
        'takip_no': takip_no
    })


def durum_sorgula(request):
    makale = None
    mesajlar = None
    mesaj_form = None
    revize_form = None
    form = DurumSorgulaForm()
    gonderildi = False

    if request.method == 'POST':
        if 'takip_numarasi' in request.POST:
            form = DurumSorgulaForm(request.POST)
            if form.is_valid():
                takip_no = form.cleaned_data['takip_numarasi']
                email = form.cleaned_data['email']
                try:
                    makale = Makale.objects.get(takip_numarasi=takip_no, email=email)
                    mesajlar = Mesaj.objects.filter(makale=makale).order_by('-tarih')
                    mesaj_form = KullaniciMesajForm()
                    revize_form = RevizeMakaleForm()
                except Makale.DoesNotExist:
                    messages.error(request, "Bu bilgilere ait makale bulunamadı.")

        elif 'revize_pdf' in request.POST:
            makale = Makale.objects.get(id=request.POST.get('makale_id'))
            revize_form = RevizeMakaleForm(request.POST, request.FILES, instance=makale)
            if revize_form.is_valid():
                revize_form.save()
                makale.guncellendi = True
                makale.save()
                gonderildi = True
            form = DurumSorgulaForm()
            mesaj_form = KullaniciMesajForm()
            mesajlar = Mesaj.objects.filter(makale=makale).order_by('-tarih')

        elif 'mesaj_gonder' in request.POST:
            makale = Makale.objects.get(id=request.POST.get('makale_id'))
            mesaj_form = KullaniciMesajForm(request.POST)
            if mesaj_form.is_valid():
                mesaj = mesaj_form.save(commit=False)
                mesaj.makale = makale
                mesaj.kullanici_gonderdi = True
                mesaj.save()
                gonderildi = True
            form = DurumSorgulaForm()
            revize_form = RevizeMakaleForm()
            mesajlar = Mesaj.objects.filter(makale=makale).order_by('-tarih')

    return render(request, 'makale/durum_sorgula.html', {
        'form': form,
        'makale': makale,
        'revize_form': revize_form,
        'mesaj_form': mesaj_form,
        'mesajlar': mesajlar,
        'gonderildi': gonderildi
    })


def editore_panel(request):
    makaleler = Makale.objects.all().order_by('-yukleme_tarihi')
    secili_makale = None
    form = None
    mesajlar = None
    gonderildi = False
    hakem_form = None
    hakem_degerlendirmeleri = []

    if request.method == 'POST':
        makale_id = request.POST.get('makale_id')
        secili_makale = Makale.objects.get(id=makale_id)

        if 'append_evaluation' in request.POST:
            # Get the evaluation
            degerlendirme = HakemDegerlendirme.objects.get(id=request.POST.get('degerlendirme_id'))
            
            # Create output path for the evaluated PDF
            output_filename = f"{secili_makale.takip_numarasi}_degerlendirilmis.pdf"
            output_path = os.path.join(settings.MEDIA_ROOT, "degerlendirmeler", output_filename)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Add evaluation with prefix to the PDF
            evaluation_text = f"Hakem Değerlendirmesi: {degerlendirme.yorum}"
            append_text_to_pdf(secili_makale.pdf.path, output_path, evaluation_text)
            
            # Update the makale record with the evaluated PDF
            secili_makale.degerlendirme_pdf = os.path.join("degerlendirmeler", output_filename)
            secili_makale.save()
            
            messages.success(request, "Değerlendirme başarıyla PDF'e eklendi.")
            
        elif 'hakeme_yolla' in request.POST:
            # Check if article is already assigned
            existing_assignment = HakemeYollamaKaydi.objects.filter(makale=secili_makale).first()
            if existing_assignment:
                messages.error(request, f"❌ Bu makale zaten {existing_assignment.hakem.isim} isimli hakeme atanmış.")
                hakem_form = None
            else:
                hakem_form = HakemeYollaForm(request.POST)
                if hakem_form.is_valid():
                    try:
                        kayit = hakem_form.save(commit=False)
                        kayit.makale = secili_makale
                        kayit.save()
                        messages.success(request, f"✅ Makale başarıyla {kayit.hakem.isim} isimli hakeme yönlendirildi.")
                        hakem_form = None
                    except Exception as e:
                        messages.error(request, "❌ Bu makale zaten bir hakeme atanmış.")
        else:
            form = MesajForm(request.POST)
            mesajlar = Mesaj.objects.filter(makale=secili_makale).order_by('-tarih')
            if form.is_valid():
                mesaj = form.save(commit=False)
                mesaj.makale = secili_makale
                mesaj.save()
                gonderildi = True
                form = MesajForm()

    elif request.GET.get('makale_id'):
        makale_id = request.GET.get('makale_id')
        secili_makale = Makale.objects.get(id=makale_id)
        form = MesajForm()
        mesajlar = Mesaj.objects.filter(makale=secili_makale).order_by('-tarih')
        hakem_degerlendirmeleri = HakemDegerlendirme.objects.filter(makale=secili_makale)

        # Only show hakem form if article is not already assigned
        if not HakemeYollamaKaydi.objects.filter(makale=secili_makale).exists():
            hakem_form = HakemeYollaForm()
        else:
            existing_assignment = HakemeYollamaKaydi.objects.get(makale=secili_makale)
            messages.info(request, f"ℹ️ Bu makale {existing_assignment.hakem.isim} isimli hakeme atanmış.")

    return render(request, 'makale/editore_panel.html', {
        'makaleler': makaleler,
        'form': form,
        'secili_makale': secili_makale,
        'mesajlar': mesajlar,
        'gonderildi': gonderildi,
        'hakem_form': hakem_form,
        'hakem_degerlendirmeleri': hakem_degerlendirmeleri
    })


def anonimlestir(request, makale_id):
    makale = get_object_or_404(Makale, id=makale_id)
    secim, _ = AnonimlestirmeSecimi.objects.get_or_create(makale=makale)

    # Formları başta tanımla
    form = AnonimlestirmeForm(instance=secim)
    hakem_form = HakemeYollaForm()

    # Get existing assignment info
    existing_assignment = HakemeYollamaKaydi.objects.filter(makale=makale).first()

    if request.method == 'POST':
        if 'hakeme_yolla' in request.POST:
            if existing_assignment:
                messages.warning(request, f"Bu makale zaten {existing_assignment.hakem.isim} isimli hakeme atanmış.")
                hakem_form = HakemeYollaForm(request.POST)  # Keep the form with user's selection
            else:
                hakem_form = HakemeYollaForm(request.POST)
                if hakem_form.is_valid():
                    try:
                        kayit = hakem_form.save(commit=False)
                        kayit.makale = makale
                        kayit.save()
                        messages.success(request, f"Makale başarıyla {kayit.hakem.isim} isimli hakeme yönlendirildi.")
                        hakem_form = HakemeYollaForm()  # Reset form after successful submission
                    except Exception as e:
                        messages.error(request, "Bu makale zaten bir hakeme atanmış.")
                else:
                    messages.error(request, "Hakem seçimi sırasında hata oluştu.")
        else:
            form = AnonimlestirmeForm(request.POST, instance=secim)
            if form.is_valid():
                form.save()

                keywords = []
                if secim.ad_soyad and makale.ad_soyad:
                    keywords += [k.strip() for k in makale.ad_soyad.split(",")]
                if secim.ad_soyad:
                    keywords.append(makale.ad_soyad)
                if secim.e_posta:
                    keywords.append(makale.email)
                if secim.kurum:
                    keywords.append(makale.kurum)

                input_path = makale.pdf.path
                output_path = os.path.join(settings.MEDIA_ROOT, "anonim", f"{makale.takip_numarasi}_anonim.pdf")

                anonymize_pdf(input_path, output_path, keywords, secim=secim)

                makale.anonim_pdf = os.path.join("anonim", f"{makale.takip_numarasi}_anonim.pdf")
                makale.save()

                messages.success(request, "PDF başarıyla anonimleştirildi.")
            else:
                messages.error(request, "Anonimleştirme sırasında hata oluştu.")
    
    # Show info message about existing assignment but keep the form visible
    if existing_assignment:
        messages.info(request, f"ℹ️ Bu makale şu anda {existing_assignment.hakem.isim} isimli hakeme atanmış durumda.")

    return render(request, 'makale/anonimlestirme_form.html', {
        'form': form,
        'makale': makale,
        'hakem_form': hakem_form,
        'existing_assignment': existing_assignment  # Pass to template to show current assignment
    })


def hakeme_yolla(request, makale_id):
    makale = get_object_or_404(Makale, id=makale_id)

    # Check if the article is already assigned to a referee
    existing_assignment = HakemeYollamaKaydi.objects.filter(makale=makale).first()
    if existing_assignment:
        messages.warning(request, f"Bu makale zaten {existing_assignment.hakem.isim} isimli hakeme atanmış.")
        return redirect('anonimlestir', makale_id=makale_id)

    if request.method == 'POST':
        form = HakemeYollaForm(request.POST)
        if form.is_valid():
            try:
                kayit = form.save(commit=False)
                kayit.makale = makale
                kayit.save()
                messages.success(request, f"{makale.takip_numarasi} numaralı makale başarıyla {kayit.hakem.isim} isimli hakeme gönderildi.")
                return redirect('anonimlestir', makale_id=makale_id)
            except Exception as e:
                messages.error(request, "Bu makale zaten bir hakeme atanmış.")
                return redirect('anonimlestir', makale_id=makale_id)
    else:
        form = HakemeYollaForm()

    return render(request, 'makale/hakeme_yolla.html', {
        'form': form,
        'makale': makale
    })



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Hakem, HakemeYollamaKaydi, HakemDegerlendirme, Makale
from .forms import HakemDegerlendirmeForm

def hakem_panel(request, isim):
    try:
        hakem = get_object_or_404(Hakem, isim=isim)
        atamalar = HakemeYollamaKaydi.objects.filter(hakem=hakem)
    except Hakem.DoesNotExist:
        messages.error(request, "Böyle bir hakem bulunamadı.")
        return redirect('editore_panel')

    return render(request, 'hakem/hakem_panel.html', {
        'hakem': hakem,
        'atamalar': atamalar,
    })


def makale_degerlendir(request, hakem_id, makale_id):
    hakem = get_object_or_404(Hakem, id=hakem_id)
    makale = get_object_or_404(Makale, id=makale_id)

    # Check if already evaluated
    if HakemDegerlendirme.objects.filter(hakem=hakem, makale=makale).exists():
        messages.error(request, "Bu makaleye zaten değerlendirme yaptınız.")
        return redirect('hakem_panel_by_id', hakem_id=hakem_id)

    if request.method == 'POST':
        form = HakemDegerlendirmeForm(request.POST)
        if form.is_valid():
            degerlendirme = form.save(commit=False)
            degerlendirme.makale = makale
            degerlendirme.hakem = hakem
            degerlendirme.save()

            # Append evaluation to PDF
            input_path = makale.anonim_pdf.path
            output_filename = f"{makale.takip_numarasi}_degerlendirilmis.pdf"
            output_path = os.path.join(settings.MEDIA_ROOT, "degerlendirmeler", output_filename)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Prepare evaluation text
            evaluation_text = f"""
            HAKEM DEĞERLENDİRMESİ
            
            Değerlendirme Tarihi: {degerlendirme.tarih.strftime('%d.%m.%Y %H:%M')}
            Hakem: {hakem.isim}
            
            DEĞERLENDİRME:
            {degerlendirme.yorum}
            """
            
            # Add evaluation to PDF
            append_text_to_pdf(input_path, output_path, evaluation_text)
            
            # Save the path to the evaluated PDF
            kayit = HakemeYollamaKaydi.objects.get(hakem=hakem, makale=makale)
            kayit.degerlendirme_pdf = os.path.join("degerlendirmeler", output_filename)
            kayit.save()

            messages.success(request, "Değerlendirmeniz başarıyla kaydedildi.")
            return redirect('hakem_panel_by_id', hakem_id=hakem_id)
    else:
        form = HakemDegerlendirmeForm()

    return render(request, 'hakem/degerlendir.html', {
        'form': form,
        'makale': makale,
        'hakem': hakem
    })

def hakem_panel_takip_no(request, takip_numarasi):
    try:
        kayit = HakemeYollamaKaydi.objects.select_related('makale').get(makale__takip_numarasi=takip_numarasi)
        makale = kayit.makale
    except HakemeYollamaKaydi.DoesNotExist:
        messages.error(request, "Bu takip numarasına ait bir hakem yönlendirmesi bulunamadı.")
        return redirect('durum_sorgula')

    # Eğer daha önce değerlendirme yapıldıysa gösterme
    mevcut_degerlendirme = HakemDegerlendirme.objects.filter(makale=makale).first()

    if request.method == 'POST' and not mevcut_degerlendirme:
        form = HakemDegerlendirmeForm(request.POST)
        if form.is_valid():
            degerlendirme = form.save(commit=False)
            degerlendirme.makale = makale
            degerlendirme.save()
            messages.success(request, "Değerlendirme başarıyla gönderildi.")
            return redirect('hakem_panel', takip_numarasi=takip_numarasi)
    else:
        form = HakemDegerlendirmeForm()

    return render(request, 'makale/hakem_panel.html', {
        'makale': makale,
        'form': form,
        'mevcut': mevcut_degerlendirme
    })
from .models import Hakem, HakemeYollamaKaydi

# Hakem Listesi Görüntüleme
def hakem_listesi(request):
    hakemler = Hakem.objects.all()
    return render(request, 'hakem/hakem_listesi.html', {'hakemler': hakemler})

# Seçilen Hakemin Paneli
def hakem_panel_isim(request, isim):
    hakem = get_object_or_404(Hakem, isim=isim)
    
    # Get all assignments for this hakem
    hakem_assignments = HakemeYollamaKaydi.objects.filter(hakem=hakem)
    
    # Get all evaluations by this hakem
    degerlendirmeler = HakemDegerlendirme.objects.filter(hakem=hakem)
    
    # Create a list of papers with their evaluation status
    makaleler = []
    for assignment in hakem_assignments:
        makale_info = {
            'makale': assignment.makale,
            'assignment_date': assignment.tarih,
            'degerlendirme': degerlendirmeler.filter(makale=assignment.makale).first(),
        }
        makaleler.append(makale_info)
    
    context = {
        'hakem': hakem,
        'makaleler': makaleler,
    }
    
    return render(request, 'makale/hakem_panel.html', context)

from .models import Makale, HakemDegerlendirme, HakemeYollamaKaydi
from .forms import HakemDegerlendirmeForm

def hakem_degerlendirme(request, makale_id):
    # Makaleyi ve atama kaydını kontrol et
    makale = get_object_or_404(Makale, id=makale_id)
    atama_kaydi = HakemeYollamaKaydi.objects.filter(makale=makale).first()
    
    if not atama_kaydi:
        return render(request, 'error.html', {'message': 'Bu makale için hakem ataması bulunamadı.'})
    
    # Hakemin daha önce değerlendirme yapıp yapmadığını kontrol et
    mevcut_degerlendirme = HakemDegerlendirme.objects.filter(makale=makale, hakem=atama_kaydi.hakem).first()
    
    if mevcut_degerlendirme:
        return render(request, 'error.html', {'message': 'Bu makale için zaten bir değerlendirme yaptınız.'})

    if request.method == 'POST':
        form = HakemDegerlendirmeForm(request.POST)
        if form.is_valid():
            HakemDegerlendirme.objects.create(
                makale=makale,
                hakem=atama_kaydi.hakem,
                yorum=form.cleaned_data['yorum']
            )
            makale.durum = 'Değerlendirildi'
            makale.save()
            return redirect('degerlendirme_basarili')
    else:
        form = HakemDegerlendirmeForm()

    return render(request, 'hakem_degerlendirme.html', {
        'form': form,
        'makale': makale,
        'hakem': atama_kaydi.hakem
    })

def degerlendirme_basarili(request):
    return render(request, 'degerlendirme_basarili.html')

def hakem_panel(request):
    # Hakemlerin atanmış olduğu makaleleri görüntüleyebileceği bir panel
    makaleler = HakemeYollamaKaydi.objects.all()
    return render(request, 'hakem/hakem_panel.html', {'makaleler': makaleler})

def hakem_panel_by_id(request, hakem_id):
    # Get the hakem object or return 404 if not found
    hakem = get_object_or_404(Hakem, id=hakem_id)
    
    # Get all assignments for this hakem
    hakem_assignments = HakemeYollamaKaydi.objects.filter(hakem=hakem)
    
    # Get all evaluations by this hakem
    degerlendirmeler = HakemDegerlendirme.objects.filter(hakem=hakem)
    
    # Create a list of papers with their evaluation status
    makaleler = []
    for assignment in hakem_assignments:
        makale_info = {
            'makale': assignment.makale,
            'assignment_date': assignment.tarih,
            'degerlendirme': degerlendirmeler.filter(makale=assignment.makale).first(),
        }
        makaleler.append(makale_info)
    
    context = {
        'hakem': hakem,
        'makaleler': makaleler,
    }
    
    return render(request, 'makale/hakem_panel.html', context)

