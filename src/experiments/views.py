import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.html import mark_safe
from django.utils.translation import ugettext

from .forms import ExperimentCreateForm


@login_required
def create_new_experiment(request):
    if request.method == 'POST':
        form = ExperimentCreateForm(
            data=request.POST, files=request.FILES,
        )
        if form.is_valid():
            experiment = form.save(commit=False)
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
    data_source_json = mark_safe(json.dumps([
        {
            'data_source_pk': ds.pk,
            'file_path': ds.file_path,
            'file_type': ds.file_type,
            'sample': ds.sample_name,
            'metadata': ds.metadata,
            'condition': -1,
            'selected': False,
        }
        for ds in data_sources
    ]))
    return render(request, 'experiments/new.html', {
        'form': form,
        'data_source_json': data_source_json
    })

