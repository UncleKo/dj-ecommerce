from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from django.contrib.auth.models import User
from django.views.generic import UpdateView  # , DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin  # UserPassesTestMixin
from .forms import ProfileUpdateForm
from core.boost import DynamicRedirectMixin


class ProfileUpdateView(LoginRequiredMixin, DynamicRedirectMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = 'edit-profile.html'
    success_url = reverse_lazy('core:checkout')
    # success_url = reverse_lazy('profile')


# @login_required
# def edit_profile(request):
#     if request.method == 'POST':
#         u_form = ProfileUpdateForm(request.POST, instance=request.user)
#     #   p_form = ProfileUpdateForm(request.POST,
#     #                              request.FILES,
#     #                              instance=request.user.profile)
#         if u_form.is_valid():
#             # and p_form.is_valid():
#             u_form.save()
#     #     p_form.save()
#         messages.success(request, 'Your account has been updated!')
#         # to avoid re-post request to the page(if reached to reander it will re-post)
#         return redirect('edit-profile')
#     else:
#         u_form = ProfileUpdateForm(instance=request.user)
#         # p_form = ProfileUpdateForm(instance=request.user.profile)

#         context = {
#             'form': u_form
#             # 'p_form': p_form
#         }

#     return render(request, 'edit-profile.html', context)
