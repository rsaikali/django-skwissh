{% load i18n %}
<!--[if lt IE 9]><script language="javascript" type="text/javascript" src="http://cdn.jsdelivr.net/jqplot/1.0.2/excanvas.js"></script><![endif]-->
<script type="text/javascript" src="http://cdn.jsdelivr.net/jqplot/1.0.2/jquery.jqplot.min.js"></script>
<link rel="stylesheet" type="text/css" href="http://cdn.jsdelivr.net/jqplot/1.0.2/jquery.jqplot.min.css" />
<script type="text/javascript" src="http://cdn.jsdelivr.net/jqplot/1.0.2/plugins/jqplot.pieRenderer.min.js"></script>
<script type="text/javascript" src="http://cdn.jsdelivr.net/jqplot/1.0.2/plugins/jqplot.barRenderer.min.js"></script>
<script type="text/javascript" src="{{ STATIC_URL }}skwissh/javascripts/jqplot/plugins/jqplot.dateAxisRenderer.min.js"></script>
<script type="text/javascript" src="http://cdn.jsdelivr.net/jqplot/1.0.2/plugins/jqplot.highlighter.min.js"></script>
<script type="text/javascript" src="http://cdn.jsdelivr.net/jqplot/1.0.2/plugins/jqplot.cursor.min.js"></script>
<script type="text/javascript" src="{{ STATIC_URL }}skwissh/javascripts/date.format.js"></script>
<script type="text/javascript" src="{{ STATIC_URL }}skwissh/javascripts/plots.js"></script>
<script type="text/javascript">
var plots = {}
var get_mesures_url = "{% url mesures server.id '999' 'period' %}";
var graphtypes = {}
{% for graphtype in graphtypes %}
graphtypes['{{ graphtype.name }}'] = { {{ graphtype.options|safe }} };
{% endfor %}
$(document).ready(function() {
	$.jqplot.config.enablePlugins = true; 	
	{% for probe in server.probes.all %}
	var graphtype = '{{ probe.graph_type.name }}';
	refreshGraph(get_mesures_url.replace('period', '{{default_view}}').replace('999', {{ probe.id }}), '{{default_view}}', graphtype, {{ probe.id }}, '{{ probe.display_name }}', '{{ probe.probe_labels }}', '{{ probe.probe_unit }}');
	{% endfor %}
});
{% for probe in server.probes.all %}{% ifnotequal probe.graph_type.name 'text' %}
$('.period-{{ probe.id }}').click(function(e){
	e.preventDefault();
	$("#graphtypeDropdown-{{ probe.id }} option:selected").each(function () {		
		graphtype = $(this).text();
	});	
	refreshGraph(get_mesures_url.replace('period', $(this).data("period")).replace('999', {{ probe.id }}), $(this).data("period"), graphtype, {{ probe.id }}, '{{ probe.display_name }}', '{{ probe.probe_labels }}', '{{ probe.probe_unit }}', $(this));
});
$("#graphtypeDropdown-{{ probe.id }}").change(function() {
	var probe_id = $(this).data("probe-id");
	var period = $('#section-' + probe_id + ' .nav-bar .active .period-' + probe_id).data("period");
	if (typeof(period) === "undefined")
		period = 'hour';
	$("#graphtypeDropdown-{{ probe.id }} option:selected").each(function () {		
		graphtype = $(this).text();
	});
	refreshGraph(get_mesures_url.replace('period', period).replace('999', {{ probe.id }}), period, graphtype, {{ probe.id }}, '{{ probe.display_name }}', '{{ probe.probe_labels }}', '{{ probe.probe_unit }}');
});
{% endifnotequal %}{% endfor %}	
</script>