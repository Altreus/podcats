$(function() {
    // Brevitometer
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

    // Move tabs to the top if JS is available.
    var postlist = $('#postlist');
    var tabbar = $('<div id="tabs"/>');
    postlist.find('h1').remove();
    var ul = postlist.find('ul');
    ul.appendTo(tabbar);
    ul.tabs('#content div.story');

    tabbar.prependTo($('#body'));

    ul.jcarousel({
        scroll: 2
    });
});
