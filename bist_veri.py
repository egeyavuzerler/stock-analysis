import yfinance as yf
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

def bist_metrikleri_hesapla(sembol):
    print(f"{sembol} isleniyor...")
    hisse = yf.Ticker(sembol)
    gelir   = hisse.quarterly_financials
    bilanco = hisse.quarterly_balance_sheet
    bilgi   = hisse.info

    if gelir.empty:
        print(f"  Veri gelmedi")
        return None

    tarihler = [t for t in gelir.columns]
    sonuclar = {}

    for tarih in tarihler:
        s = {}
        try:
            def al(tablo, satir):
                return tablo.loc[satir, tarih] if satir in tablo.index else None

            net_satis   = al(gelir,   "Total Revenue")
            brut_kar    = al(gelir,   "Gross Profit")
            faiz_gider  = al(gelir,   "Interest Expense")
            net_kar     = al(gelir,   "Net Income")
            ebitda      = al(gelir,   "EBITDA")
            opex        = al(gelir,   "Operating Expense")
            donen       = al(bilanco, "Current Assets")
            kisa_borc   = al(bilanco, "Current Liabilities")
            ozkaynak    = al(bilanco, "Stockholders Equity")
            toplam_borc = al(bilanco, "Total Debt")
            nakit       = al(bilanco, "Cash And Cash Equivalents")
            fiyat       = bilgi.get("currentPrice")
            hisse_sayisi= bilgi.get("sharesOutstanding")

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
        except Exception as e:
            print(f"  {tarih} hata: {e}")
        sonuclar[tarih] = s

    df = pd.DataFrame(sonuclar).T.sort_index()
    df.index.name = "Ceyrek"
    return df


bist_hisseler = [
    "THYAO.IS", "SISE.IS", "EREGL.IS", "ASELS.IS",
    "KCHOL.IS", "AKBNK.IS", "GARAN.IS", "YKBNK.IS",
    "BIMAS.IS", "TCELL.IS"
]

tum_sonuclar = []

for sembol in bist_hisseler:
    df = bist_metrikleri_hesapla(sembol)
    if df is not None and not df.empty:
        df["Hisse"] = sembol
        tum_sonuclar.append(df)
        df.to_csv(f"{sembol.replace('.IS','')}_metrikler.csv")
        print(f"  Kaydedildi")

if tum_sonuclar:
    birlesik = pd.concat(tum_sonuclar)
    birlesik.to_csv("BIST_HISSELER.csv")
    print(f"\nBIST_HISSELER.csv kaydedildi!")
