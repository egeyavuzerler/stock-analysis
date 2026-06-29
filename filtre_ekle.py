import pandas as pd
import warnings
warnings.filterwarnings("ignore")

def icsel_deger_hesapla(eps_yillik, buyume=0.10, iskonto=0.10, yil=10):
    if not eps_yillik or eps_yillik <= 0:
        return None
    try:
        akislar = [eps_yillik * (1 + buyume) ** i for i in range(1, yil+1)]
        terminal = akislar[-1] * 1.03 / (iskonto - 0.03)
        deger = sum([a / (1+iskonto)**i for i, a in enumerate(akislar, 1)])
        deger += terminal / (1+iskonto)**yil
        return round(deger, 2)
    except:
        return None

def filtre_ekle(dosya_adi, cikti_adi, borsa):
    print(f"\n{borsa} isleniyor...")
    df = pd.read_csv(dosya_adi)

    for col in df.columns:
        if col != "Hisse":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["BKM_Filtre"]  = df["Brut_Kar_Marji_%"].apply(lambda x: "GECTI" if pd.notna(x) and x > 40 else "GECMEDI")
    df["FGBK_Filtre"] = df["FaalGid_BrutKar_%"].apply(lambda x: "GECTI" if pd.notna(x) and x < 30 else "GECMEDI")
    df["FGG_Filtre"]  = df["FinansGid_Gelir_%"].apply(lambda x: "GECTI" if pd.notna(x) and x < 15 else "GECMEDI")
    df["FK_Filtre"]   = df["FK_Orani"].apply(lambda x: "GECTI" if pd.notna(x) and 0 < x < 15 else "GECMEDI") if "FK_Orani" in df.columns else "VERI_YOK"
    df["FS_Filtre"]   = df["FS_Orani"].apply(lambda x: "GECTI" if pd.notna(x) and 0 < x < 1 else "GECMEDI") if "FS_Orani" in df.columns else "VERI_YOK"
    df["CO_Filtre"]   = df["Cari_Oran"].apply(lambda x: "GECTI" if pd.notna(x) and 1.5 <= x <= 2 else "GECMEDI")
    df["NB_Filtre"]   = df["NetBorc_FAVOK"].apply(lambda x: "GECTI" if pd.notna(x) and x < 4 else "GECMEDI")
    df["ROE_Filtre"]  = df["ROE_%"].apply(lambda x: "GECTI" if pd.notna(x) and x > 20 else "GECMEDI")

    eps_artis = {}
    for hisse in df["Hisse"].unique():
        try:
            seri = df[df["Hisse"] == hisse]["EPS"].dropna()
            if len(seri) >= 3:
                artis = all(seri.iloc[i] < seri.iloc[i+1] for i in range(len(seri)-1))
                eps_artis[hisse] = "GECTI" if artis else "GECMEDI"
            else:
                eps_artis[hisse] = "VERI_YOK"
        except:
            eps_artis[hisse] = "VERI_YOK"
    df["EPS_Artis_Filtre"] = df["Hisse"].map(eps_artis)

    df["Icsel_Deger"] = df["EPS"].apply(
        lambda x: icsel_deger_hesapla(x * 4) if pd.notna(x) else None
    ) if "EPS" in df.columns else None

    filtreler = ["BKM_Filtre","FGBK_Filtre","FGG_Filtre","FK_Filtre",
                 "FS_Filtre","CO_Filtre","NB_Filtre","ROE_Filtre","EPS_Artis_Filtre"]
    gercek_filtreler = [f for f in filtreler if f in df.columns]
    df["Toplam_Gecilen"] = df[gercek_filtreler].apply(
        lambda row: sum(1 for v in row if v == "GECTI"), axis=1
    )

    df.to_csv(cikti_adi, index=False)
    print(f"Kaydedildi: {cikti_adi}")
    print(f"Toplam satir: {len(df)}")

filtre_ekle("NASDAQ_TUM.csv", "NASDAQ_FILTRELI.csv", "NASDAQ")
filtre_ekle("BIST_TUM.csv",   "BIST_FILTRELI.csv",   "BIST")

print("\nTamamlandi!")

