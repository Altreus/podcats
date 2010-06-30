(function($) {
    $('link#js-changeme').attr('href', '/static/css/podcats-tabbed.css');
})(jQuery);

$(function() {
    $('#postarea').html( $('#post-1').html() );

    $('#postlist li a').click(function() {
        // the href of these links should be something like '#post-1'
        $('#postarea').html( $( $(this).attr('href' ) ).html() );
    });

    $('#slider').slider( { 
        step: 33, 
        max: 99,
        value: 99,
        slide: function(event, ui) {
            var verbosity = ui.value / 33;
            for( var i = verbosity; i >= 0; --i ) {
                $(".verbose-" + i).show('fast');
            }
            for( var i = verbosity+1; i <= 3; ++i ) {
                $(".verbose-" + i).hide('fast');
            }
        }
    });
});
