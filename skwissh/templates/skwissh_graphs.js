{% load i18n %}
{% load skwissh_templatetags %}
<!--[if lt IE 9]><script language="javascript" type="text/javascript" src="http://cdn.jsdelivr.net/jqplot/1.0.2/excanvas.js"></script><![endif]-->
<script type="text/javascript" src="http://cdn.jsdelivr.net/jqplot/1.0.2/jquery.jqplot.min.js"></script>
<link rel="stylesheet" type="text/css" href="http://cdn.jsdelivr.net/jqplot/1.0.2/jquery.jqplot.min.css" />
<script type="text/javascript" src="http://cdn.jsdelivr.net/jqplot/1.0.2/plugins/jqplot.pieRenderer.min.js"></script>
<script type="text/javascript" src="http://cdn.jsdelivr.net/jqplot/1.0.2/plugins/jqplot.dateAxisRenderer.min.js"></script>
<script type="text/javascript" src="http://cdn.jsdelivr.net/jqplot/1.0.2/plugins/jqplot.highlighter.min.js"></script>
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
		timeout: 1000,
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
plot_{{ probe.id }} = null;

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
	$("#section-{{ probe.id }} .mesures").show();
	
	if (period === 'last') {
		
		$("#section-{{ probe.id }} .display").hide();
		$("#section-{{ probe.id }} .mesures").hide();
		var mesures_list = mesure_value.split(";");
		var html = "";
		
		html = "<h4 class='single-mesure'>";
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
	
	{% ifequal probe.graph_type.name "linegraph" %}
	
	var nb_values = mesures[0].fields.value.split(";").length;
	var just_values = new Array(); 
	for(var i = 0; i < nb_values; i++) {
		if (typeof graph_data[i] === "undefined")
			graph_data[i] = new Array();
		for(var k = 0, j = mesures.length; k < j; k++) {
			var mesure = mesures[k];
			var mesure_date = new Date(mesure.fields.timestamp);
			var mesure_value = parseFloat(mesure.fields.value.split(";")[i]);
			if (isNaN(mesure_value))
				mesure_value = 0;
			graph_data[i].push([mesure_date, mesure_value]);
			just_values.push(mesure_value);
		}
		var minValue = Math.min.apply(Math, just_values);
		var maxValue = Math.max.apply(Math, just_values);
		var avg = average(just_values);
		var unit = "{% ifnotequal probe.probe_unit "" %} {{ probe.probe_unit }}{% endifnotequal %}";
		$("#min-{{ probe.id }}").html(minValue + unit);
		$("#max-{{ probe.id }}").html(maxValue + unit);
		$("#avg-{{ probe.id }}").html(Math.round(avg*Math.pow(10,3))/Math.pow(10,3) + unit);
		$("#last-{{ probe.id }}").html(just_values[0] + unit);
		var maxDate = graph_data[0][0][0];
		var minDate = graph_data[0][graph_data[0].length-1][0];
	}
	
	{% endifequal %}
	
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
	
	{% ifnotequal period 'last' %}
	{% ifequal probe.graph_type.name 'linegraph' %}
	
	$("#measures-{{ probe.id }}").html();
	var html = "<h6>{% trans 'Détails des mesures' %}</h6>";
	
	html += "<table>"
	html += "<thead><th>{% trans 'Date et heure' %}</th><th>{% trans 'Valeur mesurée' %}</th></thead>";
	html += "<tbody>";
	for(var i=0,j=mesures.length; i<j; i++){
		var mesure = mesures[i]; 
		var date = new Date(mesure.fields.timestamp).format("dd/mm/yyyy HH:MM:00");
		var value = mesure.fields.value.replace(/;/g," / ");
		html += "<tr><td>" + date + "</td><td>" + value + "</td></tr>";
	};
	html += "</tbody>";
	html += "</table>";
	$("#measures-{{ probe.id }}").html(html);
	$("#measures-{{ probe.id }} h6").click(function() {
		$(this).next().toggle();	
		$(this).toggleClass("opened");
	});
	
	{% endifequal %}
	{% endifnotequal %}
	{% endif %}
};

{% endfor %}

function average(l)
{
   var items = l.length;
   var sum = 0;
   for (i = 0; i < items;i++)
      sum += l[i];
   return (sum/items);
}

</script>