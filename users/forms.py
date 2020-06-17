from django import forms
from django.contrib.auth.models import User


class ProfileUpdateForm(forms.ModelForm):
    # email = forms.EmailField(label="Eメール")

    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        }),
        required=True
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        }),
        required=True
    )

    email = forms.EmailField(
        label="Eメール",
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
