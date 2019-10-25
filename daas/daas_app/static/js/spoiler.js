$(function(){
	$('.spoiler-text').hide();
	$('.spoiler-toggle').click(function(){
		$(this).next().animate({height: 'toggle'});
		if ($('.spoiler-text').hasClass("do_not_show")){
			$('.spoiler-text').removeClass("do_not_show");
			$(this).html('<a id="search-text" href="#search"><span class="glyphicon glyphicon-plus"></span>&#x25BC;Advanced Search</a>');
		}
		else{
			$('.spoiler-text').addClass("do_not_show");
			$(this).html('<a id="search-text" href="#search"><span class="glyphicon glyphicon-minus"></span>&#x25BC;Advanced Search</a>');
		}
	}); // end spoiler-toggle
}); // end document ready