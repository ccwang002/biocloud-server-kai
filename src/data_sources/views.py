from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView
from django.views.decorators.http import require_http_methods

from .models import DataSource
from .forms import DataSourceFormSet


class UserDataSourceListView(LoginRequiredMixin, ListView):

    model = DataSource
    template_name = 'dashboard/data_source_validation.html'

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_data_source_dir'] = \
            settings.BIOCLOUD_DATA_SOURCES_DIR.joinpath(
                str(self.request.user.pk)
            )
        return context


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
            return redirect('dashboard_data_sources')
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
        initial_data = [
            {
                'file_path': pth,
                'sample_name': '',
                'file_type': '',
            }
            for pth in sorted(all_file_paths - existed_file_paths)
        ]
        formset = DataSourceFormSet(
            initial=initial_data,
            form_kwargs={'owner': owner},
        )
    return render(request, 'dashboard/data_source_discovery.html', {
        'formset': formset
    })

