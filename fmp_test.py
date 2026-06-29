import requests
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

API_KEY = "NZRq9Sm9k4udODzLEb2YoGsxO5BvdVLV"

def fmp_metrikleri_hesapla(sembol):
    print(f"{sembol} isleniyor...")
    base = "https://financialmodelingprep.com/api/v4"
    
    gelir_data = requests.get(f"https://financialmodelingprep.com/stable/income-statement?symbol={sembol}&period=quarter&limit=25&apikey={API_KEY}").json()
    bilanco_data = requests.get(f"https://financialmodelingprep.com/stable/balance-sheet-statement?symbol={sembol}&period=quarter&limit=25&apikey={API_KEY}").json()
    fiyat_data = requests.get(f"https://financialmodelingprep.com/stable/quote?symbol={sembol}&apikey={API_KEY}").json()

    print(f"Gelen veri tipi: {type(gelir_data)}")
    print(f"Ilk 200 karakter: {str(gelir_data)[:200]}")

fmp_metrikleri_hesapla("AAPL")
