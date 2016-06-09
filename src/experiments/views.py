from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
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

    return render(request, 'experiments/new.html', {
        'form': form,
    })

