import os
from dotenv import load_dotenv
load_dotenv()

load_dotenv()  # load variables from .env
COINMARKETCAP_API_KEY = os.getenv("COINMARKETCAP_API_KEY")


from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# API to get Binance BNB to INR
def get_binance_bnb_inr_price():
    try:
        url = 'https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        bnb_usdt = float(response.json()['price'])
        usdt_inr = 83.2  # Fixed conversion
        price = round(bnb_usdt * usdt_inr, 2)
        print("Binance Price:", price)
        return price
    except Exception as e:
        print("Error getting Binance price:", e)
        return 0

# API to get CoinGecko BNB to INR
def get_coinmarketcap_bnb_inr_price():
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": "YOUR_API_KEY_HERE"
    }
    params = {
        "symbol": "BNB",
        "convert": "INR"
    }

   response = requests.get(API_URL)
if response.status_code == 200:
    json_data = response.json()
    if 'data' in json_data:
        data = json_data['data']
        # process data
    else:
        print("⚠️ 'data' key not found in response")
else:
    print("❌ API call failed with:", response.status_code)
    return round(data['data']['BNB']['quote']['INR']['price'], 2)



@app.route('/tracker')
def tracker():
    binance = get_binance_bnb_inr_price()
    coingecko = get_coinmarketcap_bnb_inr_price()
    profit = coingecko - binance
    return render_template('tracker.html', binance=binance, coingecko=coingecko, profit=profit)

@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    investment = 1000
    try:
        binance = get_binance_bnb_inr_price()
        coingecko = get_coinmarketcap_bnb_inr_price()

        if request.method == 'POST':
            investment = float(request.form.get('investment', 1000))

        amount_bnb = investment / binance if binance else 0
        binance_fee = round(binance * 0.001 * amount_bnb, 2)
        sell_fee = round(coingecko * 0.002 * amount_bnb, 2)
        network_fee = 50
        total_cost = round(binance * amount_bnb + binance_fee + network_fee, 2)
        total_sale = round(coingecko * amount_bnb - sell_fee, 2)
        profit = round(total_sale - total_cost, 2)
    except Exception as e:
        print("Calculation error:", e)
        binance = coingecko = profit = amount_bnb = binance_fee = sell_fee = total_cost = total_sale = 0

    return render_template('calculator.html',
                           binance=binance, coingecko=coingecko,
                           investment=investment, amount_bnb=round(amount_bnb, 6),
                           binance_fee=binance_fee, sell_fee=sell_fee,
                           network_fee=50, total_cost=total_cost,
                           total_sale=total_sale, profit=profit)

if __name__ == '__main__':
    app.run(debug=True)
