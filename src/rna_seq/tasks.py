import time
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext, ugettext_lazy as _

from .models import RNASeqModel
from analyses.tasks import EXE, cd
from analyses.models import ExecutionStatus, StageStatus


def update_stage(job_detail, stage_name, new_status):
    setattr(job_detail, stage_name, new_status.name)
    job_detail.save(update_fields=[stage_name])


def run_pipeline(job_pk, job_url):
    job = RNASeqModel.objects.get(pk=job_pk)
    job_detail = job.execution_detail
    job.execution_status = ExecutionStatus.RUNNING.name
    job.save()

    # simulate skipping qc
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
