from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import BaseCreateView, ProcessFormView


from data_sources.forms import DataSourceDiscoveryFormSet
from data_sources.models import DataSource
from users.forms import UserProfileUpdateForm


@login_required
def dashboard_home(request):
    logout_next = reverse('login')
    return render(request, 'dashboard/welcome_page.html', {
        'logout_next': logout_next,
    })


@login_required
def dashboard_profile_update(request):
    logout_next = reverse('index')
    if request.method == 'POST':
        form = UserProfileUpdateForm(
            data=request.POST, files=request.FILES,
            instance=request.user,
        )
        if form.is_valid():
            form.save()
            messages.success(request, ugettext(
                'Your profile has been updated successfully.',
            ))
            return redirect('dashboard_home')
    else:
        form = UserProfileUpdateForm(instance=request.user)
    return render(request, 'dashboard/profile.html', {
        'form': form, 'logout_next': logout_next,
    })


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


class DiscoverDataSourceListView(
    LoginRequiredMixin, ProcessFormView, TemplateView
):

    template_name = 'dashboard/data_source_discovery.html'
    form_class = DataSourceDiscoveryFormSet

    def get_initial(self):
        owner = self.request.user
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
        return [
            {'file_path': pth, 'sample_name': '', 'file_type': ''}
            for pth in sorted(all_file_paths - existed_file_paths)
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        formset = self.form_class(initial=self.get_initial())
        context['formset'] = formset
        return context

