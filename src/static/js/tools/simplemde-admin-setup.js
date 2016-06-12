(function($) {
    $(document).ready(function(){
        var $simpleMDEs = $('textarea[data-simplemde]');
        // increase the margin between the SimpleMDE editor
        $('label[for^="id"]', $simpleMDEs.parent()).css({
            'margin-bottom': '10px'
        });
        // clear the left margin of the help text
        $('p', $simpleMDEs.parent()).css({
            'margin-left': '0px'
        });
    });
})(django.jQuery || jQuery);
