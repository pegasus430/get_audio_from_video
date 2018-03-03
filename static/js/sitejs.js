$(document).ready( function($) {
		
	simpleSlide({'swipe':'true'});
	addNotranslate();
		
	$('.slideshow').live('mouseover mouseout', 
		function(event) {
			if(event.type == 'mouseover'){
				$(this).children('.left-button, .right-button').stop(true, true).fadeIn();
			}
			else {
				$(this).children('.left-button, .right-button').stop(true, true).fadeOut();
			}
		}
	);
	
	$('.auto-slider').each( function() {							 
		var related_group = $(this).attr('rel');
		clearInterval($.autoslide);
		$.autoslide = setInterval("simpleSlideAction('.right-button', " + related_group + ");", 4000);
	});	

	// Custom GA tracking event: AJAX Page Loads
		
	$('#nav_links li').live( 'click', function() {
		var page_name = $(this).attr('rel');
				
		pageTracker._trackEvent('Pages', 'Views', page_name);
	});

	$('.right-button, .left-button').live( 'click', function() {
		var action = $(this).attr('class');
				
		pageTracker._trackEvent('Slide Interactions', 'Clicks', action);
	});

	$('#bigboy, #mini').live( 'click', function() {
		var version = $(this).attr('id');
				
		pageTracker._trackEvent('simpleSlide Downloads', 'Downloaded', version);
	});

});
