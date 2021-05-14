const currentVal = document.getElementById('current-percent').innerHTML;
const currentEle = document.getElementById('current');

if (currentVal < 0) {
	currentEle.classList.remove('green');
	currentEle.classList.add('red');
} else {
	currentEle.classList.remove('red');
	currentEle.classList.add('green');
}

const url = window.location.pathname;

if (url === '/') {
	const marketCap = document.getElementById('market-cap').innerHTML;
	const recentQuarter = document.getElementById('recent-quarter').innerHTML;
	const newRecentQuarter = toIntlCurrency(recentQuarter);
	const newMarketCap = toIntlCurrency(marketCap);

	document.getElementById('market-cap').innerHTML = newMarketCap;
	document.getElementById('recent-quarter').innerHTML = newRecentQuarter;

	const navItems = document.getElementsByClassName('nav-item');
	for (let item of navItems) {
		item.classList.remove('nav-item-selected');
	}

	const summaryEle = document.getElementById('summary');
	summaryEle.classList.add('nav-item-selected');
} else if (url === '/holders') {
	const navItems = document.getElementsByClassName('nav-item');
	for (let item of navItems) {
		item.classList.remove('nav-item-selected');
	}

	const holdersEle = document.getElementById('holders');
	holdersEle.classList.add('nav-item-selected');
}

if (url === '/profile') {
	const navItems = document.getElementsByClassName('nav-item');
	for (let item of navItems) {
		item.classList.remove('nav-item-selected');
	}

	const profileEle = document.getElementById('profile');
	profileEle.classList.add('nav-item-selected');
}

let marketPriceEle = document.getElementById('market-price');

function refreshTime() {
	const symbol = document.getElementById('symbol').innerHTML;

	$.ajax({
		url: '/get-quote-data?symbol=' + symbol,
		method: 'GET',
		cache: false,
	}).done(function (data) {
		let parseData = data;
		let marketPrice = parseData.regularMarketPrice;
		let percentVal = (
			(1 -
				parseData.regularMarketPreviousClose / parseData.regularMarketPrice) *
			100
		).toFixed(2);
		marketPriceEle.innerHTML = marketPrice;
		document.getElementById('current-percent').innerHTML = percentVal;
	});
}

setInterval(refreshTime, 5000);

function toIntlCurrency(labelValue) {
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

document.addEventListener('DOMContentLoaded', function () {
	if (url === '/') {
		LoadChart();
	}
});

LoadChart = function () {
	console.log('in loadchart');
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
	console.log('in renderchart');
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
