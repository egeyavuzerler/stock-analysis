import requests
import pandas as pd
import time
import warnings
warnings.filterwarnings("ignore")

import os
API_KEY = os.environ.get("FMP_API_KEY")
BASE = "https://financialmodelingprep.com/stable"

# Adım 1: Tüm NASDAQ hisselerini çek
print("NASDAQ hisse listesi çekiliyor...")
r = requests.get(
    "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=10000&exchange=nasdaq",
    headers={"User-Agent": "Mozilla/5.0"}
).json()

tum_hisseler = [x["symbol"] for x in r["data"]["table"]["rows"]]
print(f"Toplam {len(tum_hisseler)} hisse bulundu")

# Adım 2: Her hisse için metrikleri hesapla
def fmp_metrikleri_hesapla(sembol):
    gelir_data   = requests.get(f"{BASE}/income-statement?symbol={sembol}&period=quarter&limit=25&apikey={API_KEY}").json()
    bilanco_data = requests.get(f"{BASE}/balance-sheet-statement?symbol={sembol}&period=quarter&limit=25&apikey={API_KEY}").json()
    fiyat_data   = requests.get(f"{BASE}/quote?symbol={sembol}&apikey={API_KEY}").json()

    if not isinstance(gelir_data, list) or len(gelir_data) == 0:
        return None

    fiyat        = fiyat_data[0].get("price") if isinstance(fiyat_data, list) and fiyat_data else None
    hisse_sayisi = fiyat_data[0].get("sharesOutstanding") if isinstance(fiyat_data, list) and fiyat_data else None

    sonuclar = {}
    for g in gelir_data:
        tarih = g.get("date", "")
        if tarih[:4] < "2020":
            continue
        b = next((x for x in bilanco_data if x["date"] == tarih), None)
        if not b:
            continue
        s = {}
        try:
            net_satis   = g.get("revenue") or 0
            brut_kar    = g.get("grossProfit") or 0
            faiz_gider  = g.get("interestExpense") or 0
            net_kar     = g.get("netIncome") or 0
            ebitda      = g.get("ebitda") or 0
            opex        = g.get("operatingExpenses") or 0
            donen       = b.get("totalCurrentAssets") or 0
            kisa_borc   = b.get("totalCurrentLiabilities") or 0
            ozkaynak    = b.get("totalStockholdersEquity") or 0
            toplam_borc = b.get("totalDebt") or 0
            nakit       = b.get("cashAndCashEquivalents") or 0

            if brut_kar and net_satis:
                s["Brut_Kar_Marji_%"] = round((brut_kar / net_satis) * 100, 2)
            if opex and brut_kar:
                s["FaalGid_BrutKar_%"] = round((abs(opex) / brut_kar) * 100, 2)
            if faiz_gider and net_satis:
                s["FinansGid_Gelir_%"] = round((abs(faiz_gider) / net_satis) * 100, 2)
            if donen and kisa_borc:
                s["Cari_Oran"] = round(donen / kisa_borc, 2)
            if toplam_borc and ebitda:
                s["NetBorc_FAVOK"] = round((toplam_borc - nakit) / (ebitda * 4), 2)
            if net_kar and ozkaynak:
                s["ROE_%"] = round((net_kar / ozkaynak) * 100, 2)
            if net_kar and hisse_sayisi and hisse_sayisi != 0:
                eps = net_kar / hisse_sayisi
                s["EPS"] = round(eps, 4)
                if fiyat and eps != 0:
                    s["FK_Orani"] = round(fiyat / (eps * 4), 2)
        except:
            pass
        sonuclar[tarih] = s

    if not sonuclar:
        return None
    df = pd.DataFrame(sonuclar).T.sort_index()
    df.index.name = "Ceyrek"
    return df


# Adım 3: Toplu işle ve kaydet
tum_sonuclar = []
basarisiz = []
islenen = 0

for sembol in tum_hisseler:
    try:
        df = fmp_metrikleri_hesapla(sembol)
        if df is not None and not df.empty:
            df["Hisse"] = sembol
            tum_sonuclar.append(df)
            islenen += 1

            # Her 50 hissede bir ara kaydet
            if islenen % 50 == 0:
                gecici = pd.concat(tum_sonuclar)
                gecici.to_csv("NASDAQ_GECICI.csv")
                print(f"  {islenen}/{len(tum_hisseler)} islendi, ara kayıt yapıldı")

        time.sleep(0.5)

    except Exception as e:
        basarisiz.append(sembol)

# Final kayıt
if tum_sonuclar:
    birlesik = pd.concat(tum_sonuclar)
    birlesik.to_csv("NASDAQ_TUM.csv")
    print(f"\nNASDAQ_TUM.csv kaydedildi!")
    print(f"Toplam {islenen} hisse islendi")
    print(f"Basarisiz: {len(basarisiz)} hisse")
