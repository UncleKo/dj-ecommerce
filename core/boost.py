from django.contrib.auth.views import RedirectURLMixin
from django.utils.http import url_has_allowed_host_and_scheme


# Loginページ以外でもリンクURLにnextを付けて前のページに戻れるようにする。
class DynamicRedirectMixin(RedirectURLMixin):

    redirect_field_name = 'next'

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or super().get_success_url()

    def get_redirect_url(self):
        """Return the user-originating redirect URL if it's safe."""
        redirect_to = self.request.POST.get(
            self.redirect_field_name,
            self.request.GET.get(self.redirect_field_name, '')
        )
        url_is_safe = url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ''


# def redirect_to_next(self):

#     redirect_field_name = 'next'
#     redirect_to = self.request.POST.get(
#         self.redirect_field_name,
#         self.request.GET.get(self.redirect_field_name, '')
#     )
#     url_is_safe = url_has_allowed_host_and_scheme(
#         url=redirect_to,
#         allowed_hosts=self.get_success_url_allowed_hosts(),
#         require_https=self.request.is_secure(),
#     )
#     return redirect(redirect_to) if url_is_safe else ''
