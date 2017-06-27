from django.db import models
from django.utils.translation import ugettext_lazy as _

from analyses.models import AbstractAnalysisModel
from analyses.fields import StageStatusField
from analyses import pipelines
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
    ),
    ToolSpec(
        "Cufflinks", "2.2.1",
        _(
            "Transcriptome assembly and differential expression analysis "
            "for RNA-Seq."
        ),
        "http://cole-trapnell-lab.github.io/cufflinks/"
    )
])

SUPPORTED_ALIGNERS = [
    "Tophat",
    "STAR",
]


@pipelines.register
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

    # Alignment options for each aligner
    # Tophat
    tophat_max_multihits = models.PositiveIntegerField(
        default=20,
        blank=True,
        verbose_name='Max multi-hits',
        help_text=_(
            "Instructs TopHat to allow up to this many alignments to the "
            "reference for a given read, and choose the alignments based "
            "on their alignment scores if there are more than this number. "
            "The default is 20 for read mapping. If there are more alignments "
            "with the same score than this number, TopHat will randomly "
            "report only this many alignments."
        )
    )
    TOPHAT_LIBRARY_TYPES = [
        ("FR-UNSTRANDED", _("Unstranded (Ex. Standard illumnia)")),
        ("FR-FIRSTSTRAND", _("First-stranded (Ex. Stranded specific sequcing, dUTP, NSR, NNSR)")),
        ("FR-SECONDSTRAND", _("Second-stranded (Ex. Standard SOLiD)")),
    ]
    tophat_library_type = models.CharField(
        choices=TOPHAT_LIBRARY_TYPES,
        max_length=16,
        default=TOPHAT_LIBRARY_TYPES[0][0],
        blank=True,
        verbose_name="Library type",
        help_text=_(
            "Consider supplying library type options below to select the "
            "correct RNA-seq protocol. The default is unstranded."
        ),
    )

    # STAR
    star_separate_unmapped_reads = models.BooleanField(
        default=False,
        verbose_name=_("separate unmapped reads"),
        help_text=_(
            "Put unmapped or partially mapped (one of the paired reads is "
            "mapped) in a separate FASTA/Q file."
        ),
    )

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('rna_seq_detail', kwargs={'pk': str(self.id)})

    class Meta:
        verbose_name = "RNA-Seq analysis"
        verbose_name_plural = "RNA-Seq analyses"

    def generate_analysis_info(self):
        # Get the analysis_info from base classs
        # Including data_sources, conditions, and etc.
        analysis_info = super().generate_analysis_info()

        # Add RNA-seq specific analysis_info
        parameters = {
            'quality_check': self.quality_check,
            'genome_aligner': self.genome_aligner,
            'tophat_max_multihits': self.tophat_max_multihits,
            'tophat_library_type': self.tophat_library_type,
            'star_separate_unmapped_reads': self.star_separate_unmapped_reads,
        }
        # TODO: Instead of outputting all parameters,
        # we can output those that are actually used.
        # For example, if the analysis uses STAR,
        # ignore all Tophat settings.
        # if self.genome_aligner.startswith('Tophat'):
        # else:

        # Overwrite existed analysis_info dic
        analysis_info['parameters'] = {
            **analysis_info['parameters'],
            **parameters,
        }
        return analysis_info


class RNASeqExeDetail(models.Model):
    analysis = models.OneToOneField(
        RNASeqModel, related_name='execution_detail',
        primary_key=True, parent_link=True,
    )

    stage_qc = StageStatusField()
    stage_alignment = StageStatusField()
    stage_cufflinks = StageStatusField()
    stage_cuffdiff = StageStatusField()

    def __str__(self):
        return 'Detail of %s' % self.analysis.name

    class Meta:
        verbose_name = "RNA-Seq detail"
        verbose_name_plural = "RNA-Seq detail"
