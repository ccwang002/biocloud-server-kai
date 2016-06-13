from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from data_sources.models import DataSource


class Experiment(models.Model):
    """A model to store relations between data sources.

    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='experiments',
    )

    name = models.CharField(
        max_length=512,
        verbose_name=_("name"),
    )

    description = models.TextField(
        blank=True,
        verbose_name=_("description"),
        help_text=_(
            "Description about this experiment. Can be written in "
            "<a href=\"http://commonmark.org/\">Markdown</a> markup language."
        ),
    )

    data_sources = models.ManyToManyField(
        DataSource, through="Condition",
    )

    date_created = models.DateTimeField(
        verbose_name=_('date created'),
        default=timezone.now,
        editable=False,
    )

    @property
    def sample_names(self):
        """Return all distinct sample names"""
        return (
            self.conditions
                .values_list('sample_name', flat=True)
                .distinct()
                .order_by('sample_name')
        )

    @property
    def condition_names(self):
        """Return all distinct condition names"""
        return (
            self.conditions
                .values_list('condition', flat=True)
                .distinct()
                .order_by('condition')
        )

    def __str__(self):
        return (
            '{owner:s}\'s {name:s} '
            '(involving {num_sources:d} data sources '
            'grouped as {num_sample:d} samples '
            'and {num_condition:d} conditions)'
            .format(
                owner=self.owner.name,
                name=self.name,
                num_sample=len(self.sample_names),
                num_sources=self.conditions.count(),
                num_condition=len(self.condition_names),
            )
        )

    class Meta:
        get_latest_by = "date_created"
        ordering = ['-date_created']


class Condition(models.Model):
    """Intermediary model to connect experiments and data sources.

    """
    STRAND_CHOICES = (
        ("1", _('R1 (forward)')),
        ("2", _('R2 (reversed)')),
    )

    experiment = models.ForeignKey(
        Experiment,
        related_name="conditions",
        on_delete=models.CASCADE,
    )

    condition = models.CharField(
        max_length=512,
        help_text=_("Name of the condition")
    )

    data_source = models.ForeignKey(
        DataSource,
        related_name="exp_conditions",
        on_delete=models.CASCADE,
    )

    sample_name = models.CharField(
        max_length=512,
        blank=True,
        verbose_name=_("sample name"),
    )

    strand = models.CharField(
        choices=STRAND_CHOICES,
        max_length=4,
        blank=True,
        verbose_name=_("read strand"),
        help_text=_(
            "Strand for the sequencing type of data sources. Usually the file "
            "is sufficed with R1 (forward) or R2 (reversed). If the data "
            "source is not stranded or not of sequencing type, leave this "
            "field blank."
        )
    )

    class Meta:
        unique_together = ("experiment", "condition", "data_source")

    def __str__(self):
        return (
            '{condition:s} ({source_file_path:} of {sample_name:s})'
            .format(
                condition=self.condition,
                sample_name=self.sample_name,
                source_file_path=self.data_source.get_rel_file_path(),
            )
        )
