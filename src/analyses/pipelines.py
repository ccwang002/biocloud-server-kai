from collections import namedtuple


AVAILABLE_PIPELINES = []

Pipeline = namedtuple('Pipeline', ['name', 'description', 'url'])


def register(cls):
    """Register a new pipeline view"""
    AVAILABLE_PIPELINES.append(
        Pipeline(
            cls.analysis_type,
            cls.analysis_description,
            cls.analysis_create_url)
    )
    return cls
