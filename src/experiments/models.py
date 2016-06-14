from collections import namedtuple, OrderedDict, defaultdict

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
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

    @cached_property
    def sample_names(self):
        """Return all distinct sample names"""
        return (
            self.conditions
                .values_list('sample_name', flat=True)
                .distinct()
                .order_by('sample_name')
        )

    @cached_property
    def condition_names(self):
        """Return all distinct condition names

        Note that condition (ALL) is ignored.
        """
        return (
            self.conditions
                .filter(condition_order__gt=0)
                .values_list('condition', flat=True)
                .distinct()
                .order_by('condition_order')
        )

    @cached_property
    def group_data_sources(self):
        """
        Return dict of condition to samples to data sources.
        """
        grouped_data_sources = OrderedDict()

        conditions = (
            self.conditions
                .select_related('data_source')
                .order_by("condition_order", "sample_name")
        )
        for condition in conditions:
            cond_lab = condition.condition_label
            sample = condition.sample_name
            if cond_lab not in grouped_data_sources:
                grouped_data_sources[cond_lab] = defaultdict(list)
            grouped_data_sources[cond_lab][sample].append(condition)
        # If we do not disable the default_factory, it cannot be rendered
        # correctly in templates.
        # Ref: http://stackoverflow.com/a/12842716
        for samples in grouped_data_sources.values():
            samples.default_factory = None
        return grouped_data_sources

    def get_absolute_url(self):
        return reverse('detail_experiment', kwargs={'pk': self.pk})

    @cached_property
    def summary(self):
        return (
            '{name:s} was created by {owner:s} involving '
            '{num_sources:d} data sources. '
            'It defined {num_sample:d} samples: {samples:s}, '
            'and defined {num_condition:d} conditions: {conditions:s}.'
            .format(
                owner=self.owner.name,
                name=self.name,
                num_sample=len(self.sample_names),
                samples=', '.join(self.sample_names),
                num_sources=self.conditions.count(),
                conditions=', '.join(self.condition_names),
                num_condition=len(self.condition_names),
            )
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


ConditionLabel = namedtuple('ConditionLabel', ['order', 'label'])


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
        help_text=_("Name of the condition. (All) is a special condition "
                    "which implies this data source appears in every "
                    "condition.")
    )

    condition_order = models.IntegerField(
        help_text=_("Order of the condition. 0 should always represent the "
                    "special condition (All).")
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

    @property
    def condition_label(self):
        """Return a ConditionLabel tuple"""
        return ConditionLabel(self.condition_order, self.condition)
