import subprocess as sp
from pathlib import Path
import time
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext, ugettext_lazy as _

from .models import RNASeqModel
from analyses.tasks import cd
from analyses.models import ExecutionStatus, StageStatus

FASTQC_BIN = str(Path('~/miniconda3/envs/rnaseq/bin/fastqc').expanduser())


def update_stage(job_detail, stage_name, new_status):
    setattr(job_detail, stage_name, new_status.name)
    job_detail.save(update_fields=[stage_name])


def run_fastqc(job: RNASeqModel, analysis_info):
    data_sources = analysis_info['data_sources']
    with cd(str(job.result_dir)):
        for ds in data_sources:
            ds_pth, ds_info = next(iter(ds.items()))
            ds_pth = Path(ds_pth)
            ds_dir = Path('fastqc/{}'.format(ds_pth.stem))
            if not ds_dir.exists():
                ds_dir.mkdir()
            p = sp.run([
                FASTQC_BIN,
                '-o', str(ds_dir),
                str(ds_pth)
            ])
            p.check_returncode()
            if p.returncode:
                return p.returncode
    return 0


def run_pipeline(job_pk, job_url):
    job = RNASeqModel.objects.get(pk=job_pk)
    job_detail = job.execution_detail
    job.execution_status = ExecutionStatus.RUNNING.name
    job.save()
    analysis_info = job.generate_analysis_info()

    # Stage QC:
    fastqc_dir = job.result_dir.joinpath('fastqc')
    if not fastqc_dir.exists():
        fastqc_dir.mkdir()
    if job.quality_check:
        update_stage(job_detail, 'stage_qc', StageStatus.RUNNING)
        returncode = run_fastqc(job, analysis_info)
        if returncode:
            update_stage(job_detail, 'stage_qc', StageStatus.FAILED)
            # TODO: short circuit failure and notification
            # End the pipeline now and notify user about why
        else:
            update_stage(job_detail, 'stage_qc', StageStatus.SUCCESSFUL)
    else:
        update_stage(job_detail, 'stage_qc', StageStatus.SKIPED)

    # simulate running alignment
    update_stage(job_detail, 'stage_alignment', StageStatus.RUNNING)
    time.sleep(5)
    update_stage(job_detail, 'stage_alignment', StageStatus.SUCCESSFUL)

    # simluate running cufflinks
    update_stage(job_detail, 'stage_cufflinks', StageStatus.RUNNING)
    time.sleep(5)
    update_stage(job_detail, 'stage_cufflinks', StageStatus.SUCCESSFUL)

    # intentionally skip stage_cuffdiff

    # generating report
    job_report = job.report
    sp.run([
        'bc_report',
        '-p', 'bc_pipelines.rna_seq.report.RNASeqReport',
        str(job.result_dir),
        str(job_report.full_path)
    ])

    # pipeline ends
    job.date_finished = timezone.now()
    job.execution_status = ExecutionStatus.SUCCESSFUL.name
    job.save()

    # sending notification email
    user = job.owner
    context = {
        'user': user,
        'job_url': job_url,
        'job': job,
        'type': job._meta.verbose_name,
        'name': job.name,
        'status': job.execution_status,
    }
    message = render_to_string(
        'rna_seq/analysis_complete_email.txt', context,
    )
    send_mail(
        ugettext(
            '[BioCloud] {type}: {name} has been complete ({status})'
            .format(**context)
        ),
        message,
        None,           # sender
        [user.email]    # receiver
    )
