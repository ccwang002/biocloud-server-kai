from django.contrib import admin

from analyses.admin import (
    AbstractAnalysisAdmin,
    AbstractAnalysisAdminUpdateForm,
)
from .models import RNASeqModel, RNASeqExeDetail


class RNASeqAdminUpdateForm(AbstractAnalysisAdminUpdateForm):
    class Meta(AbstractAnalysisAdminUpdateForm.Meta):
        model = RNASeqModel


class RNASeqExeDetailInline(admin.StackedInline):
    model = RNASeqExeDetail


@admin.register(RNASeqModel)
class RNASeqModelAdmin(AbstractAnalysisAdmin):

    form = RNASeqAdminUpdateForm
    list_display = (
        *AbstractAnalysisAdmin.list_display,
        "genome_aligner",
    )
    inlines = [
        RNASeqExeDetailInline,
    ]
