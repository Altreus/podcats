$(function() {
    // Brevitometer
    /*
    $('#slider').slider( { 
        step: 1, 
        max: 3,
        value: 3,
        slide: function(event, ui) {
            var verbosity = ui.value;
            for( var i = verbosity; i >= 0; --i ) {
                $(".verbose-" + i).show('fast');
            }
            for( var i = verbosity+1; i <= 3; ++i ) {
                $(".verbose-" + i).hide('fast');
            }
        }
    });
    */
    $('#postlist ul').tabs('#content div.story');
});
