import os
from dotenv import load_dotenv
load_dotenv()  # load variables from .env

COINMARKETCAP_API_KEY = os.getenv("COINMARKETCAP_API_KEY")


from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# API to get CoinDcx BNB to INR
def get_coindcx_bnb_inr_price():
    try:
        # CoinDCX API for all ticker data
        url = 'https://api.coindcx.com/exchange/ticker'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Find BNB/INR price
        for ticker in data:
            if ticker['market'] == 'BNBINR':
                price = float(ticker['last_price'])
                print(f"CoinDCX BNB/INR Live Price: ₹{price}")
                return price

        print("BNBINR not found in CoinDCX data.")
        return 0

    except Exception as e:
        print("Error getting CoinDCX price:", e)
        return 0

# Example usage:
if __name__ == "__main__":
    get_coindcx_bnb_inr_price()

# API to get CoinGecko BNB to INR
def get_coinmarketcap_bnb_inr_price():
    try:
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": COINMARKETCAP_API_KEY
        }
        params = {
            "symbol": "BNB",
            "convert": "INR"
        }

        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        print("📦 CoinMarketCap Response:", data)

        if "data" in data and "BNB" in data["data"]:
            return round(data["data"]["BNB"]["quote"]["INR"]["price"], 2)
        else:
            print("⚠️ Unexpected API response:", data)
            return 0

    except Exception as e:
        print("❌ Error getting CoinMarketCap price:", e)
        return 0


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/tracker')
def tracker():
    coindcx = get_coindcx_bnb_inr_price()
    coingecko = get_coinmarketcap_bnb_inr_price()
    profit = coindcx - coingecko
    return render_template('tracker.html', coindcx=coindcx, coingecko=coingecko, profit=profit)

@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    investment = 1000
    try:
        coindcx = get_coindcx_bnb_inr_price()
        coingecko = get_coinmarketcap_bnb_inr_price()

        if request.method == 'POST':
            investment = float(request.form.get('investment', 1000))

        amount_bnb = investment / coingecko if coingecko else 0
        buy_fee = round(coingecko * 0.001 * amount_bnb, 2)
        sell_fee = round(coindcx * 0.002 * amount_bnb, 2)
        network_fee = 50
        total_cost = round(coingecko * amount_bnb + buy_fee + network_fee, 2)
        total_sale = round(coindcx * amount_bnb - sell_fee, 2)
        profit = round(total_sale - total_cost, 2)
    except Exception as e:
        print("Calculation error:", e)
        coindcx = coingecko = profit = amount_bnb = buy_fee = sell_fee = total_cost = total_sale = 0

    return render_template('calculator.html',
                           coindcx=coindcx, coingecko=coingecko,
                           investment=investment, amount_bnb=round(amount_bnb, 6),
                           buy_fee=buy_fee, sell_fee=sell_fee,
                           network_fee=50, total_cost=total_cost,
                           total_sale=total_sale, profit=profit)

if __name__ == '__main__':
    app.run(debug=True)
