from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext
from django.views.generic import TemplateView

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


class DashboardAdminView(PermissionRequiredMixin, TemplateView):
    permission_required = 'is_staff'
    template_name = 'dashboard/admin.html'
    raise_exception = True
    permission_denied_message = 'User of current session is not an admin'


