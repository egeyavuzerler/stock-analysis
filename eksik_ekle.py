import requests
import pandas as pd
import time
import warnings
warnings.filterwarnings("ignore")

API_KEY = "NZRq9Sm9k4udODzLEb2YoGsxO5BvdVLV"
BASE = "https://financialmodelingprep.com/stable"

def eps_ve_fs_cek(sembol):
    gelir = requests.get(f"{BASE}/income-statement?symbol={sembol}&period=quarter&limit=25&apikey={API_KEY}").json()
    profil = requests.get(f"{BASE}/profile?symbol={sembol}&apikey={API_KEY}").json()
    
    if not isinstance(gelir, list) or not gelir:
        return None
    
    fiyat = profil[0].get("price") if isinstance(profil, list) and profil else None
    market_cap = profil[0].get("marketCap") if isinstance(profil, list) and profil else None
    
    sonuclar = {}
    for g in gelir:
        tarih = g.get("date", "")
        if tarih[:4] < "2020":
            continue
        
        eps = g.get("eps")
        revenue = g.get("revenue")
        shares = g.get("weightedAverageShsOut")
        
        s = {}
        if eps is not None:
            s["EPS"] = round(eps, 4)
        
        # F/K = fiyat / (eps * 4)
        if fiyat and eps and eps != 0:
            s["FK_Orani"] = round(fiyat / (eps * 4), 2)
        
        # F/S = market cap / (revenue * 4)
        if market_cap and revenue and revenue != 0:
            s["FS_Orani"] = round(market_cap / (revenue * 4), 2)
        
        sonuclar[tarih] = s
    
    if not sonuclar:
        return None
    
    df = pd.DataFrame(sonuclar).T.sort_index()
    df.index.name = "Ceyrek"
    return df


# Mevcut NASDAQ verisini oku
print("Mevcut NASDAQ verisi okunuyor...")
mevcut = pd.read_csv("NASDAQ_TUM.csv", index_col=0)
hisseler = mevcut["Hisse"].unique()
print(f"Toplam {len(hisseler)} hisse için EPS ve F/S eklenecek")

tum_yeni = []
islenen = 0

for sembol in hisseler:
    try:
        yeni = eps_ve_fs_cek(sembol)
        if yeni is not None:
            yeni["Hisse"] = sembol
            tum_yeni.append(yeni)
        islenen += 1
        
        if islenen % 100 == 0:
            print(f"  {islenen}/{len(hisseler)} islendi")
        
        time.sleep(0.3)
    except Exception as e:
        pass

# Yeni veriyi birleştir
print("\nBirlestiriliyor...")
yeni_df = pd.concat(tum_yeni)
yeni_df = yeni_df.reset_index()
yeni_df.columns = ["Ceyrek", "EPS", "FK_Orani", "FS_Orani", "Hisse"]

# Mevcut veri ile merge et
mevcut = mevcut.reset_index()
birlesik = mevcut.merge(yeni_df, on=["Ceyrek", "Hisse"], how="left")
birlesik.to_csv("NASDAQ_TUM.csv", index=False)
print("NASDAQ_TUM.csv guncellendi!")
print(f"Kolonlar: {birlesik.columns.tolist()}")
