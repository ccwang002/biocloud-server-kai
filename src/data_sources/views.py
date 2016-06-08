from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, UpdateView
from django.views.decorators.http import require_http_methods

from .models import DataSource
from .forms import DataSourceFormSet, DataSourceUpdateForm
from .utils import complete_fastaq_info, guess_data_source


class UserDataSourceListView(LoginRequiredMixin, ListView):

    model = DataSource
    template_name = 'data_sources/list.html'

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_data_source_dir'] = \
            settings.BIOCLOUD_DATA_SOURCES_DIR.joinpath(
                str(self.request.user.pk)
            )
        return context


class UserDataSourceUpdateView(LoginRequiredMixin, UpdateView):

    model = DataSource
    form_class = DataSourceUpdateForm
    template_name = 'data_sources/update.html'
    success_url = reverse_lazy('list_data_sources')

    def get_initial(self):
        initial = super().get_initial()
        data_source = self.object
        if not data_source.sample_name and not data_source.metadata and \
                data_source.file_type in ['FASTA', 'FASTQ']:
            return complete_fastaq_info(data_source.file_path, initial)
        return initial


@require_http_methods(["GET", "POST"])
@login_required
def discover_data_source(request):
    if request.method == 'POST':
        formset = DataSourceFormSet(
            request.POST, request.FILES,
            form_kwargs={'owner': request.user},
        )
        if formset.is_valid():
            # save the new data sources
            new_data_sources = []
            for form in formset:
                data_source = form.save()
                new_data_sources.append(data_source.file_path)
            messages.add_message(
                request,
                messages.SUCCESS,
                _('Successfully added data sources: %(data_sources)s') % {
                    'data_sources': ', '.join(new_data_sources)
                },
            )
            return redirect('list_data_sources')
    else:
        # Discover new data sources
        owner = request.user
        owner_data_source_pth = settings.BIOCLOUD_DATA_SOURCES_DIR.joinpath(
            str(owner.pk)
        )
        all_file_paths = set(
            p.relative_to(owner_data_source_pth).as_posix()
            for p in owner_data_source_pth.iterdir()
            if p.name not in ['.DS_Store'] and not p.name.startswith('.')
        )
        existed_file_paths = set(
            owner.data_sources.values_list('file_path', flat=True)
        )
        initial_data = []
        for file_path in sorted(all_file_paths - existed_file_paths):
            initial = guess_data_source(file_path)
            initial_data.append(initial)
        formset = DataSourceFormSet(
            initial=initial_data,
            form_kwargs={'owner': owner},
        )
    return render(request, 'data_sources/discovery.html', {
        'formset': formset
    })

