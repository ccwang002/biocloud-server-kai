import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.html import mark_safe
from django.utils.translation import ugettext

from data_sources.models import DataSource
from .forms import ExperimentCreateForm
from .models import Condition

@login_required
def create_new_experiment(request):
    if request.method == 'POST':
        form = ExperimentCreateForm(
            data=request.POST, files=request.FILES,
        )
        extra_data = json.loads(request.POST.get('extraData', {}))
        conditions = extra_data.get('conditions', [])
        condition_labels = {
            cond['_uid']: cond['label']
            for cond in conditions
        }
        condition_labels['0'] = '(All)'
        num_condition_created = extra_data.get('numConditionCreated', 0)
        labelled_data_sources = extra_data.get('dataSources', [])
        if form.is_valid():
            # Create the experiment first
            experiment = form.save(commit=False)
            experiment.owner = request.user
            experiment.save()
            # Create all conditions of the experiment
            condition_objects = [
                Condition(
                    experiment=experiment,
                    condition=condition_labels[ds['condition']],
                    data_source=DataSource.objects.get(
                        pk=ds['data_source_pk']
                    ),
                    sample_name=ds['sample'],
                    strand=ds['metadata'].get('strand', ''),
                )
                for ds in labelled_data_sources if ds['selected']
            ]
            Condition.objects.bulk_create(condition_objects)
            messages.success(request, ugettext(
                'You have created a new experiment {name}'.format(
                    name=experiment.name
                ),
            ))
            return redirect('index')
        # if the form is invalid, remain this form instance and pass to the
        # render() at the end (all errors has been generated during the
        # form.is_valid() check.
    else:
        form = ExperimentCreateForm()
        # get user's sample with metadata
        data_sources = request.user.data_sources.all()
        labelled_data_sources = [
            {
                'data_source_pk': ds.pk,
                'file_path': ds.file_path,
                'file_type': ds.file_type,
                'sample': ds.sample_name,
                'metadata': ds.metadata,
                'condition': '0',
                'selected': False,
            }
            for ds in data_sources
        ]
        conditions = []
        num_condition_created = len(conditions)
    return render(request, 'experiments/new.html', {
        'form': form,
        'data_source_json': mark_safe(json.dumps(labelled_data_sources)),
        'conditions_json': mark_safe(json.dumps(conditions)),
        'num_condition_created': num_condition_created,
    })

