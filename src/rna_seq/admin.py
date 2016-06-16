from django.contrib import admin

from analyses.admin import (
    AbstractAnalysisAdmin,
    AbstractAnalysisAdminUpdateForm,
)
from .models import RNASeqModel


class RNASeqAdminUpdateForm(AbstractAnalysisAdminUpdateForm):
    class Meta(AbstractAnalysisAdminUpdateForm.Meta):
        model = RNASeqModel


@admin.register(RNASeqModel)
class RNASeqModelAdmin(AbstractAnalysisAdmin):

    form = RNASeqAdminUpdateForm
    list_display = (
        *AbstractAnalysisAdmin.list_display,
        "genome_aligner",
    )
