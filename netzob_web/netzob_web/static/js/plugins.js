// place any jQuery/helper plugins in here, instead of separate, slower script files.

//plugin to make any element text editable
$.fn.extend({
    editable: function () {
	$(this).each(function () {
	    var $el = $(this),
		
		$edittextbox = $('<input type="text"></input>').css('min-width', $el.width()),
		submitChanges = function () {
		    if ($edittextbox.val() !== '') {
			$el.html($edittextbox.val());
			$el.show();
			$el.trigger('editsubmit', [$el.html()]);
			$(document).unbind('click', submitChanges);
			$edittextbox.detach();
		    }
		},
		tempVal;
	    $edittextbox.click(function (event) {
		event.stopPropagation();
	    });

	    $el.addClass("editable");
	    

	    $el.dblclick(function (e) {
		tempVal = $el.html();
		$edittextbox.val(tempVal).insertBefore(this)
			    .bind('keypress', function (e) {
				var code = (e.keyCode ? e.keyCode : e.which);
				if (code == 13) {
				    submitChanges();
				}
			    }).select();
		$el.hide();
		$(document).click(submitChanges);
	    });
	});
	return this;
    }
});
