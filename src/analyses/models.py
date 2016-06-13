from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from core.utils import ChoiceEnum
from experiments.models import Experiment


class ExecutionStatus(ChoiceEnum):
    INIT = _("Initiating")
    QUEUEING = _("Waiting in the queue")
    RUNNING = _("Running")
    SUCCESSFUL = _("Successful")
    FAILED = _("Failed")


class AbstractAnalysisModel(models.Model):

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analyses',
    )

    name = models.CharField(max_length=255)

    description = models.TextField(
        blank=True,
        verbose_name=_("description"),
        help_text=_(
            "Description about this analysis. Can be written in "
            "<a href=\"http://commonmark.org/\">Markdown</a> markup language."
        ),
    )

    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name='experiments',
        help_text=_(
            "Previously defined experiment, which contains how sources are "
            "grouped as samples and conditions."
        ),
    )

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
        get_latest_by = ("date_finished", "date_created")
        ordering = ("-date_created", )
