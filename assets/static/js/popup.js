jQuery(document).ready(function(){
    jQuery('.fancybox').fancybox({
        'transitionIn' : 'elastic',
        'hideOnContentClick': false,
        'height': '90%',
        'width': '90%',
        'autoScale': false,
        'type': 'iframe',
        'speedIn' : 600,
        'speedOut': 600,
        'centerOnScroll': true
    });

    //close fancybox when the close button is clicked
    jQuery('.popup_close').live('click', function(){
        jQuery.fancybox.close();
        return false;
    });

});

