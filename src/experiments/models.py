from django.db import models
from django.utils.translation import ugettext_lazy as _

from data_sources.models import DataSource


class Experiment(models.Model):
    """A model to store relations between data sources.

    """
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


class Condition(models.Model):
    """Intermediary model to connect experiments and data sources.

    """
    STRAND_CHOICES = (
        ("1", _('R1 (forward)')),
        ("2", _('R2 (reversed)')),
    )

    experiment = models.ForeignKey(
        Experiment,
        related_name="data_source_conditions",
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
