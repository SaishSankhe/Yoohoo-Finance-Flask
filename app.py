from flask import Flask, render_template, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import yfinance as yf
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///symbols.db'
db = SQLAlchemy(app)

class Symbols(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100), default=None)
    city = db.Column(db.String(50), default=None)
    state = db.Column(db.String(50), default=None)
    zip = db.Column(db.Integer, default=None)
    phone = db.Column(db.Integer, default=None)
    website = db.Column(db.String(100), default=None)
    sector = db.Column(db.String(500), default=None)
    industry = db.Column(db.String(500), default=None)
    fullTimeEmployees = db.Column(db.Integer, default=None)
    description = db.Column(db.String(5000), default=None)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        symbol = request.form['symbol'].lower()
    else:
        if request.args:
            symbol = request.args['symbol'] if request.args['symbol'] else 'tsla'    
        else:
            symbol = 'tsla'

    data = yf.Ticker(symbol)
    
    if len(data.info) <= 1:
        return render_template('index.html', error="No such symbol. Try again.")
    else:
        error = addToDb(symbol, data)

        return render_template('index.html', data=data.info)

@app.route('/history', methods=["POST", "GET"])
def history():
    #get the query string parameters
	symbol = request.args.get('symbol', default="AAPL")
	period = '2y'
	interval = '1mo'

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
    if '%' in major_holders[0][0]:
        major_holders.columns = ["shares", "holders"]

        majorDict = major_holders.to_dict()
        majorHolders = []

        for i in range(len(majorDict['shares'])):
            majorHolders.append({
                "share": majorDict['shares'][i],
                "holder": majorDict['holders'][i]
            })
    else:
        majorHolders = False

    inst_holders = data.institutional_holders
    if 'Holder' in inst_holders.columns:
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
    else:
        instHolders = False

    return render_template('holders.html', data=data.info, major=majorHolders, inst=instHolders)

@app.route('/profile')
def profile():
    symbol = request.args['symbol']

    data = yf.Ticker(symbol)
    dbData = Symbols.query.get(symbol)

    return render_template('profile.html', data=data.info, info=dbData)

def addToDb (symbol, data):
    error = False

    # try:
    #     toDel = Symbols.query.get(symbol)
    #     db.session.delete(toDel)
    #     db.session.commit()
    # except:
    #     error=True

    if(db.session.query(db.exists().where(Symbols.id == symbol)).scalar() != True):
        id = symbol
        name = data.info['shortName']
        address = data.info['address1'] if 'address' in data.info else None
        city = data.info['city'] if 'city' in data.info else None
        state = data.info['state'] if 'state' in data.info else None
        zip = data.info['zip'] if 'zip' in data.info else None
        phone = data.info['phone'] if 'phone' in data.info else None
        website = data.info['website'] if 'website' in data.info else None
        sector = data.info['sector'] if 'sector' in data.info else None
        industry = data.info['industry'] if 'industry' in data.info else None
        fullTimeEmployees = data.info['fullTimeEmployees'] if 'fullTimeEmployees' in data.info else None
        description = data.info['longBusinessSummary'] if 'longBusinessSummary' in data.info else None

        new_symbol = Symbols(id = id, name = name, address = address, city = city, 
                            state = state, zip = zip, phone = phone, website = website, 
                            sector = sector, industry = industry, 
                            fullTimeEmployees = fullTimeEmployees, description = description)
        
        try:
            db.session.add(new_symbol)
            db.session.commit()
        except:
            error = True
    
    return error

if __name__ == "__main__":
    app.run(debug = True)