# KÜTÜPHANELERİN EKLENMESİ
import pandas as pd # Excel dosyalarını okumak, veri tabloları (DataFrame) oluşturmak ve yönetmek için kullanılır.
import numpy as np  # Büyük veri dizileri ve matematiksel/istatistiksel işlemler için kullanılır.
import matplotlib.pyplot as plt # Veri analizi sonuçlarını çizgi, bar veya pasta grafiğine dönüştürmek için temel çizim kütüphanesidir.
import matplotlib.ticker as mticker # Grafik eksenlerindeki sayıları biçimlendirmek (örneğin eksene $100M yazdırmak) için kullanılır.
import seaborn as sns  # Matplotlib tabanlı, daha gelişmiş, estetik ve modern veri görselleştirme grafikler çizmek için kullanılır.
import re # Metinlerin (string) içinden belirli kalıpları (Regex kullanarak sadece sayıları vb.) seçmek için kullanılır.
import warnings # Kodun çalışmasını engellemeyen ancak ekranda kalabalık yapan uyarı mesajlarını yönetmek için eklenir.
warnings.filterwarnings('ignore') # Ekrana gelecek olan önemsiz uyarı mesajlarını tamamen gizler.

plt.rcParams['font.family'] = 'DejaVu Sans' 
sns.set_theme(style='whitegrid', palette='muted')

# VERİ OKUMA
df = pd.read_excel('guncel_eserler_veri_seti.xlsx') # Belirtilen Excel dosyasını okur ve 'df' isimli bir Pandas veri tablosuna (DataFrame) aktarır.
print(f"Veri seti yüklendi: {len(df)} satır, {len(df.columns)} sütun\n") # Yüklenen veri tablosunun kaç satır ve sütundan oluştuğunu ekrana yazdırır.

# VERİ TEMİZLEME
df.replace('N/A', np.nan, inplace=True) # Veri setinde metin olarak yazılmış 'N/A' (tanımsız) ifadelerini, Pandas'ın tanıyacağı gerçek boş değer (NaN) ile değiştirir.
df['Gise_Hasilati_USD'] = pd.to_numeric(df['Gise_Hasilati_USD'], errors='coerce') # Hasılat sütununu sayısal tipe çevirir, harf veya hatalı karakter içeren satırları zorunlu olarak NaN yapar.
df['Kitap_Puani_10'] = df['Kitap_Puani'] * 2 # 5'lik sistemde olan kitap puanını, 10'luk sistemdeki IMDb puanıyla kıyaslayabilmek için 2 ile çarpar.

# Metin içerisindeki süre ifadesinden (Örn: "120 min") sadece sayısal kısmı ayıklayan fonksiyon:
def sure_temizle(deger):
    if pd.isna(deger): # Eğer hücre zaten boşsa (NaN) işlem yapmadan geç.
        return np.nan
    eslesme = re.search(r'(\d+)', str(deger)) # Metin içerisindeki ilk sayısal örüntüyü (\d+) bulur.
    return int(eslesme.group(1)) if eslesme else np.nan # Sayı bulunduysa tam sayıya (int) çevirip döndürür, bulunamadıysa NaN döndürür.

# Eğer eserin tipi 'movie' ise yukarıdaki süreyi temizleme fonksiyonunu çalıştırır, 'series' ise süreye NaN yazar:
df['Film_Suresi_Dk'] = df.apply(
    lambda row: sure_temizle(row['Film_Suresi']) if row['Eser_Tipi'] == 'movie' else np.nan, axis=1
)

# Ödül metninden (Örn: "Ödül: 3 wins & 5 nominations") sadece kazanılan ödül sayısını ayıran fonksiyon:
def odul_kazan(metin):
    if pd.isna(metin): return 0 # Eğer hücre boşsa kazanılan ödül sayısı direkt 0'dır.
    eslesme = re.search(r'(\d+)\s+win', str(metin), re.IGNORECASE) # Büyük/küçük harf duyarsız olarak "win" kelimesinin solundaki sayıyı arar.
    return int(eslesme.group(1)) if eslesme else 0 # Sayı bulduysa tam sayı olarak verir, bulamadıysa 0 kabul eder.

df['Kazanilan_Odul'] = df['Film_Odulleri'].apply(odul_kazan) # 'Film_Odulleri' sütunundaki her satıra ödül bulma fonksiyonunu uygular ve yeni sütuna yazar.
df_tur = df.assign(Film_Turu=df['Film_Turu'].str.split(', ')).explode('Film_Turu') # Bir film birden fazla türe aitse virgüle göre ayırır ve her türü ayrı bir satır olarak aşağıya doğru çoğaltır.

# Veri temizleme bittikten sonra elde edilen güncel verilerin özetini ekrana yazdırır:
print("VERİ TEMİZLEME TAMAMLANDI.")
print(f"Toplam eser: {len(df)}")
print(f"Film: {(df['Eser_Tipi']=='movie').sum()} | Dizi: {(df['Eser_Tipi']=='series').sum()}")
print(f"Ortalama IMDb Puanı: {df['IMDb_Puani'].mean():.2f}")
print(f"Ortalama Kitap Puanı (10'luk): {df['Kitap_Puani_10'].mean():.2f}\n")

# GRAFİKLERİN OLUŞTURULMASI

# 1. Eser Tipi Dağılımı (Pasta Grafiği)
tip_dagilim = df['Eser_Tipi'].value_counts() # Veri setindeki 'movie' ve 'series' değerlerinin toplam sayılarını hesaplar.
fig, ax = plt.subplots(figsize=(7, 7)) # 7'ye 7 boyutlarında boş bir grafik penceresi oluşturur.
ax.pie(tip_dagilim.values, labels=['Film', 'Dizi'], autopct='%1.1f%%', 
       colors=['#4C72B0', '#DD8452'], startangle=90, textprops={'fontsize': 13}) # Dilimlerin yüzdelik oranlarını yazarak pasta grafiğini çizer.
plt.tight_layout() # Grafik ögelerinin pencere kenarlarına sıkışmasını önler.
plt.savefig('grafik_01_tip_dagilim.png', dpi=150) # Çizilen grafiği 150 DPI kalitesinde PNG resmi olarak kaydeder.
plt.close() # Hafızada gereksiz yer kaplamaması için açılan bu grafik penceresini kapatır.
print("Grafik 1 kaydedildi")

# 2. Kitap vs IMDb Puanı Karşılaştırması (Dikey Sütun Grafiği)
means = [df['Kitap_Puani_10'].mean(), df['IMDb_Puani'].mean()] # Kitapların ve filmlerin genel ortalama puanlarını hesaplayıp bir listeye alır.
fig, ax = plt.subplots(figsize=(8, 6)) # 8'e 6 boyutlarında boş bir grafik penceresi oluşturur.
bars = ax.bar(['Kitap Puanı', 'IMDb Puanı'], means, 
              color=['#4C72B0', '#DD8452'], width=0.4)# Yan yana iki adet sütun çizdirir.
for bar, val in zip(bars, means): # Döngü yardımıyla her bir sütunun koordinatlarına ulaşır.
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
            f'{val:.2f}', ha='center', fontsize=13, fontweight='bold') # Sütunların üzerine ortalama puan değerini yazar.
ax.set_ylabel('Ortalama Puan') # Y eksenine isim verir.
ax.set_ylim(0, 11) # Puanlar 10 üzerinden değerlendirildiği için Y ekseninin sınırını 0 ile 11 arası yapar.
plt.tight_layout() # Kenar boşluklarını düzenler.
plt.savefig('grafik_02_kitap_vs_imdb.png', dpi=150) # Grafiği PNG resmi olarak kaydeder.
plt.close() # Pencereyi kapatır.
print("Grafik 2 kaydedildi")

# 3. Kitap Puanı ile IMDb Puanı Korelasyonu (Saçılım ve Trend Grafiği)
df_kor = df[['Kitap_Puani_10', 'IMDb_Puani', 'Kategori']].dropna() # İlişki analizi için gerekli sütunları alır ve içinde boş (NaN) olan satırları eler.
kor = df_kor['Kitap_Puani_10'].corr(df_kor['IMDb_Puani']) # İki puan türü arasındaki ilişki derecesini (korelasyonu) hesaplar.
fig, ax = plt.subplots(figsize=(9, 6)) # 9'a 6 boyutlarında boş bir grafik penceresi oluşturur.
for kategori, renk, marker in [('Yabanci', '#4C72B0', 'o'), ('Turk', '#DD8452', '^')]: # Türk ve Yabancı eserleri döngüyle ayırır.
    alt = df_kor[df_kor['Kategori'] == kategori] # Sadece o anki döngüye ait kategorinin verilerini filtreler.
    ax.scatter(alt['Kitap_Puani_10'], alt['IMDb_Puani'], label=kategori,
               alpha=0.7, color=renk, s=70, marker=marker) # Verileri nokta grafiği olarak basar.
m, b = np.polyfit(df_kor['Kitap_Puani_10'], df_kor['IMDb_Puani'], 1) # Noktaların genel gidişatını özetleyen doğrusal fonksiyon formülünü (y = mx + b) bulur.
x_line = np.linspace(df_kor['Kitap_Puani_10'].min(), df_kor['Kitap_Puani_10'].max(), 100) # Eğilim çizgisi için X ekseni noktaları oluşturur
ax.plot(x_line, m * x_line + b, color='red', linestyle='--', linewidth=1.5, label='Trend') # Hesaplanan formüle göre kırmızı bir trend çizgisi çizer.
ax.set_xlabel('Kitap Puanı (10\'luk)') # X eksenine isim verir.
ax.set_ylabel('IMDb Puanı') # Y eksenine isim verir.
ax.text(0.05, 0.95, f'r = {kor:.2f}', transform=ax.transAxes, fontsize=12,
        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)) # Grafik içine bir kutu açarak korelasyon katsayısını (r) yazar.
ax.legend() # Kategorilerin ve trend çizgisinin ne renk olduğunu belirten göstergeyi ekler.
plt.tight_layout() # Kenar boşluklarını düzenler.
plt.savefig('grafik_03_korelasyon.png', dpi=150) # Grafiği PNG resmi olarak kaydeder.
plt.close() # Pencereyi kapatır.
print("Grafik 3 kaydedildi")

# 4. Sayfa Sayısı ile IMDb Puanı İlişkisi (Saçılım Grafiği)
df_sayfa = df[['Sayfa_Sayisi', 'IMDb_Puani']].dropna() # Sayfa sayısı ve film puanı dolu olan satırları seçer.
kor2 = df_sayfa['Sayfa_Sayisi'].corr(df_sayfa['IMDb_Puani']) # İki puan türü arasındaki ilişki derecesini (korelasyonu) hesaplar.
fig, ax = plt.subplots(figsize=(9, 6)) # 9'a 6 boyutlarında boş bir grafik penceresi oluşturur.
ax.scatter(df_sayfa['Sayfa_Sayisi'], df_sayfa['IMDb_Puani'], alpha=0.6, color='#4C72B0', s=60) # Verileri noktalar halinde grafiğe döker.
m2, b2 = np.polyfit(df_sayfa['Sayfa_Sayisi'], df_sayfa['IMDb_Puani'], 1) # Trend çizgisinin formülünü çıkarır.
x2 = np.linspace(df_sayfa['Sayfa_Sayisi'].min(), df_sayfa['Sayfa_Sayisi'].max(), 100) # Eğilim çizgisi için X ekseni noktaları oluşturur.
ax.plot(x2, m2 * x2 + b2, color='red', linestyle='--', linewidth=1.5) # Hesaplanan formüle göre kırmızı bir trend çizgisi çizer.
ax.set_xlabel('Sayfa Sayısı') # X eksenine isim verir.
ax.set_ylabel('IMDb Puanı') # Y eksenine isim verir.
ax.text(0.05, 0.95, f'r = {kor2:.2f}', transform=ax.transAxes, fontsize=12,
        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)) # İlişki katsayısını (r) grafik içine yazar.
plt.tight_layout() # Kenar boşluklarını düzenler.
plt.savefig('grafik_04_sayfa_imdb.png', dpi=150) # Grafiği PNG resmi olarak kaydeder.
plt.close() # Pencereyi kapatır.
print("Grafik 4 kaydedildi")

# 5. En Yüksek ve En Düşük Puanlı Türler
tur_puan = df_tur.groupby('Film_Turu')['IMDb_Puani'].agg(['mean', 'count']).reset_index() # Türleri gruplayıp her türün ortalama puanını ve kaç esere sahip olduğunu bulur.
tur_puan = tur_puan[tur_puan['count'] >= 5].sort_values('mean', ascending=False) # Güvenilir sonuç için en az 5 eseri olan türleri seçer ve puana göre büyükten küçüğe sıralar.
en_iyi = tur_puan.head(6) # En yüksek puana sahip ilk 6 türü alır.
en_kotu = tur_puan.tail(6) # En düşük puana sahip son 6 türü alır.
tur_secim = pd.concat([en_iyi, en_kotu]) # Bu iki grubu tek bir tabloda birleştirir.
renkler = ['#2ecc71'] * 6 + ['#e74c3c'] * 6 # En iyiler için yeşil, en kötüler için kırmızı renk tanımlar.
fig, ax = plt.subplots(figsize=(10, 8)) # 10'a 8 boyutlarında boş bir grafik penceresi oluşturur.
bars = ax.barh(tur_secim['Film_Turu'], tur_secim['mean'], color=renkler) # Seçilen türleri yatay sütun grafiği olarak çizer.
ax.axvline(tur_puan['mean'].mean(), color='gray', linestyle='--', linewidth=1.5, label='Genel Ortalama') # Tüm türlerin ortalamasını gösteren gri dikey bir çizgi çizer.
ax.set_xlabel('Ortalama IMDb Puanı') # X eksenine isim verir.
ax.set_ylabel('Tür') # Y eksenine isim verir.
ax.set_xlim(0, 10) # X eksenini 0 ile 10 puan arasında sınırlandırır.
ax.legend() # Göstergeyi ekler.
plt.tight_layout() # Kenar boşluklarını düzenler.
plt.savefig('grafik_05_tur_basari.png', dpi=150) # Grafiği PNG resmi olarak kaydeder.
plt.close() # Pencereyi kapatır.
print("Grafik 5 kaydedildi")

#  6. Yıllara Göre IMDb Puanı Trendi 
yil_puan = df.groupby('Film_Yili')['IMDb_Puani'].mean().reset_index() # Veriyi yıllara göre gruplayarak her yılın ortalama film puanını hesaplar.
fig, ax = plt.subplots(figsize=(12, 6)) # 12'ye 6 boyutlarında boş bir grafik penceresi oluşturur.
ax.plot(yil_puan['Film_Yili'], yil_puan['IMDb_Puani'], marker='o', linewidth=2,
        color='#4C72B0', markersize=5) # Yıllara göre değişimi gösteren çizgisel grafik çizer.
ax.axhline(df['IMDb_Puani'].mean(), color='red', linestyle='--', linewidth=1.5,
           label=f'Genel Ortalama ({df["IMDb_Puani"].mean():.2f})') # Tüm zamanların ortalamasını kırmızı yatay çizgiyle belirtir.
ax.set_xlabel('Yıl') # X eksenine isim verir.
ax.set_ylabel('Ortalama IMDb Puanı') # Y eksenine isim verir.
ax.legend() # Göstergeyi ekler.
plt.tight_layout() # Kenar boşluklarını düzenler.
plt.savefig('grafik_06_yil_trend.png', dpi=150) # Grafiği PNG resmi olarak kaydeder.
plt.close() # Pencereyi kapatır.
print("Grafik 6 kaydedildi")

# 7. En Çok Ödül Kazanan Türler 
tur_odul = df_tur.groupby('Film_Turu')['Kazanilan_Odul'].sum().sort_values(ascending=False).head(10) # Türlerin kazandığı toplam ödülleri hesaplar, büyükten küçüğe dizer ve ilk 10'u seçer.
fig, ax = plt.subplots(figsize=(10, 7)) # 10'a 7 boyutlarında boş bir grafik penceresi oluşturur.
sns.barplot(x=tur_odul.values, y=tur_odul.index, palette='Oranges_d', ax=ax) # Seaborn kullanarak turuncu bir yatay sütun grafiği çizer.
ax.set_xlabel('Toplam Kazanılan Ödül') # X eksenine isim verir.
ax.set_ylabel('Tür') # Y eksenine isim verir.
plt.tight_layout() # Kenar boşluklarını düzenler.
plt.savefig('grafik_07_tur_odul.png', dpi=150) # Grafiği PNG resmi olarak kaydeder.
plt.close() # Pencereyi kapatır.
print("Grafik 7 kaydedildi")

# 8. En Başarılı Yazar Uyarlamaları 
yazar_puan = df.groupby('Yazar').agg(
    IMDb_Puani_Ort=('IMDb_Puani', 'mean'),
    Eser_Sayisi=('IMDb_Puani', 'count')
).reset_index() # Yazarları gruplayıp uyarlanan eserlerinin ortalama puanını ve toplam eser sayısını hesaplar.
yazar_puan = yazar_puan[yazar_puan['Eser_Sayisi'] >= 2].sort_values('IMDb_Puani_Ort', ascending=False).head(12) # En az 2 eseri uyarlanmış yazarları seçer, puana göre sıralar ve ilk 12'yi alır.
fig, ax = plt.subplots(figsize=(10, 7)) # 10'a 7 boyutlarında boş bir grafik penceresi oluşturur.
sns.barplot(data=yazar_puan, x='IMDb_Puani_Ort', y='Yazar', palette='Blues_d', ax=ax) # Yazarların başarı grafiğini çizer.
for i, (_, row) in enumerate(yazar_puan.iterrows()): # Her bir sütun için döngü başlatır.
    ax.text(row['IMDb_Puani_Ort'] + 0.05, i, f"({int(row['Eser_Sayisi'])} eser)", va='center', fontsize=9) # Sütunların yanına o yazarın kaç eseri olduğunu yazar.
ax.set_xlabel('Ortalama IMDb Puanı') # X eksenine isim verir.
ax.set_ylabel('Yazar') # Y eksenine isim verir.
ax.set_xlim(0, 11) # X eksenini 11'e kadar sınırlar (metinlerin sığması için).
plt.tight_layout() # Kenar boşluklarını düzenler.
plt.savefig('grafik_08_yazar_basari.png', dpi=150) # Grafiği PNG resmi olarak kaydeder.
plt.close() # Pencereyi kapatır.
print("Grafik 8 kaydedildi")

# 9. En Çok Kitap Uyarlayan Yönetmenler 
yon_sayisi = df[df['Yonetmen'].notna()].groupby('Yonetmen').agg(
    Eser_Sayisi=('Eser_Adi', 'count'),
    Ort_Puan=('IMDb_Puani', 'mean')
).reset_index().sort_values('Eser_Sayisi', ascending=False).head(12) # Yönetmeni belli olan filmleri yönetmene göre gruplar, film sayılarını ve ortalama puanlarını bulup ilk 12'yi seçer.
fig, ax = plt.subplots(figsize=(10, 7)) # 10'a 7 boyutlarında boş bir grafik penceresi oluşturur.
sns.barplot(data=yon_sayisi, x='Eser_Sayisi', y='Yonetmen', palette='Purples_d', ax=ax) # Yönetmenlerin uyarlama sayılarını gösteren grafiği çizer.
for i, (_, row) in enumerate(yon_sayisi.iterrows()): # Sütunlar üzerinde döngü kurar.
    ax.text(row['Eser_Sayisi'] + 0.05, i, f"(ort. {row['Ort_Puan']:.1f})", va='center', fontsize=9) # Her yönetmenin sütununun yanına filmlerinin ortalama puanını yazar.
ax.set_xlabel('Uyarlama Sayısı') # X eksenine isim verir.
ax.set_ylabel('Yönetmen') # Y eksenine isim verir.
plt.tight_layout() # Kenar boşluklarını düzenler.
plt.savefig('grafik_09_yonetmen.png', dpi=150) # Grafiği PNG resmi olarak kaydeder.
plt.close() # Pencereyi kapatır.
print("Grafik 9 kaydedildi")

# 10. Kitap Puanlarının Gişe Hasılatına Etkisi
df_gise = df[(df['Gise_Hasilati_USD'].notna()) & (df['Gise_Hasilati_USD'] > 0)][['Kitap_Puani_10', 'Gise_Hasilati_USD', 'IMDb_Puani']].dropna() # Sadece gişe hasılatı sıfırdan büyük ve puanı olan verileri filtreler.
kor3 = df_gise['Kitap_Puani_10'].corr(df_gise['Gise_Hasilati_USD']) # Kitap puanı ile gişe hasılatı arasındaki korelasyonu (r) hesaplar.
fig, ax = plt.subplots(figsize=(9, 6)) # 9'a 6 boyutlarında boş bir grafik penceresi oluşturur.
sc = ax.scatter(df_gise['Kitap_Puani_10'], df_gise['Gise_Hasilati_USD'],
                c=df_gise['IMDb_Puani'], cmap='RdYlGn', alpha=0.7, s=80) # Kitap puanı ve gişeyi noktalarla çizer. Noktaların rengini IMDb puanına göre (kırmızıdan yeşile) ayarlar.
plt.colorbar(sc, ax=ax, label='IMDb Puanı') # Sağ tarafa renklerin hangi IMDb puanına denk geldiğini gösteren bir renk skalası çubuğu ekler.
ax.set_xlabel('Kitap Puanı (10\'luk)') # X eksenine isim verir.
ax.set_ylabel('Gişe Hasılatı (USD)') # Y eksenine isim verir.
ax.text(0.05, 0.95, f'r = {kor3:.2f}', transform=ax.transAxes, fontsize=12,
        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)) # Korelasyon değerini grafiğe ekler.
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1e6:.0f}M')) # Devasa gişe sayılarını okunabilir yapmak için Milyon Dolar ($150M gibi) formatına çevirir.
plt.tight_layout() # Kenar boşluklarını düzenler.
plt.savefig('grafik_10_kitap_gise.png', dpi=150) # Grafiği PNG resmi olarak kaydeder.
plt.close() # Pencereyi kapatır.
print("Grafik 10 kaydedildi")

# 11. Yıllara Göre Gişe Hasılatı Trendi 
df_yil_gise = df[(df['Eser_Tipi']=='movie') & (df['Gise_Hasilati_USD'] > 0)] # Sadece gişe hasılatı olan filmleri seçer.
yil_gise = df_yil_gise.groupby('Film_Yili')['Gise_Hasilati_USD'].mean().reset_index().dropna() # Yıllara göre gruplayıp yıllık ortalama hasılatı bulur.
fig, ax = plt.subplots(figsize=(12, 6)) # 12'ye 6 boyutlarında boş bir grafik penceresi oluşturur.
ax.fill_between(yil_gise['Film_Yili'], yil_gise['Gise_Hasilati_USD'], alpha=0.3, color='#4C72B0') # Çizginin altındaki alanı mavi renkle doldurur (alan grafiği).
ax.plot(yil_gise['Film_Yili'], yil_gise['Gise_Hasilati_USD'], color='#4C72B0', linewidth=2, marker='o', markersize=4) # Ana trend çizgisini çizer.
ax.set_xlabel('Yıl') # X eksenine isim verir.
ax.set_ylabel('Ortalama Gişe Hasılatı (USD)') # Y eksenine isim verir.
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1e6:.0f}M')) # Y eksenini Milyon Dolar formatına çevirir.
plt.tight_layout() # Kenar boşluklarını düzenler.
plt.savefig('grafik_11_yil_gise.png', dpi=150) # Grafiği PNG resmi olarak kaydeder.
plt.close() # Pencereyi kapatır.
print("Grafik 11 kaydedildi")

# 12. Puan Farkı Dağılımı (Kitap - IMDb) 
df_fark = df[['Kitap_Puani_10', 'IMDb_Puani']].dropna().copy() # İki puan türünün de dolu olduğu satırları kopyalar.
df_fark['Puan_Farki'] = df_fark['Kitap_Puani_10'] - df_fark['IMDb_Puani'] # Kitap puanından film puanını çıkararak aradaki farkı bulur.
fig, ax = plt.subplots(figsize=(10, 6)) # 10'a 6 boyutlarında boş bir grafik penceresi oluşturur.
ax.hist(df_fark['Puan_Farki'], bins=20, color='#4C72B0', edgecolor='white', alpha=0.8) # Farkların hangi aralıkta yoğunlaştığını gösteren bir histogram grafiği çizer.
ax.axvline(0, color='red', linestyle='--', linewidth=2, label='Eşit Puan') # Kitap ve filmin aynı puanı aldığı sıfır noktasına kırmızı bir çizgi çeker.
ax.axvline(df_fark['Puan_Farki'].mean(), color='orange', linestyle='--', linewidth=2,
           label=f"Ortalama Fark ({df_fark['Puan_Farki'].mean():.2f})") # Ortalama fark değerini turuncu bir çizgiyle gösterir.
ax.set_xlabel('Puan Farkı') # X eksenine isim verir.
ax.set_ylabel('Eser Sayısı') # Y eksenine isim verir.
ax.legend() # Göstergeyi ekler.
plt.tight_layout() # Kenar boşluklarını düzenler.
plt.savefig('grafik_12_puan_farki.png', dpi=150) # Grafiği PNG resmi olarak kaydeder.
plt.close() # Pencereyi kapatır.
print("Grafik 12 kaydedildi")

# 13. Film Süresi ile IMDb Puanı İlişkisi 
df_sure = df[(df['Eser_Tipi']=='movie') & df['Film_Suresi_Dk'].notna() & df['IMDb_Puani'].notna()] # Süresi ve IMDb puanı olan filmleri filtreler.
kor4 = df_sure['Film_Suresi_Dk'].corr(df_sure['IMDb_Puani']) # Film süresi ile aldığı puan arasındaki korelasyonu(r) hesaplar.
fig, ax = plt.subplots(figsize=(9, 6)) # 9'a 6 boyutlarında boş bir grafik penceresi oluşturur.
ax.scatter(df_sure['Film_Suresi_Dk'], df_sure['IMDb_Puani'], alpha=0.6, color='#C44E52', s=60) # Süre ve puan ilişkisini noktalarla çizer.
m4, b4 = np.polyfit(df_sure['Film_Suresi_Dk'], df_sure['IMDb_Puani'], 1) # Doğrusal trend formülünü oluşturur.
x4 = np.linspace(df_sure['Film_Suresi_Dk'].min(), df_sure['Film_Suresi_Dk'].max(), 100) # Çizgi noktalarını belirler.
ax.plot(x4, m4 * x4 + b4, color='red', linestyle='--', linewidth=1.5) # Kırmızı bir trend çizgisi çizer.
ax.set_xlabel('Film Süresi (Dakika)') # X eksenine isim verir.
ax.set_ylabel('IMDb Puanı') # Y eksenine isim verir.
ax.text(0.05, 0.95, f'r = {kor4:.2f}', transform=ax.transAxes, fontsize=12,
        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)) # Korelasyon değerini grafiğe ekler.
plt.tight_layout() # Kenar boşluklarını düzenler.
plt.savefig('grafik_13_sure_imdb.png', dpi=150) # Grafiği PNG resmi olarak kaydeder.
plt.close() # Pencereyi kapatır.
print("Grafik 13 kaydedildi")

# Öne çıkan sonuçları ekrana yazdırır.
print("\n TÜM GRAFİKLER TAMAMLANDI.")
print(f"\n Öne Çıkan Sonuçlar:")
print(f"  • Ortalama kitap puanı (10'luk): {df['Kitap_Puani_10'].mean():.2f}")
print(f"  • Ortalama IMDb puanı: {df['IMDb_Puani'].mean():.2f}")
print(f"  • Kitap-IMDb korelasyonu: {df[['Kitap_Puani_10','IMDb_Puani']].dropna().corr().iloc[0,1]:.2f}")
print(f"  • En çok kitap uyarlayan yönetmen: {df['Yonetmen'].value_counts().index[0]}")