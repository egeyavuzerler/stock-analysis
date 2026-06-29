import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

ticker_sembol = "AAPL"
print(f"{ticker_sembol} verisi çekiliyor...")

hisse = yf.Ticker(ticker_sembol)
gelir = hisse.quarterly_financials
bilanco = hisse.quarterly_balance_sheet

print("\n--- GELİR TABLOSU SATIRLARI ---")
print(gelir.index.tolist())

print("\n--- BİLANÇO SATIRLARI ---")
print(bilanco.index.tolist())

print("\nBasarili!")
