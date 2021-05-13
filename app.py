from flask import Flask, render_template, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import yfinance as yf
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite///symbols.db'
db = SQLAlchemy(app)

class Symbols(db.model):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(5000), default=None)
    city = db.Column(db.String(50), default=None)
    state = db.Column(db.String(50), default=None)
    zip = db.Column(db.Integer, default=None)
    phone = db.Column(db.Integer, default=None)
    website = db.Column(db.String(100), default=None)
    sector = db.Column(db.String(500), default=None)
    industry = db.Column(db.String(500), default=None)
    fullTimeEmployees = db.Column(db.Integer, default=None)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        symbol = request.form['symbol'].lower()
    else:
        symbol = 'tsla'

    data = yf.Ticker(symbol)

    return render_template('index.html', data=data.info)

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

@app.route('/get-quote-data')
def getQuoteData():
    symbol = request.args['symbol']

    data = yf.Ticker(symbol)

    return (jsonify(data.info))

@app.route('/holders')
def holders():
    symbol = request.args['symbol']

    data = yf.Ticker(symbol)
    
    major_holders = data.major_holders
    major_holders.columns = ["shares", "holders"]

    majorDict = major_holders.to_dict()
    majorHolders = []

    for i in range(len(majorDict['shares'])):
        majorHolders.append({
            "share": majorDict['shares'][i],
            "holder": majorDict['holders'][i]
        })

    inst_holders = data.institutional_holders
    instDict = inst_holders.to_dict()
    instHolders = []

    for i in range(len(instDict['Holder'])):
        instHolders.append({
            "holder": instDict['Holder'][i],
            "share": '{:,}'.format(instDict['Shares'][i]),
            "date": (instDict['Date Reported'][i]).strftime('%b %d,%Y'),
            "outPercent": instDict['% Out'][i],
            "value": '{:,}'.format(instDict['Value'][i])
        })

    return render_template('holders.html', data=data.info, major=majorHolders, inst=instHolders)

@app.route('/profile')
def profile():
    symbol = request.args['symbol']

    data = yf.Ticker(symbol)

    return render_template('profile.html', data=data.info)

if __name__ == "__main__":
    app.run(debug = True)