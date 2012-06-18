$.elycharts.templates['streamnumbers-basic'] = {
	type: "line",
	style: {
		"background-color": "#111"
	},
	margins: [7, 7, 7, 5],
	defaultSeries: {
		rounded: false,
		fill: true,
		plotProps: {
			"stroke-width": 4
		},
		dot: true,
		dotShowOnNull: false,
		dotProps: {
			stroke: "#5AF",
			"stroke-width": 2,
			fill: "black"
		},
		startAnimation: {
			active: true,
			type: "grow",
			speed: 800,
			easing: "bounce"
		},
		highlight: {
			scaleSpeed: 0,
			scaleEasing: '',
			scale: 1.5
		},
		tooltip: {
			height: 35,
			width: 95,
			padding: [4, 3],
			offset: [-15, -10],
			frameProps: {
				opacity: 0.75,
				fill: "black",
				stroke: "#CCC"
			}
		}
	},
	series: {
		serie1: {
			color: "#5AF"
		}
	},
	defaultAxis: {
		labels: true,
		labelsProps: {
			fill: "white",
			"font-size": "12px"
		},
		labelsAnchor: "start",
		labelsMargin: 7,
		labelsDistance: -10
	},
	axis: {
		l: {
			labels: true,
			labelsProps: {
				fill: "#eaeaea",
				"font-size": "13px",
				"font-weight": "bold"
			},
			labelsMargin: 12,
			labelsDistance: -6,
			labelsAnchor: "start",
			labelsSkip: 1,
		}
	},
	features: {
		mousearea: {
			type: 'axis'
		},
		tooltip: {
			positionHandler: function(env, tooltipConf, mouseAreaData, suggestedX, suggestedY) {
				return [mouseAreaData.event.pageX, mouseAreaData.event.pageY, true]
			}
		},
		grid: {
			draw: true,
			forceBorder: true,
			ny: 4,
			nx: 4,
			props: {
				stroke: "#505040"
			}
		}
	}
}

$.elycharts.templates['streamnumbers-hour'] = $.extend(true, {}, $.elycharts.templates['streamnumbers-basic']);
$.elycharts.templates['streamnumbers-day'] = $.extend(true, {}, $.elycharts.templates['streamnumbers-basic']);
$.elycharts.templates['streamnumbers-week'] = $.extend(true, {}, $.elycharts.templates['streamnumbers-basic']);
$.elycharts.templates['streamnumbers-month'] = $.extend(true, {}, $.elycharts.templates['streamnumbers-basic']);

$.elycharts.templates['streamnumbers-day']['features']['grid']['nx'] = 6;
$.elycharts.templates['streamnumbers-week']['features']['grid']['nx'] = 7;
$.elycharts.templates['streamnumbers-month']['features']['grid']['nx'] = 6;
