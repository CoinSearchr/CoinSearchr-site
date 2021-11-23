// uses charts.js

const default_base_currency = 'usd'; // TODO get this from cookie or URL (Issue #15)
const default_num_days = 7; // TODO get this from an input element

function make_top_chart(coin_id, base_currency = default_base_currency, num_days = default_num_days) {

	$.get(
		"https://api.coingecko.com/api/v3/coins/" + coin_id + "/market_chart",
		{'vs_currency' : base_currency, 'days' : num_days},
		function(data) {
			// when the data is loaded, create the chart

			const labels = data.prices.map(function(timestamp_price_tuple) {
				return new Date(timestamp_price_tuple[0]);
			});
			const prices = data.prices.map(function(timestamp_price_tuple) {
				return timestamp_price_tuple[1];
			});

			let time_unit = 'day';
			if (num_days < 6) {
				time_unit = 'hour';
			}
			else if (num_days > 29) {
				time_unit = 'week';
			}
			
			const top_price_chart_7d = new Chart(document.getElementById('top-price-chart-7d').getContext('2d'), {
				type: 'line',
				data: {
					labels: labels,
					datasets: [{
						label: 'Price (' + base_currency.toUpperCase() + ')',
						data: prices,
						borderColor: 'rgb(75, 192, 192)'
					}]
				},
				options: {
					scales: {
						x: {
							type: 'timeseries',
							time: {
								unit: time_unit
							}

						},
						y: {
							beginAtZero: false
						}
					},

					plugins: {
						title: {
							display: true,
							text: num_days + '-Day Price Chart'
						},
						legend: {
							display: false
						}
					}
				}
			});
		}
	);

}
