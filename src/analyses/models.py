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


class GenomeReference(models.Model):

    identifier = models.CharField(
        primary_key=True,
        max_length=64,
        help_text=_(
            "Identifier for the genome reference. Ex. hg19, GRCh38.p5."
        ),
    )

    SOURCE_CHOICES = [
        ("NCBI", _("NCBI")),
        ("ENSEMBL", _("Ensembl")),
        ("UCSC", _("UCSC")),
        ("OTHER", _("Other or Custom"))
    ]
    source = models.CharField(
        max_length=16,
        choices=SOURCE_CHOICES,
        help_text=_(
            "The institution that maintains the genome reference."
        ),
    )

    organism = models.CharField(
        max_length=512,
        help_text=_(
            "Species description using the Linnaean taxonomy naming system. "
            "Ex. Homo sapiens; Mus musculus."
        ),
    )

    newer_reference = models.ForeignKey(
        "self",
        blank=True, null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("newer version"),
        help_text=_(
            "If new version of the genome reference of the same "
            "organism and source exists, link the reference here. "
            "For example, UCSC mm9 can set its newer reference to UCSC mm10."
        ),
    )

    def __str__(self):
        return "{0.identifier} ({0.source})".format(self)


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

    genome_reference = models.ForeignKey(
        GenomeReference,
        on_delete=models.CASCADE,
        related_name="experiments",
        help_text=_(
            "The genome reference in use."
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
