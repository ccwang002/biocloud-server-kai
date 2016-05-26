from django import forms
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from core.choices import ChoiceEnum


class ExecutionStatus(ChoiceEnum):
    INIT = _("Initiating")
    QUEUEING = _("Waiting in the queue")
    RUNNING = _("Running")
    SUCCESSFUL = _("Successful")
    FAILED = _("Failed")


class AbstractPipelineModel(models.Model):

    analysis_name = models.CharField(max_length=256)
    analysis_type = models.CharField()
    date_created = models.DateTimeField(
        verbose_name=_('date created'),
        default=timezone.now,
        editable=False,
    )
    date_finished = models.DateTimeField(
        verbose_name=_('date finished'),
        blank=True,
        editable=False,
    )
    execution_status = models.CharField(
        choices=ExecutionStatus.choices(),
        required=True,
        default=ExecutionStatus.INIT.name
    )
