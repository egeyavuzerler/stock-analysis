import yfinance as yf
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

def metrikleri_hesapla(sembol):
    print(f"\n{sembol} isleniyor...")
    hisse = yf.Ticker(sembol)
    
    gelir   = hisse.quarterly_financials
    bilanco = hisse.quarterly_balance_sheet
    bilgi   = hisse.info

    tarihler = [t for t in gelir.columns if t.year >= 2020]
    sonuclar = {}

    for tarih in tarihler:
        s = {}
        try:
            def al(tablo, satir):
                return tablo.loc[satir, tarih] if satir in tablo.index else None

            net_satis      = al(gelir,   "Total Revenue")
            brut_kar       = al(gelir,   "Gross Profit")
            faiz_gider     = al(gelir,   "Interest Expense")
            net_kar        = al(gelir,   "Net Income")
            ebitda         = al(gelir,   "EBITDA")
            opex           = al(gelir,   "Operating Expense")
            donen          = al(bilanco, "Current Assets")
            kisa_borc      = al(bilanco, "Current Liabilities")
            ozkaynak       = al(bilanco, "Stockholders Equity")
            toplam_borc    = al(bilanco, "Total Debt")
            nakit          = al(bilanco, "Cash And Cash Equivalents")

            if brut_kar and net_satis and net_satis != 0:
                s["Brut_Kar_Marji_%"] = round((brut_kar / net_satis) * 100, 2)

            if opex and brut_kar and brut_kar != 0:
                s["FaalGid_BrutKar_%"] = round((abs(opex) / brut_kar) * 100, 2)

            if faiz_gider and net_satis and net_satis != 0:
                s["FinansGid_Gelir_%"] = round((abs(faiz_gider) / net_satis) * 100, 2)

            if donen and kisa_borc and kisa_borc != 0:
                s["Cari_Oran"] = round(donen / kisa_borc, 2)

            if toplam_borc and nakit and ebitda and ebitda != 0:
                s["NetBorc_FAVOK"] = round((toplam_borc - nakit) / (ebitda * 4), 2)

            if net_kar and ozkaynak and ozkaynak != 0:
                s["ROE_%"] = round((net_kar / ozkaynak) * 100, 2)

            hisse_sayisi = bilgi.get("sharesOutstanding")
            fiyat        = bilgi.get("currentPrice")

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

if __name__ == "__main__":
    sembol = "AAPL"
    df = metrikleri_hesapla(sembol)
    print(df.to_string())
    df.to_csv(f"{sembol}_metrikler.csv")
    print(f"\nKaydedildi: {sembol}_metrikler.csv")
