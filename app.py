from flask import Flask, render_template, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import yfinance as yf

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///symbols.db'
db = SQLAlchemy(app)
server = app.server

# define our database model
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
    """ This function is for index route ('/').
        It fetches data from yfinance module for POSTed symbol or 'aapl' by default.
        It then sends the data to 'index.html' template which renders the data and chart.

    Returns:
        jinja template
    """

    # check if the method is POST, i.e. is something is sent from form
    if request.method == "POST":
        symbol = request.form['symbol'].lower()
    else:
        # this is to check if any symbol is passed as url parameters
        if request.args:
            symbol = request.args['symbol'] if request.args['symbol'] else 'aapl'    
        else:
            symbol = 'aapl'

    # get the data from yfinance module
    data = yf.Ticker(symbol)
    
    # if there's no data available for any symbol, it means that there's no such symbol
    if len(data.info) <= 1:
        # render the error message
        return render_template('index.html', error="No such symbol. Try again.")
    else:
        '''
        # add the static data to SQL database and get if there are any errors in adding it
        # this data will be used for '/profile
        # '''
        error = addToDb(symbol, data)

        # render the index page and pass the data.info got from the yfinance module
        return render_template('index.html', data=data.info)

@app.route('/history', methods=["POST", "GET"])
def history():
    """ This function is for getting the historical data from yfinace module for any symbol
        that is passed as a url parameter and then returning the data to javascript file
        to use this data for creating a chart

    Returns:
        JSON
    """

    # get the symbol from query string parameters
    symbol = request.args.get('symbol', default="AAPL")
    period = '2y' # set default period
    interval = '1mo' # set default interval

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
    """ This function is to get the latest updated quote (every 5 seconds) data from yfinance,
        return the JSON to javascript, where current market price and difference percent
        is calculate and updated on the webpage using innerHtml

    Returns:
        JSON
    """

    # get the symbol from url parameter
    symbol = request.args['symbol']

    data = yf.Ticker(symbol)

    # return JSON data
    return (jsonify(data.info))

@app.route('/holders')
def holders():
    """ This function is get the holders data from module and pass it to 'holders.html'
        It also checks if any symbol has holders data or not.
        If not, returns False, so that the specific block is not displayed on webpage.

    Returns:
        jinja template
    """
    symbol = request.args['symbol']

    data = yf.Ticker(symbol)
    
    # get major holders from data
    major_holders = data.major_holders

    '''
    # this is to check if it really contains holder data or some other data
    # after assessing the data for symbols which do not have holders data stored,
    # this returned a different data like 52DayAvg, etc. Therefore, if we check if there
    # is a '%' in [0][0] index, we may know if it is holders data or not'''
    if '%' in major_holders[0][0]:
        major_holders.columns = ["shares", "holders"]

        # convert it to a dict
        majorDict = major_holders.to_dict()
        majorHolders = []

        # put the data from dict to an array of dicts
        # this is to properly pass the data to the template as to read it properly
        for i in range(len(majorDict['shares'])):
            majorHolders.append({
                "share": majorDict['shares'][i],
                "holder": majorDict['holders'][i]
            })
    else:
        # set false to not load the block
        majorHolders = False

    inst_holders = data.institutional_holders

    '''
    # this is to check if it really contains holder data or some other data
    # after assessing the data for symbols which do not have holders data stored,
    # this returned data like DailyAvg, etc. Therefore, if we check if the column names
    # has "Holder" in it, we can be sure if it is holders data'''
    if 'Holder' in inst_holders.columns:
        instDict = inst_holders.to_dict()
        instHolders = []

        # put the data from dict to an array of dicts
        # this is to properly pass the data to the template as to read it properly
        for i in range(len(instDict['Holder'])):
            instHolders.append({
                "holder": instDict['Holder'][i],
                "share": '{:,}'.format(instDict['Shares'][i]),
                "date": (instDict['Date Reported'][i]).strftime('%b %d,%Y'),
                "outPercent": instDict['% Out'][i],
                "value": '{:,}'.format(instDict['Value'][i])
            })
    else:
        # set false to not load the block
        instHolders = False

    # pass the data and render the template
    return render_template('holders.html', data=data.info, major=majorHolders, inst=instHolders)

@app.route('/profile')
def profile():
    """ This function is used to get the data from SQL database and pass it to template

    Returns:
        jinja template
    """
    symbol = request.args['symbol']

    data = yf.Ticker(symbol)

    # get the data from the database
    dbData = Symbols.query.get(symbol)

    return render_template('profile.html', data=data.info, info=dbData)

def addToDb (symbol, data):
    """ This is a helper function to load the data to database

    Args:
        symbol (string)
        data (dict)

    Returns:
        bool: if there was any error while loading the data or not
    """
    error = False

    # try:
    #     toDel = Symbols.query.get(symbol)
    #     db.session.delete(toDel)
    #     db.session.commit()
    # except:
    #     error=True

    # check if there already exists any row with same symbol
    # if not, create one
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