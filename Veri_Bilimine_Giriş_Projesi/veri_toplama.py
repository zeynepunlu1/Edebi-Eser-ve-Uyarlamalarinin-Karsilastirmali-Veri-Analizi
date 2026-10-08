# KÜTÜPHANELERİN EKLENMESİ
import pandas as pd # Excel dosyalarını okumak, veri tabloları (DataFrame) oluşturmak ve yönetmek için kullanılır.
import numpy as np # Büyük veri dizileri ve matematiksel/istatistiksel işlemler için kullanılır.
import matplotlib.pyplot as plt # Veri analizi sonuçlarını çizgi, bar veya pasta grafiğine dönüştürmek için temel çizim kütüphanesidir.
import seaborn as sns # Matplotlib tabanlı, daha gelişmiş, estetik ve modern veri görselleştirme grafikler çizmek için kullanılır.
import requests # İnternetteki API'lere bağlanıp veri çekmek için kullanılır.
import time # API istekleri arasına küçük bekleme süreleri koyarak sunucuları yormamak ve ban yememek için kullanılır.


# Verisi çekilecek eserler listesi dosyasının adını bir değişkene atıyoruz.
dosya_adi = 'eserler.xlsx' 
try:
    df = pd.read_excel(dosya_adi) # pandas kütüphanesini kullanarak eserler.xlsx dosyasını okuyor ve 'df' isimli bir tabloya dönüştürüyoruz.
    print(f" '{dosya_adi}' dosyası başarıyla okundu.")
    print(f"Toplam {len(df)} adet eser için işlem başlatıldı.\n") # len(df) komutuyla listede kaç tane eser olduğunu öğrenip ekrana yazdırıyoruz.
except FileNotFoundError:
    # Eğer belirtilen isimde bir Excel dosyası klasörde yoksa kodun çökmesini engelleyip kullanıcıya hata mesajı gösteriyoruz.
    print(f"HATA: '{dosya_adi}' dosyası bulunamadı! Dosya adını kontrol edin.")
    exit() # Dosya olmadan veri çekme adımına geçilemeyeceği için programın çalışmasını güvenli bir şekilde sonlandırıyoruz.

OMDB_API_KEY = "ee1dbbc2"
BOOKS_API_KEY = "AIzaSyCFcyFqlqyiRtUU8Lxp1v5DNd_mQe39xWg"

# İnternetten veri çekecek olan ana fonksiyonumuzu tanımlıyoruz. (Her bir eser ismi için bu fonksiyon tetiklenecek.)
def imdb_and_books_fetcher(eser_adi):
    print(f"Şu anda {eser_adi} adlı eserin verisi çekiliyor") # Terminalde hangi eserin verisinin çekildiğini anlık olarak takip edebilmek için ekrana yazdırıyoruz.
    # API'den veri gelmeme ihtimaline karşı başlangıçta içi boş (None) olan bir veri sözlüğü (dictionary) hazırlıyoruz.
    veri = {
        'IMDb_Puani': None, 'Film_Yili': None, 'Yonetmen': None,
        'Film_Turu': None, 'Film_Odulleri': None, 'Eser_Tipi': None,
        'Film_Suresi': None, 'Sezon_Sayisi': None,
        'Gise_Hasilati_USD': None,
        'Kitap_Puani': None, 'Sayfa_Sayisi': None, 'Yazar': None
    }
    # GOOGLE BOOKS API İLE KİTAP VERİLERİNİN ÇEKİLMESİ
    try:
        # Eser adını web diline (URL encoding) çevirip Google Books'un arama linkine bağlıyoruz.
        books_url = f"https://www.googleapis.com/books/v1/volumes?q={requests.utils.quote(str(eser_adi))}&key={BOOKS_API_KEY}&langRestrict=en"
        books_response = requests.get(books_url, timeout=5).json() # Google Books'a istek gönderip gelen cevabı Python'ın okuyabileceği JSON formatına çeviriyoruz.
        # Eğer arama sonucunda Google Books bize en az bir tane kitap sonucu ('items') döndürdüyse:
        if 'items' in books_response:
            for item in books_response['items']:
                volume_info = item['volumeInfo'] 
                puan = volume_info.get('averageRating')
                if puan: # Puan bulunduysa al ve döngüden çık
                    # Kitap puanını ve sayfa sayısını çekip sözlüğümüze kaydediyoruz.
                    veri['Kitap_Puani'] = puan
                    veri['Sayfa_Sayisi'] = volume_info.get('pageCount')
                    authors = volume_info.get('authors', []) # Kitabın yazarlarını bir liste olarak çekiyoruz.
                    veri['Yazar'] = ", ".join(authors) if authors else None # Kitabın birden fazla yazarı varsa, tüm yazarları aralarına virgül koyarak tek bir metin halinde birleştiriyoruz.
                    break
            # Hiçbirinde puan yoksa ilk sonucun diğer bilgilerini al
            if not veri['Yazar']:
                volume_info = books_response['items'][0]['volumeInfo']
                veri['Sayfa_Sayisi'] = volume_info.get('pageCount')
                authors = volume_info.get('authors', [])
                veri['Yazar'] = ", ".join(authors) if authors else None
    # API'lerde anlık bir kopma veya hata olursa programın durmasını engellemek için hatayı geçiyoruz.
    except Exception:
        pass
    # OMDb API (IMDb) İLE FİLM/DİZİ VERİLERİNİ ÇEKME
    try:
        # Eser adını web diline çevirip çalışan API anahtarımızla birlikte OMDb (IMDb veritabanı) sorgu linkini oluşturuyoruz.
        # requests.utils.quote fonksiyonu  Excel'den gelen eser adını alır; içindeki internete yasak olan tüm karakterleri bulur ve onları dünya standartlarında  güvenli kodlara dönüştürür.
        omdb_url = f"http://www.omdbapi.com/?t={requests.utils.quote(str(eser_adi))}&apikey={OMDB_API_KEY}"
        
        # Hazırladığımız film URL'ine internet üzerinden istek gönderip gelen cevabı JSON formatına çeviriyoruz.
        omdb_response = requests.get(omdb_url, timeout=5).json()
        
        # Eğer film/dizi veritabanında bu isimde bir eser başarıyla bulunduysa:
        if omdb_response.get('Response') == 'True':
            imdb_rating = omdb_response.get('imdbRating')
            # Puan 'N/A' (Yok) değilse sayıya (float) çevirip kaydediyoruz.
            # Aksi halde Excel tablosuna boş veri anlamına gelen None yazılır.
            veri['IMDb_Puani'] = float(imdb_rating) if imdb_rating != 'N/A' else None
            
            # Yıl ve Yönetmen bilgilerini alıyoruz.
            veri['Film_Yili'] = omdb_response.get('Year')
            veri['Yonetmen'] = omdb_response.get('Director')
            
            # API'den gelen Tür ve Ödül verilerini çekip sözlüğümüze kaydediyoruz.
            veri['Film_Turu'] = omdb_response.get('Genre')
            veri['Film_Odulleri'] = omdb_response.get('Awards')
            # API'den gelen eser tipi(dizi/film) film süresi sezon sayısı ve gişe hasılatı verilerini çekip sözlüğümüze kaydediyoruz.
            veri['Eser_Tipi'] = omdb_response.get('Type')
            veri['Film_Suresi'] = omdb_response.get('Runtime')
            veri['Sezon_Sayisi'] = omdb_response.get('totalSeasons')
            veri['Gise_Hasilati_USD'] = omdb_response.get('BoxOffice')
    except Exception:
        pass
        
    # Karşı sunuculardan ban yememek için iki istek arasında 0.3 saniye dinleniyoruz.
    time.sleep(0.3)
    
    # Topladığımız tüm satır verisini Pandas yapısına (Series) dönüştürüp ana programa return ediyoruz.
    return pd.Series(veri)


# VERİLERİN ÇEKİLMESİ VE EXCEL'E AKTARILMASI

print("API'lardan veri çekme işlemi başladı.\n")

# .apply() fonksiyonu ile tablodaki tüm satırları sırasıyla imdb_and_books_fetcher fonksiyonuna gönderip detayları topluyoruz.
detaylar = df['Eser_Adi'].apply(imdb_and_books_fetcher)

# Orijinal tablomuz (df) ile internetten yeni çektiğimiz sütunları (detaylar) yan yana (axis=1) birleştiriyoruz.
df = pd.concat([df, detaylar], axis=1)

# Sonuçları klasörün içine güncel bir Excel dosyası olarak yazıyoruz.
df.to_excel('guncel_eserler_veri_seti.xlsx', index=False)

print("\nTüm veriler çekildi ve 'guncel_eserler_veri_seti.xlsx' oluşturuldu.")