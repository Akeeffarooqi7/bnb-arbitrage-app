from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# APIs
def get_binance_bnb_inr_price():
    url = 'https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT'
    response = requests.get(url).json()
    bnb_usdt = float(response['price'])
    usdt_inr = 83.2
    return round(bnb_usdt * usdt_inr, 2)

def get_coingecko_bnb_inr_price():
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=binancecoin&vs_currencies=inr'
    response = requests.get(url).json()
    return float(response['binancecoin']['inr'])

# 📈 LIVE PRICE TRACKER
@app.route('/tracker')
def tracker():
    try:
        binance = get_binance_bnb_inr_price()
        coingecko = get_coingecko_bnb_inr_price()
        profit = coingecko - binance
    except:
        binance = coingecko = profit = 0
    return render_template('tracker.html', binance=binance, coingecko=coingecko, profit=profit)

# 🧮 CALCULATOR
@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    investment = 1000
    try:
        binance = get_binance_bnb_inr_price()
        coingecko = get_coingecko_bnb_inr_price()
        if request.method == 'POST':
            investment = float(request.form.get('investment', 1000))

        amount_bnb = investment / binance
        binance_fee = round(binance * 0.001 * amount_bnb, 2)
        sell_fee = round(coingecko * 0.002 * amount_bnb, 2)
        network_fee = 50
        total_cost = round(binance * amount_bnb + binance_fee + network_fee, 2)
        total_sale = round(coingecko * amount_bnb - sell_fee, 2)
        profit = round(total_sale - total_cost, 2)
    except:
        binance = coingecko = profit = amount_bnb = binance_fee = sell_fee = total_cost = total_sale = 0

    return render_template('calculator.html',
                           binance=binance, coingecko=coingecko,
                           investment=investment, amount_bnb=round(amount_bnb, 6),
                           binance_fee=binance_fee, sell_fee=sell_fee,
                           network_fee=50, total_cost=total_cost,
                           total_sale=total_sale, profit=profit)


if __name__ == '__main__':
    app.run(debug=True)
