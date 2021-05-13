from flask import Flask, render_template, url_for, request
import yfinance as yf

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        symbol = request.form['symbol'].lower()
    else:
        symbol = 'tsla'

    data = yf.Ticker(symbol)

    return render_template('index.html', data=data)

@app.route('/history', methods=["POST", "GET"])
def history():
    #get the query string parameters
	symbol = request.args.get('symbol', default="AAPL")
	period = request.args.get('period', default="1y")
	interval = request.args.get('interval', default="1mo")

	#pull the quote
	quote = yf.Ticker(symbol)	
	#use the quote to pull the historical data from Yahoo finance
	hist = quote.history(period=period, interval=interval)
    
	#convert the historical data to JSON
	data = hist.to_json()
	#return the JSON in the HTTP response
	return data

@app.route('/holders')
def holders():
    symbol = request.args['symbol']

    data = yf.Ticker(symbol)

    return render_template('summary.html', data=data)

if __name__ == "__main__":
    app.run(debug = True)