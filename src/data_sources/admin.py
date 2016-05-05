from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import DataSource
from .forms import DataSourceCreateForm


class ChecksumBlankListFilter(admin.SimpleListFilter):
    title = _('Checksum')
    parameter_name = 'blank'

    def lookups(self, request, model_admin):
        return (
            ('0', _('Blank')),
            ('1', _('Computed')),
        )

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(checksum__exact='')
        if self.value() == '1':
            return queryset.exclude(checksum__exact='')


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):

    fields = [
        'owner', 'file_path', 'checksum',
    ]
    search_fields = ['owner', 'file_path']
    list_display = [
        'owner', 'file_path', 'checksum',
    ]
    list_filter = (ChecksumBlankListFilter,)

    form = DataSourceCreateForm
