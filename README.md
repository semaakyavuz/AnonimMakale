# Güvenli Belge Anonimleştirme Sistemi

Bu proje, akademik makalelerin ad-soyad, e-posta ve kurum bilgilerine göre otomatik olarak anonimleştirildiği, Django tabanlı bir web sistemidir. Editör, yazar ve hakem etkileşimini destekler. Amaç, hakem değerlendirme sürecinde gizliliği sağlamak ve süreci dijitalleştirmektir.

---

## 📋 İçindekiler

- [Proje Tanıtımı](#proje-tanıtımı)
- [Kullanılan Teknolojiler](#kullanılan-teknolojiler)
- [Kurulum Adımları](#kurulum-adımları)
- [Özellikler](#özellikler)
- [Uygulama Akışı](#uygulama-akışı)
- [Geliştirici Notları](#geliştirici-notları)
- [Lisans](#lisans)

---

## 📌 Proje Tanıtımı

Bu sistem, kullanıcıların PDF formatındaki makalelerini yüklediği, editörün bu makaleleri anonimleştirip hakemlere yönlendirdiği, hakemlerin ise değerlendirme yazısı yazabildiği bir platformdur. 

Anonimleştirme işlemi PyMuPDF kütüphanesi ile PDF içeriğinde ad, e-posta ve kurum bilgilerini siyah kutu ile sansürleyerek yapılır.

---

## 💻 Kullanılan Teknolojiler

- Python 3.11+
- Django 4.x
- PostgreSQL / SQLite
- PyMuPDF (`fitz`) – PDF anonimleştirme
- spaCy – Kişi isimlerini otomatik tespiti
- Regex – E-posta ve kurum tespiti
- HTML, CSS (Bootstrap)
- AES şifreleme (opsiyonel)

---

## ⚙️ Kurulum Adımları

1. Projeyi klonlayın:
   ```bash
   git clone https://github.com/semaakyavuz/AnonimMakale.git
   cd AnonimMakale
2.Sanal Ortam Oluşturun ve Etkinleştirin:
Sanal ortam oluşturun ve etkinleştirin:
python -m venv venv
venv\Scripts\activate  # (Mac/Linux: source venv/bin/activate)

3.Bağımlılıkları Yükleyin:
Projede kullanılan bağımlılıkları yüklemek için requirements.txt dosyasını kullanın:
pip install -r requirements.txt

4.Veritabanını Migrate Edin:
Veritabanı tablolarını oluşturmak için migrate komutunu çalıştırın:
python manage.py migrate

5.Sunucuyu Başlatın:
Sunucuyu başlatmak için aşağıdaki komutu kullanın:
python manage.py runserver

Sunucu başarıyla başlatıldıktan sonra, uygulamayı tarayıcınızda http://127.0.0.1:8000/ adresinde görüntüleyebilirsiniz.

🚀 Özellikler
Kullanıcılar PDF makale yükleyebilir.

Editör, sansürlenecek bilgi türlerini (ad, e-posta, kurum) seçer.

Sistem PDF içindeki bilgileri otomatik bulur ve siyah kutularla sansürler.

Sansürlü PDF media/anonim/ klasörüne kaydedilir.

Editör, makaleyi uygun bir hakeme yönlendirir.

Hakem, yalnızca kendine atanmış makaleyi görür ve değerlendirme yazısı girer.

Editör ve yazar arasında mesajlaşma sağlanır.

Revize yükleme ve işlem geçmişi (log) takibi yapılabilir.

🔄 Uygulama Akışı
Yazar: PDF makaleyi yükler ve durumunu sorgular.

Editör: Makaleyi kontrol eder, sansürlenecek bilgileri seçer ve anonimleştirir.

Editör: Anonim makaleyi hakeme atar.

Hakem: Makaleyi inceler, değerlendirme yorumunu yazar.

Editör: Yorumları kontrol eder ve yazara iletir.

Yazar: Gerekirse revize PDF’yi yükler.

🧠 Geliştirici Notları
utils.py, PDF içerisindeki bilgileri maskeleme/sansürleme işlemlerini yapar.

views.py içindeki anonimlestir fonksiyonu, editör seçimlerine göre PyMuPDF ile PDF üzerine siyah kutular ekler.

Anonimleştirilmiş dosyalar media/anonim/ klasörüne güvenli şekilde kaydedilir.

Hakem değerlendirme süreci, yalnızca atanmış kullanıcılarla sınırlıdır.

models.py dosyasında kullanıcı rolleri (editör, yazar, hakem) açık şekilde tanımlıdır.

📄 Lisans
Bu proje lisanslanmamıştır. Kullanım ve paylaşım için geliştirici izni gereklidir.
