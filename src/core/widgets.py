from django import forms
from django.forms.utils import flatatt
from django.utils.html import format_html
from django.utils.encoding import force_text


class SimpleMDEWidget(forms.Textarea):
    """A Markdown editor widget rendering the plain text at client side.

    The code is copied from PyCon Taiwan 2016 website.
    """
    class Media:
        css = {
            'all': [
                'css/vendors/simplemde.min.css',
                'css/tools/simplemde-setup.css',
            ],
        }
        js = [
            'js/vendors/simplemde.min.js',
            'js/tools/simplemde-setup.js'
        ]

    def render(self, name, value, attrs=None):
        attrs = self.build_attrs(attrs, name=name)
        value = value or ''  # if value is None, print empty string instead
        if attrs.get('disabled', False):
            return format_html(
                '<div class="editor-readonly">'
                '<div class="editor-preview editor-preview-active">'
                '{content}</div></div>',
                content=value,
            )
        else:
            attrs['data-simplemde'] = True
            return format_html(
                '<textarea{attrs}>\r\n{content}</textarea>',
                attrs=flatatt(attrs), content=force_text(value),
            )


