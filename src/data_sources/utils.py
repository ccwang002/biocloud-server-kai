from pathlib import Path
import re


def guess_data_source(file_path):
    """Guess data source info based on file path.

    It first detects the file suffix and delegates to the proper
    data source info extractor.

    Args:
        file_path (str): file path to the data source

    Returns:
        dict: initial data to create the DataSource object
    """
    pth = Path(file_path)
    initial = {
        'file_path': file_path,
        'sample_name': '',
        'file_type': '',
    }
    if pth.suffix in ['.fastq', '.fq']:
        initial['file_type'] = 'FASTQ'
        initial = complete_fastaq_info(file_path, initial)
    elif pth.suffix in ['.fasta', '.fa']:
        initial['file_type'] = 'FASTA'
        initial = complete_fastaq_info(file_path, initial)
    return initial


def complete_fastaq_info(file_path, initial):
    """Guess FASTA/Q data source info based on file path.

    Args:
        file_path (str): file path to the data source
        initial (dict): initial data

    Returns:
        dict: initial data to create the DataSource object
    """
    pth = Path(file_path)
    initial = initial.copy()
    sample_regex = (
        r'^(?P<sample>\w+)_'       # sample name
        r'[rR]?(?P<strand>[12])$'  # read 1 or read 2 (pair-end)
                                   # can be R1 / R2
    )
    match = re.match(sample_regex, pth.stem)
    if match:
        initial['sample_name'] = match.group('sample')
        initial['metadata'] = {}
        initial['metadata']['paired'] = True
        initial['metadata']['strand'] = int(match.group('strand'))
    return initial


