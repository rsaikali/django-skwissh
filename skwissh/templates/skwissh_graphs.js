{% load i18n %}
{% load skwissh_templatetags %}
<!--[if lt IE 9]><script language="javascript" type="text/javascript" src="http://cdn.jsdelivr.net/jqplot/1.0.2/excanvas.js"></script><![endif]-->
<script type="text/javascript" src="http://cdn.jsdelivr.net/jqplot/1.0.2/jquery.jqplot.min.js"></script>
<link rel="stylesheet" type="text/css" href="http://cdn.jsdelivr.net/jqplot/1.0.2/jquery.jqplot.min.css" />
<script type="text/javascript" src="http://cdn.jsdelivr.net/jqplot/1.0.2/plugins/jqplot.pieRenderer.min.js"></script>
<script type="text/javascript" src="http://cdn.jsdelivr.net/jqplot/1.0.2/plugins/jqplot.barRenderer.min.js"></script>
<script type="text/javascript" src="{{ STATIC_URL }}skwissh/javascripts/jqplot/plugins/jqplot.dateAxisRenderer.min.js"></script>
<script type="text/javascript" src="http://cdn.jsdelivr.net/jqplot/1.0.2/plugins/jqplot.highlighter.min.js"></script>
<script type="text/javascript" src="http://cdn.jsdelivr.net/jqplot/1.0.2/plugins/jqplot.cursor.min.js"></script>
<script type="text/javascript" src="{{ STATIC_URL }}skwissh/javascripts/date.format.js"></script>
<script type="text/javascript">
$(document).ready(function() {
	$.jqplot.config.enablePlugins = true; 	
    {% for probe in server.probes.all %}
		refreshGraph_{{ probe.id }}('hour');
    {% endfor %}
});
{% for probe in server.probes.all %}
	{% ifnotequal probe.graph_type.name 'text' %}
	$('.period-{{ probe.id }}').click(function(e){
		e.preventDefault();
		refreshGraph_{{ probe.id }}($(this).data("period"), $(this));
	});
	{% endifnotequal %}
	function refreshGraph_{{ probe.id }}(period, element) {
		if (typeof element != "undefined") {
			element.parents("ul.nav-bar").children("li").removeClass("active");
			element.parents("li").addClass("active");
		}
		$("#graph-{{ probe.id }}").empty();
		$("#graph-{{ probe.id }}").css('height','auto');
		$("#detail-{{ probe.id }} .waiting, #detail-{{ probe.id }} .waiting-title").show();
		$.ajax({
			async : true,
			url : "{% url mesures server.id probe.id 'period' %}".replace('period', period),
			dataType : "json",
			success : function(mesures) {
				if (mesures.length === 0) {
					showError_{{ probe.id }}("{% blocktrans %}Aucune mesure n'a été trouvée pour la sonde{% endblocktrans %} \'{{ probe.display_name }}\'.");
				}
				updateGraph_{{ probe.id }}(mesures, period);
			},
			error : function(mesures) {
				showError_{{ probe.id }}("{% blocktrans %}Une erreur s\'est produite lors de la construction du graphique{% endblocktrans %} \'{{ probe.display_name }}\'.");
			}
		});
	};
	function showError_{{ probe.id }}(message) {
		$("#detail-{{ probe.id }} .waiting, #detail-{{ probe.id }} .waiting-title").hide();
		$("#graph-{{ probe.id }}").html('<div class="alert-box alert">' + message + '</div>');
	};
	{% ifnotequal probe.graph_type.name 'text' %}
	var plot_{{ probe.id }} = null;
	$(window).resize(function() {
		plot_{{ probe.id }}.replot( { resetAxes: false } );
	});
	{% endifnotequal %}
	function updateGraph_{{ probe.id }}(mesures, period) {
		var mesure_value = mesures[0].fields.value;
		{% if probe.graph_type.name == 'text' %}
		var html = "<textarea disabled class='text-output'>" + mesure_value + "</textarea>";
		$("#detail-{{ probe.id }} .waiting, #detail-{{ probe.id }} .waiting-title").hide();
		$("#graph-{{ probe.id }}").html(html);
		{% else %}
		$("#section-{{ probe.id }} .display").show();
		if (period === 'last') {
			$("#section-{{ probe.id }} .display").hide();
			var mesures_list = mesure_value.split(";");
			var html = "<h4 class='single-mesure'>";
			for(var i=0,j=mesures_list.length; i<j; i++){
				var value = mesures_list[i];
				if (i!=0)
					html = html + " / ";
				if (value == "")
					value = "0";			
				html = html + value + " {{ probe.probe_unit }}";
			}
			html = html + "</h4>";
			$("#detail-{{ probe.id }} .waiting, #detail-{{ probe.id }} .waiting-title").hide();
			$("#graph-{{ probe.id }}").html(html);
			return;
		}
		var graph_data = new Array();
		{% if probe.graph_type.name == "linegraph" or probe.graph_type.name == 'bargraph'%}
		var nb_values = mesures[0].fields.value.split(";").length;
		var labels = "{{ probe.probe_labels }}";
		$("#summary-{{ probe.id }}").empty();
		for(var i = 0; i < nb_values; i++) {
			var just_values = new Array(); 
			if (typeof graph_data[i] === "undefined")
				graph_data[i] = new Array();
			for(var k = 0, j = mesures.length; k < j; k++) {
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
			var unit = "{% ifnotequal probe.probe_unit "" %} {{ probe.probe_unit }}{% endifnotequal %}";
			$("#summary-{{ probe.id }}").append("<div class='display'>")
			$("#summary-{{ probe.id }}").append("<div class='two columns border'><span id='min-{{ probe.id }}'>" + labels.split(';')[i] + "</span></div>");
			$("#summary-{{ probe.id }}").append("<div class='two columns border'>Min : <span id='min-{{ probe.id }}'>" + minValue + unit + "</span></div>");
			$("#summary-{{ probe.id }}").append("<div class='two columns border'>Max : <span id='max-{{ probe.id }}'>" + maxValue + unit + "</span></div>");
			$("#summary-{{ probe.id }}").append("<div class='two columns border'>Avg : <span id='avg-{{ probe.id }}'>" + avg + unit + "</span></div>");
			$("#summary-{{ probe.id }}").append("<div class='two columns border'>Last : <span id='last-{{ probe.id }}'>" + just_values[0] + unit + "</span></div>");
			$("#summary-{{ probe.id }}").append("<div class='two columns'></div>");
			$("#summary-{{ probe.id }}").append("</div>")
		}
		for (var i=0; i < graph_data.length; i++) {
		  var data = graph_data[i];
		  var desired_start_date = new $.jsDate(new Date()).add(-1, period).add(1, 'minute');
		  desired_start_date = desired_start_date.add(- desired_start_date.getSeconds(), 'seconds');
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
		}
		else if (period === 'day')
			var tickInt = '2 hours';
		else if (period === 'week')
			var tickInt = '1 days';
		else if (period === 'month')
			var tickInt = '3 days';
		{% endif %}
		{% ifequal probe.graph_type.name "pie" %}
		var labels = "{{ probe.probe_labels }}".split(';');
		var data = mesures[0].fields.value.split(';');
		var tmp_data = new Array();
		for(var i=0; i<data.length; i++) {
			mesure_value = parseInt(data[i]);
			if (isNaN(mesure_value))
				mesure_value = 0;
		  	tmp_data.push([labels[i],mesure_value]);
		}
		graph_data.push(tmp_data);
		{% endifequal %}
		$("#detail-{{ probe.id }} .waiting, #detail-{{ probe.id }} .waiting-title").hide();
		var graph_options = { {{ probe.graph_type.options|addunits:probe.probe_unit|addlegend:probe.probe_labels|safe }} };
		plot_{{ probe.id }} = $.jqplot('graph-{{ probe.id }}', graph_data, graph_options);
		{% endif %}
	};
{% endfor %}
function average(l) {
	var items = l.length;
   	var sum = 0;
   	for (i = 0; i < items;i++)
      	sum += l[i];
   	return (sum/items);
}
function roundNumber(rnum, rlength) {
  	return parseFloat(Math.round(rnum*Math.pow(10,rlength))/Math.pow(10,rlength));
}
function reverseArray(array, preserve_keys) {
	var isArray = Object.prototype.toString.call(array) === "[object Array]", tmp_arr = preserve_keys ? {} : [], key;
    if (isArray && !preserve_keys)
    	return array.slice(0).reverse();
    if (preserve_keys) {
        var keys = [];
        for (key in array)
            keys.push(key);
        var i = keys.length;
        while (i--) {
            key = keys[i];
            tmp_arr[key] = array[key];
        }
    } else {
        for (key in array) {
            tmp_arr.unshift(array[key]);
        }
    }
    return tmp_arr;
}
function jqplotToImg(obj) {
    var newCanvas = document.createElement("canvas");
    newCanvas.width = obj.find("canvas.jqplot-base-canvas").width();
    newCanvas.height = obj.find("canvas.jqplot-base-canvas").height()+10;
    var baseOffset = obj.find("canvas.jqplot-base-canvas").offset();

    var context = newCanvas.getContext("2d");
    context.fillStyle = "rgba(255,255,255,1)";
    context.fillRect(0, 0, newCanvas.width, newCanvas.height);

    obj.children().each(function () {
        if ($(this)[0].tagName.toLowerCase() == 'div') {
            $(this).children("canvas").each(function() {
                var offset = $  (this).offset();
                newCanvas.getContext("2d").drawImage(this,
                    offset.left - baseOffset.left,
                    offset.top - baseOffset.top
                );
            });
            $(this).children("div").each(function() {
                var offset = $(this).offset();
                var context = newCanvas.getContext("2d");
                context.font = $(this).css('font-style') + " " + $(this).css('font-size') + " " + $(this).css('font-family');
                context.fillStyle = $(this).css('color');
                context.fillText($(this).text(),
                    offset.left - baseOffset.left,
                    offset.top - baseOffset.top + $(this).height()
                );
            });
        } else if($  (this)[0].tagName.toLowerCase() == 'canvas') {
            // all other canvas from the chart
            var offset = $  (this).offset();
            newCanvas.getContext("2d").drawImage(this,
                offset.left - baseOffset.left,
                offset.top - baseOffset.top
            );
        }
    });

    // add the point labels
    obj.children(".jqplot-point-label").each(function() {
        var offset = $  (this).offset();
        var context = newCanvas.getContext("2d");
        context.font = $  (this).css('font-style') + " " + $  (this).css('font-size') + " " + $  (this).css('font-family');
        context.fillStyle = $  (this).css('color');
        context.fillText($  (this).text(),
            offset.left - baseOffset.left,
            offset.top - baseOffset.top + $  (this).height()*3/4
        );
    });

    // add the title
    obj.children("div.jqplot-title").each(function() {
        var offset = $  (this).offset();
        var context = newCanvas.getContext("2d");
        context.font = $  (this).css('font-style') + " " + $  (this).css('font-size') + " " + $  (this).css('font-family');
        context.textAlign = $  (this).css('text-align');
        context.fillStyle = $  (this).css('color');
        context.fillText($  (this).text(),
            newCanvas.width / 2,
            offset.top - baseOffset.top + $  (this).height()
        );
    });

    // add the legend
    obj.children("table.jqplot-table-legend").each(function() {
        var offset = $  (this).offset();
        var context = newCanvas.getContext("2d");
        context.strokeStyle = $  (this).css('border-top-color');
        context.strokeRect(
            offset.left - baseOffset.left,
            offset.top - baseOffset.top,
            $  (this).width(),$  (this).height()
        );
        context.fillStyle = $  (this).css('background-color');
        context.fillRect(
            offset.left - baseOffset.left,
            offset.top - baseOffset.top,
            $  (this).width(),$  (this).height()
        );
    });

    // add the rectangles
    obj.find("div.jqplot-table-legend-swatch").each(function() {
        var offset = $  (this).offset();
        var context = newCanvas.getContext("2d");
        context.fillStyle = $  (this).css('background-color');
        context.fillRect(
            offset.left - baseOffset.left,
            offset.top - baseOffset.top,
            $  (this).parent().width(),$  (this).parent().height()
        );
    });

    obj.find("td.jqplot-table-legend").each(function() {
        var offset = $  (this).offset();
        var context = newCanvas.getContext("2d");
        context.font = $  (this).css('font-style') + " " + $  (this).css('font-size') + " " + $  (this).css('font-family');
        context.fillStyle = $  (this).css('color');
        context.textAlign = $  (this).css('text-align');
        context.textBaseline = $  (this).css('vertical-align');
        context.fillText($  (this).text(),
            offset.left - baseOffset.left,
            offset.top - baseOffset.top + $  (this).height()/2 + parseInt($  (this).css('padding-top').replace('px',''))
        );
    });

    // convert the image to base64 format
    return newCanvas.toDataURL("image/png");
}



</script>