from collections import namedtuple


AVAILABLE_PIPELINES = []
AVAILABLE_PIPELINE_MODELS = []

Pipeline = namedtuple('Pipeline', ['name', 'description', 'url'])


def register_view(cls):
    """Register a new pipeline view"""
    AVAILABLE_PIPELINES.append(
        Pipeline(
            cls.analysis_type,
            cls.analysis_description,
            cls.analysis_create_url
        )
    )
    return cls


def register(cls):
    """Register a new pipeline's django model"""
    AVAILABLE_PIPELINE_MODELS.append(cls)
    return cls
