$.Isotope.prototype._spineAlignReset = function() {
	this.spineAlign = {
		colA : 0,
		colB : 0
	};
};

$.Isotope.prototype._spineAlignLayout = function($elems) {
	var instance = this, props = this.spineAlign, gutterWidth = Math.round(this.options.spineAlign && this.options.spineAlign.gutterWidth) || 0, centerX = Math.round(this.element.width() / 2);

	$elems.each(function() {
		var $this = $(this), isColA = props.colB > props.colA, x = isColA ? centerX - ($this.outerWidth(true) + gutterWidth / 2 ) : // left side
		centerX + gutterWidth / 2, // right side
		y = isColA ? props.colA : props.colB;
		instance._pushPosition($this, x, y);
		props[( isColA ? 'colA' : 'colB' )] += $this.outerHeight(true);
	});
};

$.Isotope.prototype._spineAlignGetContainerSize = function() {
	var size = {};
	size.height = this.spineAlign[(this.spineAlign.colB > this.spineAlign.colA ? 'colB' : 'colA' )];
	return size;
};

$.Isotope.prototype._spineAlignResizeChanged = function() {
	return true;
};

var $container = $('#servergroup-list')
if ($container.width() < 800) {
	$container.isotope({
		layoutMode : 'fitRows'
	});
} else {
	$container.isotope({
		layoutMode : 'spineAlign',
		spineAlign : {
			gutterWidth : 20
		},
	});
}

$(window).smartresize(function() {
	if ($container.width() < 800) {
		$container.isotope({
			layoutMode : 'fitRows'
		});
	} else {
		$container.isotope({
			layoutMode : 'spineAlign',
			spineAlign : {
				gutterWidth : 20
			},
		});
	}
});
