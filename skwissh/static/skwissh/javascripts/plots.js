function refreshGraph(url, period, graphtype, probe_id, display_name, labels, units, element) {
	if ( typeof element != "undefined") {
		element.parents("ul.nav-bar").children("li").removeClass("active");
		element.parents("li").addClass("active");
	}
	$("#graph-" + probe_id).empty();
	$("#graph-" + probe_id).css('height', 'auto');
	$("#detail-" + probe_id + " .waiting, #detail-" + probe_id + " .waiting-title").show();
	$.ajax({
		async : true,
		url : url,
		dataType : "json",
		success : function(mesures) {
			if (mesures.length === 0)
				showError("No data found for sensor \'" + display_name + "\'.", probe_id);
			else
				updateGraph(mesures, graphtype, probe_id, labels, units, period);
		},
		error : function(mesures) {
			showError("An error occured while building sensor graph \'" + display_name + "\'.", probe_id);
		}
	});
};
function updateGraph(mesures, graphtype, probe_id, labels, units, period) {
	var mesure_value = mesures[0].fields.value;
	if (graphtype === "text") {
		var html = "<textarea disabled class='text-output'>" + mesure_value + "</textarea>";
		$("#detail-" + probe_id + " .waiting, #detail-" + probe_id + " .waiting-title").hide();
		$("#graph-" + probe_id).html(html);
		return;
	} else {
		var graph_options = jQuery.extend(true, {}, graphtypes[graphtype]);
		;
		if (labels.length != 0) {
			str_labels = labels.split(";");
			for (var i = 0; i < str_labels.length; i++) {
				if ( typeof graph_options.series === "undefined")
					graph_options.series = new Array();
				graph_options.series.push({
					label : str_labels[i]
				});
			}
			graph_options.legend = {
				show : true,
				location : 'w',
				placement : 'inside',
				preDraw : true,
			};
		}
		$("#section-" + probe_id + " .display").show();
		if (period === 'last') {
			$("#section-" + probe_id + " .display").hide();
			var mesures_list = mesure_value.split(";");
			var html = "<h4 class='single-mesure'>";
			for (var i = 0, j = mesures_list.length; i < j; i++) {
				var value = mesures_list[i];
				if (i != 0)
					html = html + " / ";
				if (value == "")
					value = "0";
				html = html + value + " " + units;
			}
			html = html + "</h4>";
			$("#detail-" + probe_id + " .waiting, #detail-" + probe_id + " .waiting-title").hide();
			$("#graph-" + probe_id).html(html);
			return;
		}
		var graph_data = new Array();
		if (graphtype.indexOf("graph") != -1) {
			var nb_values = mesures[0].fields.value.split(";").length;
			$("#summary-" + probe_id).empty();
			for (var i = 0; i < nb_values; i++) {
				var just_values = new Array();
				if ( typeof graph_data[i] === "undefined")
					graph_data[i] = new Array();
				for (var k = 0, j = mesures.length; k < j; k++) {
					var mesure = mesures[k];
					var mesure_date = $.jsDate.strftime(new $.jsDate(new Date(mesure.fields.timestamp)), "%Y-%m-%d %H:%M:%S");
					var mesure_value = parseFloat(mesure.fields.value.split(";")[i]);
					if (isNaN(mesure_value))
						mesure_value = 0;
					graph_data[i].push([mesure_date, mesure_value]);
					just_values.push(mesure_value);
				}
				var minValue = roundNumber(Math.min.apply(Math, just_values), 2);
				var maxValue = roundNumber(Math.max.apply(Math, just_values), 2);
				var avg = roundNumber(average(just_values), 2);
				var unit = " " + units;
				$("#summary-" + probe_id).append("<div class='display'>")
				$("#summary-" + probe_id).append("<div class='two columns border'><span id='min-" + probe_id + "'>" + labels.split(';')[i] + "</span></div>");
				$("#summary-" + probe_id).append("<div class='two columns border'>Min : <span id='min-" + probe_id + "'>" + minValue + unit + "</span></div>");
				$("#summary-" + probe_id).append("<div class='two columns border'>Max : <span id='max-" + probe_id + "'>" + maxValue + unit + "</span></div>");
				$("#summary-" + probe_id).append("<div class='two columns border'>Avg : <span id='avg-" + probe_id + "'>" + avg + unit + "</span></div>");
				$("#summary-" + probe_id).append("<div class='two columns border'>Last : <span id='last-" + probe_id + "'>" + just_values[0] + unit + "</span></div>");
				$("#summary-" + probe_id).append("<div class='two columns'></div>");
				$("#summary-" + probe_id).append("</div>")
			}
			for (var i = 0; i < graph_data.length; i++) {
				var data = graph_data[i];
				var desired_start_date = new $.jsDate(new Date()).add(-1, period).add(1, 'minute');
				desired_start_date = desired_start_date.add(-desired_start_date.getSeconds(), 'seconds');
				var effective_start_date = new $.jsDate(data[data.length -1][0]);
				var fake_values = []
				while (desired_start_date.getUnix() < effective_start_date.getUnix()) {
					if (period == "hour")
						desired_start_date = new $.jsDate(desired_start_date).add(1, 'minute')
					else if (period == "day")
						desired_start_date = new $.jsDate(desired_start_date).add(10, 'minute')
					else if (period == "week")
						desired_start_date = new $.jsDate(desired_start_date).add(1, 'hour')
					else if (period == "month")
						desired_start_date = new $.jsDate(desired_start_date).add(3, 'hour')

					fake_values.push([$.jsDate.strftime(desired_start_date.getTime(), "%Y-%m-%d %H:%M:%S"), 0])
				}
				graph_data[i] = graph_data[i].concat(reverseArray(fake_values, false));
			};
			var maxDate = graph_data[0][0][0];
			var minDate = graph_data[0][graph_data[0].length-1][0];
			var bMgin = 1;
			if (period === 'hour') {
				var tickInt = '5 minutes';
				bMgin = 2;
			} else if (period === 'day')
				var tickInt = '2 hours';
			else if (period === 'week')
				var tickInt = '1 days';
			else if (period === 'month')
				var tickInt = '3 days';

			graph_options.animate = true;
			graph_options.animateReplot = false;

			graph_options.axes.yaxis.tickOptions.formatString = graph_options.axes.yaxis.tickOptions.formatString.replace("@UNITS@", units);
			graph_options.axes.xaxis.min = minDate;
			graph_options.axes.xaxis.max = maxDate;
			graph_options.axes.xaxis.tickInterval = tickInt;
			if ( typeof graph_options.seriesDefaults.rendererOptions === "undefined")
				graph_options.seriesDefaults.rendererOptions = new Object();
			graph_options.seriesDefaults.rendererOptions.barMargin = bMgin;

			if (graphtype.indexOf("groups") != -1) {
				graph_options.seriesDefaults.rendererOptions.barMargin = 0;
				graph_options.seriesDefaults.rendererOptions.barPadding = 2;
				graph_options.seriesDefaults.rendererOptions.barWidth = 3;
			}
		} else if (graphtype == "pie") {
			var lbls = labels.split(';')
			var data = mesures[0].fields.value.split(';');
			var tmp_data = new Array();
			for (var i = 0; i < data.length; i++) {
				mesure_value = parseInt(data[i]);
				if (isNaN(mesure_value))
					mesure_value = 0;
				tmp_data.push([lbls[i], mesure_value]);
			}
			graph_data.push(tmp_data);
		}
		$("#detail-" + probe_id + " .waiting, #detail-" + probe_id + " .waiting-title").hide();
		plots[probe_id] = $.jqplot('graph-' + probe_id, graph_data, graph_options);
	}
};
function average(l) {
	var items = l.length;
	var sum = 0;
	for ( i = 0; i < items; i++)
		sum += l[i];
	return (sum / items);
};
function roundNumber(rnum, rlength) {
	return parseFloat(Math.round(rnum * Math.pow(10, rlength)) / Math.pow(10, rlength));
};
function reverseArray(array, preserve_keys) {
	var isArray = Object.prototype.toString.call(array) === "[object Array]", tmp_arr = preserve_keys ? {} : [], key;
	if (isArray && !preserve_keys)
		return array.slice(0).reverse();
	if (preserve_keys) {
		var keys = [];
		for (key in array)
		keys.push(key);
		var i = keys.length;
		while (i--)
		tmp_arr[keys[i]] = array[keys[i]];
	} else
		for (key in array)
		tmp_arr.unshift(array[key]);
	return tmp_arr;
};
function jqplotToImg(obj) {
	var newCanvas = document.createElement("canvas");
	newCanvas.width = obj.find("canvas.jqplot-base-canvas").width();
	newCanvas.height = obj.find("canvas.jqplot-base-canvas").height() + 10;
	var baseOffset = obj.find("canvas.jqplot-base-canvas").offset();
	var context = newCanvas.getContext("2d");
	context.fillStyle = "rgba(255,255,255,1)";
	context.fillRect(0, 0, newCanvas.width, newCanvas.height);
	obj.children().each(function() {
		if ($(this)[0].tagName.toLowerCase() == 'div') {
			$(this).children("canvas").each(function() {
				var offset = $(this).offset();
				newCanvas.getContext("2d").drawImage(this, offset.left - baseOffset.left, offset.top - baseOffset.top);
			});
			$(this).children("div").each(function() {
				var offset = $(this).offset();
				var context = newCanvas.getContext("2d");
				context.font = $(this).css('font-style') + " " + $(this).css('font-size') + " " + $(this).css('font-family');
				context.fillStyle = $(this).css('color');
				context.fillText($(this).text(), offset.left - baseOffset.left, offset.top - baseOffset.top + $(this).height());
			});
		} else if ($  (this)[0].tagName.toLowerCase() == 'canvas') {
			var offset = $(this).offset();
			newCanvas.getContext("2d").drawImage(this, offset.left - baseOffset.left, offset.top - baseOffset.top);
		}
	});
	obj.children(".jqplot-point-label").each(function() {
		var offset = $(this).offset();
		var context = newCanvas.getContext("2d");
		context.font = $(this).css('font-style') + " " + $(this).css('font-size') + " " + $(this).css('font-family');
		context.fillStyle = $(this).css('color');
		context.fillText($(this).text(), offset.left - baseOffset.left, offset.top - baseOffset.top + $(this).height() * 3 / 4);
	});
	obj.children("div.jqplot-title").each(function() {
		var offset = $(this).offset();
		var context = newCanvas.getContext("2d");
		context.font = $(this).css('font-style') + " " + $(this).css('font-size') + " " + $(this).css('font-family');
		context.textAlign = $(this).css('text-align');
		context.fillStyle = $(this).css('color');
		context.fillText($(this).text(), newCanvas.width / 2, offset.top - baseOffset.top + $(this).height());
	});
	obj.children("table.jqplot-table-legend").each(function() {
		var offset = $(this).offset();
		var context = newCanvas.getContext("2d");
		context.strokeStyle = $(this).css('border-top-color');
		context.strokeRect(offset.left - baseOffset.left, offset.top - baseOffset.top, $(this).width(), $(this).height());
		context.fillStyle = $(this).css('background-color');
		context.fillRect(offset.left - baseOffset.left, offset.top - baseOffset.top, $(this).width(), $(this).height());
	});
	obj.find("div.jqplot-table-legend-swatch").each(function() {
		var offset = $(this).offset();
		var context = newCanvas.getContext("2d");
		context.fillStyle = $(this).css('background-color');
		context.fillRect(offset.left - baseOffset.left, offset.top - baseOffset.top, $(this).parent().width(), $(this).parent().height());
	});
	obj.find("td.jqplot-table-legend").each(function() {
		var offset = $(this).offset();
		var context = newCanvas.getContext("2d");
		context.font = $(this).css('font-style') + " " + $(this).css('font-size') + " " + $(this).css('font-family');
		context.fillStyle = $(this).css('color');
		context.textAlign = $(this).css('text-align');
		context.textBaseline = $(this).css('vertical-align');
		context.fillText($(this).text(), offset.left - baseOffset.left, offset.top - baseOffset.top + $(this).height() / 2 + parseInt($(this).css('padding-top').replace('px', '')));
	});
	return newCanvas.toDataURL("image/png");
};
function showError(message, probe_id) {
	$("#detail-" + probe_id + " .waiting, #detail-" + probe_id + " .waiting-title").hide();
	$("#graph-" + probe_id).html('<div class="alert-box alert">' + message + '</div>');
};
$(window).resize(function() {
	for (id in plots)
	plots[id].replot({
		resetAxes : false
	});
});

