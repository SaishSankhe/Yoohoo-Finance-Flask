const currentVal = document.getElementById('current-percent').innerHTML;
const currentEle = document.getElementById('current');

// check the value of current percent
// set green if above 0 and red if in negative
if (currentVal < 0) {
	currentEle.classList.remove('green');
	currentEle.classList.add('red');
} else {
	currentEle.classList.remove('red');
	currentEle.classList.add('green');
}

// get the url pathname to highlight the navigation item
const url = window.location.pathname;

if (url === '/') {
	// get the big numbers and convert them to K, M, B or T
	const marketCap = document.getElementById('market-cap').innerHTML;
	const recentQuarter = document.getElementById('recent-quarter').innerHTML;
	const newRecentQuarter = toIntlCurrency(recentQuarter);
	const newMarketCap = toIntlCurrency(marketCap);

	// set the new numbers
	document.getElementById('market-cap').innerHTML = newMarketCap;
	document.getElementById('recent-quarter').innerHTML = newRecentQuarter;

	// remove selected class attribute from all nav-items
	const navItems = document.getElementsByClassName('nav-item');
	for (let item of navItems) {
		item.classList.remove('nav-item-selected');
	}

	// add selected class to summary nav-item
	const summaryEle = document.getElementById('summary');
	summaryEle.classList.add('nav-item-selected');
} else if (url === '/holders') {
	// remove selected class attribute from all nav-items
	const navItems = document.getElementsByClassName('nav-item');
	for (let item of navItems) {
		item.classList.remove('nav-item-selected');
	}

	// add selected class to holders nav-item
	const holdersEle = document.getElementById('holders');
	holdersEle.classList.add('nav-item-selected');
}

if (url === '/profile') {
	// remove selected class attribute from all nav-items
	const navItems = document.getElementsByClassName('nav-item');
	for (let item of navItems) {
		item.classList.remove('nav-item-selected');
	}

	// add selected class to profile nav-item
	const profileEle = document.getElementById('profile');
	profileEle.classList.add('nav-item-selected');
}

// get the current market price to calculate new price and set the innerHtml
let marketPriceEle = document.getElementById('market-price');

function refreshTime() {
	// this function is to get the latest data from yfinance
	// and set the new values to webpage
	// this ensures that the user gets the latest price, without refreshing
	const symbol = document.getElementById('symbol').innerHTML;

	// get the data from backend by passing the symbol
	$.ajax({
		url: '/get-quote-data?symbol=' + symbol,
		method: 'GET',
		cache: false,
	}).done(function (data) {
		let parseData = data;
		let marketPrice = parseData.regularMarketPrice;
		// calculate the percentage
		let percentVal = (
			(1 -
				parseData.regularMarketPreviousClose / parseData.regularMarketPrice) *
			100
		).toFixed(2);

		// set the values to webpage
		marketPriceEle.innerHTML = marketPrice;
		document.getElementById('current-percent').innerHTML = percentVal;
	});
}

// update the values every 5 seconds
// can change this value, I have kept it 5 sec, not to overload the api and backend
setInterval(refreshTime, 5000);

function toIntlCurrency(labelValue) {
	// This function converts the big numbers and returns its respective number
	// in K, M, B or T

	// Twelve Zeroes for Trillions
	return Math.abs(Number(labelValue)) >= 1.0e12
		? (Math.abs(Number(labelValue)) / 1.0e12).toFixed(3) + 'T'
		: // Nine Zeroes for Billions
		Math.abs(Number(labelValue)) >= 1.0e9
		? (Math.abs(Number(labelValue)) / 1.0e9).toFixed(3) + 'B'
		: // Six Zeroes for Millions
		Math.abs(Number(labelValue)) >= 1.0e6
		? (Math.abs(Number(labelValue)) / 1.0e6).toFixed(3) + 'M'
		: // Three Zeroes for Thousands
		Math.abs(Number(labelValue)) >= 1.0e3
		? (Math.abs(Number(labelValue)) / 1.0e3).toFixed(3) + 'K'
		: Math.abs(Number(labelValue));
}

// to load chart every time the content is loaded and only when url is '/'
document.addEventListener('DOMContentLoaded', function () {
	if (url === '/') {
		LoadChart();
	}
});

LoadChart = function () {
	// this function gets the data from backend and passes to RenderChart function to render
	// the chart

	const symbol = document.getElementById('symbol').innerHTML;

	$.ajax({
		url: '/history?symbol=' + symbol,
		method: 'GET',
		cache: false,
	}).done(function (data) {
		RenderChart(JSON.parse(data), symbol);
	});
};

RenderChart = function (data, symbol) {
	// this function renders the chart using Charts.js and data passed

	let priceData = [];
	let dates = [];

	for (let i in data.Close) {
		let dt = i.slice(0, i.length - 3);
		let dateString = moment.unix(dt).format('MM/YY');
		let close = data.Close[i];
		if (close != null) {
			priceData.push(data.Close[i].toFixed(2));
			dates.push(dateString);
		}
	}

	// to change the color of graph depending of value, green if positive, red if negative
	let color = '#00873C';
	if (currentVal > 0) {
		color = '#00873C';
	} else {
		color = '#EB0F29';
	}

	new Chart(document.getElementById('myChart'), {
		type: 'line',
		data: {
			labels: dates,
			datasets: [
				{
					label: symbol,
					data: priceData,
					fill: true,
					borderColor: color,
					backgroundColor: color,
					tension: 0,
				},
			],
			options: {
				interaction: {
					intersect: false,
					mode: 'index',
				},
			},
		},
	});
};
