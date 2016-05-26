from django.db import models
from pipelines.models import AbstractPipelineModel
from data_sources.models import DataSource


class RNASeqModel(AbstractPipelineModel):

    fastq_sources = models.ManyToManyField(
        DataSource,
        related_name='+',
    )
