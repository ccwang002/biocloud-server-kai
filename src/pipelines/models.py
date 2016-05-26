from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from core.utils import ChoiceEnum


class ExecutionStatus(ChoiceEnum):
    INIT = "Initiating"
    QUEUEING = "Waiting in the queue"
    RUNNING = "Running"
    SUCCESSFUL = "Successful"
    FAILED = "Failed"


class AbstractPipelineModel(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='analyses'
    )
    analysis_name = models.CharField(max_length=255)
    date_created = models.DateTimeField(
        verbose_name=_('date created'),
        default=timezone.now,
        editable=False,
    )
    date_finished = models.DateTimeField(
        verbose_name=_('date finished'),
        blank=True,
        default=None,
        editable=False,
    )
    execution_status = models.CharField(
        choices=ExecutionStatus.choices(),
        max_length=63,
        default=ExecutionStatus.INIT.name,
        editable=False,
    )

    class Meta:
        abstract = True
