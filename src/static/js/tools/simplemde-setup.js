// use jQuery or the jQuery bundled by django admin
(function($) {
    $(document).ready(function(){
        $('textarea[data-simplemde]').each(function() {
            new SimpleMDE({
                'element': this,
                'indentWithTabs': false,
                'spellChecker': false,
                'status': false,
                'tabSize': 4,
                'renderingConfig': {
                    'singleLineBreaks': false
                }
            });
        });
    });
})(jQuery || (typeof django !== 'undefined' && django.jQuery));


(function (SimpleMDE) {

    if (!document.querySelectorAll || !window.DOMParser)
        return;

    var parser = new DOMParser();
    var elementList = document.querySelectorAll(
        '.editor-readonly > .editor-preview'
    );
    for (var i = 0; i < elementList.length; i++) {
        var element = elementList[i];
        var source = element.textContent || element.innerText;
        element.innerHTML = SimpleMDE.prototype.markdown(
            parser.parseFromString(source, 'text/html').documentElement.textContent
        );
    }

})(SimpleMDE);
