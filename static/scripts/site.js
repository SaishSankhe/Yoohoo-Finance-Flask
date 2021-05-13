const currentVal = document.getElementById('currentPercent').innerHTML;
const currentEle = document.getElementById('current');

if (currentVal < 0) {
	currentEle.classList.remove('green');
	currentEle.classList.add('red');
} else {
	currentEle.classList.remove('red');
	currentEle.classList.add('green');
}

let bigNum = document.getElementById('big-number').innerHTML;
let newNum = toIntlCurrency(bigNum);
document.getElementById('big-number').innerHTML = newNum;

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
	LoadChart();
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
	var priceData = [];
	var dates = [];

	for (var i in data.Close) {
		var dt = i.slice(0, i.length - 3);
		var dateString = moment.unix(dt).format('MM/YY');
		var close = data.Close[i];
		if (close != null) {
			priceData.push(data.Close[i].toFixed(2));
			dates.push(dateString);
		}
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
					borderColor: 'rgb(75, 192, 192)',
					tension: 0,
				},
			],
		},
	});
};
