var Site = function () {
	console.log('in site');
	this.symbol = 'AAPL';
};

Site.prototype.Init = function () {
	console.log('in init');
	console.log($('#symbol').val());
	if ($('#symbol').val()) {
		this.symbol = $('#symbol').val();
	}
	this.LoadChart();
};

Site.prototype.SubmitForm = function () {
	console.log('in submit form');
	this.symbol = $('#symbol').val();
	$.ajax({
		url: '/',
		method: 'POST',
		data: { symbol: this.symbol },
	});
	this.LoadChart();
};

Site.prototype.LoadChart = function () {
	console.log('in loadchart');
	var that = this;
	$.ajax({
		url: '/history?symbol=' + that.symbol,
		method: 'GET',
		cache: false,
	}).done(function (data) {
		console.log(JSON.parse(data));
		that.RenderChart(JSON.parse(data));
	});
};

Site.prototype.RenderChart = function (data) {
	console.log('in renderchart');
	var priceData = [];
	var dates = [];

	for (var i in data.Close) {
		var dt = i.slice(0, i.length - 3);
		var dateString = moment.unix(dt).format('MM/YY');
		var close = data.Close[i];
		if (close != null) {
			priceData.push(data.Close[i]);
			dates.push(dateString);
		}
	}

	new Chart(document.getElementById('myChart'), {
		type: 'line',
		data: {
			labels: dates,
			datasets: [
				{
					label: '',
					data: priceData,
					fill: true,
					borderColor: 'rgb(75, 192, 192)',
					tension: 0,
				},
			],
		},
	});
};

var site = new Site();

$(document).ready(() => {
	console.log($('#symbol').val());
	site.Init();
});
