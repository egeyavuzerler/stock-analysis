import anthropic
import pandas as pd
import time
import warnings
warnings.filterwarnings("ignore")

import os
key = os.environ.get("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=key)

def goldman_analiz(hisse, metrikler):
    prompt = f"""Hisse: {hisse}
Metrikler: {metrikler}

Asagidaki formatta yaz, her satir ayri:
OZET: [1 cumle]
BOGA_HEDEF: [sayi]
AYI_HEDEF: [sayi]
BAZ_HEDEF: [sayi]
ALIS: [sayi]
SATIS: [sayi]
RISK: [1-10]
RISK_ACIKLAMA: [1 cumle]
CIRO: [1 cumle]
PE: [1 cumle]
MOAT: [weak/moderate/strong]
MOAT_ACIKLAMA: [1 cumle]
TEMETTÜ_SKOR: [1-10]
TEMETTÜ_ACIKLAMA: [1 cumle]
TAVSIYE: [AL/SAT/TUT]
GEREKCE: [1 cumle]"""

    try:
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            timeout=60,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text
    except Exception as e:
        print(f"  API hata: {e}")
        return None


def metrikleri_hazirla(df, hisse):
    hisse_df = df[df["Hisse"] == hisse].tail(6)
    if hisse_df.empty:
        return None
    satirlar = []
    for _, row in hisse_df.iterrows():
        satir = f"{row.get('Ceyrek','')}"
        for col in ["Brut_Kar_Marji_%","ROE_%","EPS","FK_Orani","FS_Orani","Cari_Oran","NetBorc_FAVOK"]:
            if col in row and pd.notna(row[col]):
                satir += f"|{col}:{row[col]}"
        satirlar.append(satir)
    return " / ".join(satirlar)


def yaniti_parse_et(yanit, hisse, borsa):
    satirlar = yanit.strip().split("\n")
    veri = {"Hisse": hisse, "Borsa": borsa}
    for satir in satirlar:
        if ":" in satir:
            anahtar, deger = satir.split(":", 1)
            veri[anahtar.strip()] = deger.strip()
    return veri


for dosya, borsa in [("NASDAQ_FILTRELI.csv", "NASDAQ"), ("BIST_FILTRELI.csv", "BIST")]:
    print(f"\n{borsa} analiz ediliyor...")
    df = pd.read_csv(dosya)
    hisseler = df["Hisse"].unique()
    print(f"Toplam {len(hisseler)} hisse")

    sonuclar = []
    islenen = 0

    for hisse in hisseler:
        try:
            metrikler = metrikleri_hazirla(df, hisse)
            if not metrikler:
                continue

            yanit = goldman_analiz(hisse, metrikler)
            print(f"  {hisse} isleniyor...", end="", flush=True)
            print(" tamam")

            if not yanit:
                continue

            veri = yaniti_parse_et(yanit, hisse, borsa)
            sonuclar.append(veri)
            islenen += 1

            if islenen % 50 == 0:
                pd.DataFrame(sonuclar).to_csv(f"{borsa}_ANALIZ_GECICI.csv", index=False)
                print(f"  {islenen}/{len(hisseler)} tamamlandi")

            time.sleep(0.3)

        except Exception as e:
            print(f"  {hisse} hata: {e}")
            continue

    if sonuclar:
        sonuc_df = pd.DataFrame(sonuclar)
        sonuc_df.to_csv(f"{borsa}_GOLDMAN_ANALIZ.csv", index=False)
        print(f"{borsa}_GOLDMAN_ANALIZ.csv kaydedildi! ({islenen} hisse)")

print("\nTum analizler tamamlandi!")
