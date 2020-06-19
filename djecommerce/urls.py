from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
# from django.contrib.auth import views as auth_views
from django.urls import path, include
from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('core.urls', namespace='core')),
    # path('login/', auth_views.LoginView.as_view(template_name='user/login.html'), name='login')
    # path('edit-profile/', user_views.edit_profile, name='edit-profile')
    path('edit-profile/user/<int:pk>/',
         user_views.ProfileUpdateView.as_view(), name='edit-profile')
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
