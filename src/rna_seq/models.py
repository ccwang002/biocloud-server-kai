from django.db import models
from django.utils.translation import ugettext_lazy as _

from analyses.models import AbstractAnalysisModel
from analyses.tool_specs import ToolSpec, ToolSet
from data_sources.models import DataSource


ALL_TOOLS_IN_USE = ToolSet([
    ToolSpec(
        "FastQC", "0.11.5",
        _("A quality control tool for high throughput sequence data."),
        "http://www.bioinformatics.babraham.ac.uk/projects/fastqc/",
    ),
    ToolSpec(
        "Picard", "2.4.1",
        _(
            "A set of command line tools (in Java) for manipulating "
            "high-throughput sequencing (HTS) data and formats such as "
            "SAM/BAM/CRAM and VCF."
        ),
        "http://broadinstitute.github.io/picard/"
    ),
    ToolSpec(
        "Tophat", "2.1.1",
        _("A genome aligner"),
        "https://ccb.jhu.edu/software/tophat/index.shtml",
    ),
    ToolSpec(
        "STAR", "2.5.0",
        _("A genome aligner"),
        "https://github.com/alexdobin/STAR",
    )
])

SUPPORTED_ALIGNERS = [
    "Tophat",
    "STAR",
]


class RNASeqModel(AbstractAnalysisModel):

    quality_check = models.BooleanField(
        default=True,
        help_text=_(
            'Generate a quality check report based on FastQC',
        ),
    )

    trim_adapter = models.BooleanField(
        default=False,
        help_text=_(
            "Trim illumina 3' adapter. "
            "<strong>Currently no support for this option.</strong>",
        ),
    )

    rm_duplicate = models.BooleanField(
        default=False,
        verbose_name='Remove PCR duplication',
        help_text=_(
            "Remove PCR duplication based on the genome alignment of reads "
            "during sequencing using "
            "<a href=\"http://broadinstitute.github.io/picard/\">Picard</a>. "
            "<strong>Currently no support for this option.</strong>"
        ),
    )

    genome_aligner = models.CharField(
        choices=ALL_TOOLS_IN_USE.subset(SUPPORTED_ALIGNERS).db_choices,
        max_length=128,
    )
