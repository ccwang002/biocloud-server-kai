from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.signing import BadSignature
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from core.utils import ChoiceEnum
from core.signing import fixed_loads, fixed_dumps
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

    release_date = models.DateField(
        blank=True, null=True,
        verbose_name=_('Release date'),
        help_text=_(
            "The date this genome reference is released."
        )
    )

    class Meta:
        ordering = ("organism", "source", "-release_date",)
        get_latest_by = "release_date"

    def __str__(self):
        return "{0.identifier} ({0.source})".format(self)


class ReportQuerySet(models.QuerySet):

    def get_with_auth_key(self, auth_key):
        """
        Obtain the report object based on given auth_key

        Args:
              auth_key (str): authentication string
        """
        # decode the auth_key
        try:
            auth_email, auth_number, report_pk = fixed_loads(auth_key)
        except (BadSignature, ValueError):
            raise self.model.DoesNotExist

        # get the report object
        report = self.get(pk=report_pk)
        if not report.is_analysis_attached():
            raise self.model.DoesNotExist

        # check if auth_number mismatches user's current auth_number
        # auth_email is also checked so other user cannot forget the auth key
        owner = report.analysis.owner
        if not (
            owner.email == auth_email and
            owner.auth_number == auth_number
        ):
            raise self.model.DoesNotExist
        return report


class Report(models.Model):

    date_created = models.DateTimeField(
        verbose_name=_('date created'),
        default=timezone.now,
        editable=False,
    )

    is_public = models.BooleanField(
        verbose_name=_('is public'),
        help_text=_(
            "Whether the access link is publicly visible."
        ),
        default=False,
    )

    objects = ReportQuerySet.as_manager()

    class Meta:
        get_latest_by = "date_created"
        ordering = ("-date_created", )

    def is_analysis_attached(self):
        """Check if the report has been attached to an analysis"""
        try:
            self.analysis
        except ObjectDoesNotExist:
            return False
        return True

    @cached_property
    def auth_key(self):
        user = self.analysis.owner  # will throw ObjectDoesNotExist
        return fixed_dumps(
            [user.email, user.auth_number, self.pk]
        )

    def __str__(self):
        return str(self.pk)


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
        blank=True, null=True,
        default=None,
        editable=False,
    )

    execution_status = models.CharField(
        choices=ExecutionStatus.choices(),
        max_length=63,
        default=ExecutionStatus.INIT.name,
        editable=False,
    )

    report = models.OneToOneField(
        Report,
        blank=True, null=True,
        default=None,
        related_name='analysis',
    )

    class Meta:
        abstract = True
        get_latest_by = ("date_finished", "date_created")
        ordering = ("-date_created", )
