import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

def icsel_deger_hesapla(eps, buyume_orani=0.10, iskonto=0.10, yil=10):
    """DCF yöntemiyle içsel değer hesaplar"""
    if not eps or eps <= 0:
        return None
    try:
        nakit_akislari = []
        for i in range(1, yil + 1):
            nakit_akislari.append(eps * (1 + buyume_orani) ** i)
        terminal_deger = nakit_akislari[-1] * (1 + 0.03) / (iskonto - 0.03)
        toplam = sum([na / (1 + iskonto) ** (i+1) for i, na in enumerate(nakit_akislari)])
        toplam += terminal_deger / (1 + iskonto) ** yil
        return round(toplam, 2)
    except:
        return None

def filtrele_ve_puanla(df):
    """Her hisse için filtre kontrolü ve puan hesaplar"""
    
    # Son çeyrek verisini al
    son = df.iloc[-1]
    
    sonuc = {}
    puan = 0
    
    # 1. Brüt Kar Marjı > 0.40 (yüzde 40)
    bkm = son.get("Brut_Kar_Marji_%")
    if bkm is not None and not pd.isna(bkm):
        sonuc["Brut_Kar_Marji_%"] = bkm
        sonuc["BKM_Gecti"] = "EVET" if bkm > 40 else "HAYIR"
        if bkm > 40:
            puan += 1

    # 2. Faaliyet Giderleri / Brüt Kar < 0.30
    fgbk = son.get("FaalGid_BrutKar_%")
    if fgbk is not None and not pd.isna(fgbk):
        sonuc["FaalGid_BrutKar_%"] = fgbk
        sonuc["FGBK_Gecti"] = "EVET" if fgbk < 30 else "HAYIR"
        if fgbk < 30:
            puan += 1

    # 3. Finansman Giderleri / Gelir < 0.15
    fgg = son.get("FinansGid_Gelir_%")
    if fgg is not None and not pd.isna(fgg):
        sonuc["FinansGid_Gelir_%"] = fgg
        sonuc["FGG_Gecti"] = "EVET" if fgg < 15 else "HAYIR"
        if fgg < 15:
            puan += 1

    # 4. F/K Oranı < 1 (F/S için F/K kullanıyoruz)
    fk = son.get("FK_Orani")
    if fk is not None and not pd.isna(fk):
        sonuc["FK_Orani"] = fk
        sonuc["FK_Gecti"] = "EVET" if 0 < fk < 1 else "HAYIR"
        if 0 < fk < 1:
            puan += 1

    # 5. Cari Oran 1.5 ile 2 arası
    co = son.get("Cari_Oran")
    if co is not None and not pd.isna(co):
        sonuc["Cari_Oran"] = co
        sonuc["CO_Gecti"] = "EVET" if 1.5 <= co <= 2 else "HAYIR"
        if 1.5 <= co <= 2:
            puan += 1

    # 6. Net Borç / FAVÖK < 4
    nb = son.get("NetBorc_FAVOK")
    if nb is not None and not pd.isna(nb):
        sonuc["NetBorc_FAVOK"] = nb
        sonuc["NB_Gecti"] = "EVET" if nb < 4 else "HAYIR"
        if nb < 4:
            puan += 1

    # 7. ROE > 0.20 (yüzde 20)
    roe = son.get("ROE_%")
    if roe is not None and not pd.isna(roe):
        sonuc["ROE_%"] = roe
        sonuc["ROE_Gecti"] = "EVET" if roe > 20 else "HAYIR"
        if roe > 20:
            puan += 1

    # 8. EPS sürekli artıyor mu?
    eps_serisi = df["EPS"].dropna() if "EPS" in df.columns else pd.Series()
    if len(eps_serisi) >= 3:
        surekli_artis = all(eps_serisi.iloc[i] < eps_serisi.iloc[i+1] 
                           for i in range(len(eps_serisi)-1))
        sonuc["EPS_Surekli_Artis"] = "EVET" if surekli_artis else "HAYIR"
        if surekli_artis:
            puan += 1

    # 9. İçsel Değer (DCF)
    eps_son = son.get("EPS")
    if eps_son and not pd.isna(eps_son):
        icsel = icsel_deger_hesapla(eps_son * 4)  # yıllık EPS
        sonuc["Icsel_Deger"] = icsel

    sonuc["Toplam_Puan"] = puan
    sonuc["Maks_Puan"] = 8

    return sonuc


# --- ANA İŞLEM ---
print("NASDAQ verisi isleniyor...")
nasdaq_df = pd.read_csv("NASDAQ_TUM.csv", index_col=0)

print("BIST verisi isleniyor...")
bist_df = pd.read_csv("BIST_TUM.csv", index_col=0)

sonuclar = []

for kaynak, veri in [("NASDAQ", nasdaq_df), ("BIST", bist_df)]:
    print(f"\n{kaynak} filtreleniyor...")
    hisseler = veri["Hisse"].unique()
    
    for hisse in hisseler:
        try:
            hisse_df = veri[veri["Hisse"] == hisse].copy()
            hisse_df = hisse_df.drop(columns=["Hisse"])
            
            # Sayısal sütunları dönüştür
            for col in hisse_df.columns:
                hisse_df[col] = pd.to_numeric(hisse_df[col], errors="coerce")
            
            filtre = filtrele_ve_puanla(hisse_df)
            filtre["Hisse"] = hisse
            filtre["Borsa"] = kaynak
            sonuclar.append(filtre)
        except Exception as e:
            pass

# DataFrame oluştur
sonuc_df = pd.DataFrame(sonuclar)
sonuc_df = sonuc_df.sort_values("Toplam_Puan", ascending=False)

# Tüm kriterleri geçenler
tam_gecenler = sonuc_df[sonuc_df["Toplam_Puan"] == 8]
cok_iyi = sonuc_df[sonuc_df["Toplam_Puan"] >= 6]

# Kaydet
sonuc_df.to_csv("TUM_FILTRE_SONUCLARI.csv", index=False)
tam_gecenler.to_csv("TAM_GECENLER.csv", index=False)
cok_iyi.to_csv("COK_IYI_HISSELER.csv", index=False)

print(f"\nToplam işlenen hisse: {len(sonuclar)}")
print(f"Tüm kriterleri geçen (8/8): {len(tam_gecenler)} hisse")
print(f"6+ kriter geçen: {len(cok_iyi)} hisse")
print(f"\nEn iyi 20 hisse:")
print(sonuc_df[["Hisse", "Borsa", "Toplam_Puan"]].head(20).to_string())
print(f"\nDosyalar kaydedildi!")
