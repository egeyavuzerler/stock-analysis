from metrikler import metrikleri_hesapla
import pandas as pd
import time

# İstediğin hisseleri buraya ekle
# NASDAQ hisseleri normal yaz, BIST hisselerinin sonuna .IS ekle
hisseler = [
    "AAPL",     # Apple
    "MSFT",     # Microsoft
    "GOOGL",    # Google
    "THYAO.IS", # Türk Hava Yolları
    "SISE.IS",  # Şişecam
    "EREGL.IS", # Ereğli Demir
]

tum_sonuclar = []

for sembol in hisseler:
    try:
        df = metrikleri_hesapla(sembol)
        df["Hisse"] = sembol
        tum_sonuclar.append(df)
        df.to_csv(f"{sembol.replace('.IS','')}_metrikler.csv")
        print(f"✓ {sembol} tamamlandi")
        time.sleep(2)  # Yahoo Finance'i yormamak için bekle
    except Exception as e:
        print(f"✗ {sembol} hata: {e}")

# Hepsini tek CSV'ye birleştir
if tum_sonuclar:
    birlesik = pd.concat(tum_sonuclar)
    birlesik.to_csv("TUM_HISSELER.csv")
    print("\nTUM_HISSELER.csv kaydedildi!")
