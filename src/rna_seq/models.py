from django.db import models
from analyses.models import AbstractAnalysisModel
from data_sources.models import DataSource


class RNASeqModel(AbstractAnalysisModel):

    quality_check = models.BooleanField(
        default=True,
        help_text='Generate a quality check report based on FastQC',
    )

    trim_adapter = models.BooleanField(
        default=False,
        help_text="Trim illumina 3' adapter",
    )

    rm_duplicate = models.BooleanField(
        default=False,
        verbose_name='Remove PCR duplication',
        help_text=(
            'Remove PCR duplication based on the genome alignment of reads '
            'during sequencing using Picard'
        ),
    )
