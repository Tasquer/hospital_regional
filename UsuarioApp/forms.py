from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Position
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
        ]


class UserCreateForm(UserCreationForm, UserUpdateForm):
    password1 = forms.PasswordInput()
    password2 = forms.PasswordInput()

    class Meta:
        model = User
        fields = UserUpdateForm.Meta.fields + ["password1", "password2"]

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        validate_password(password1)
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match")

        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    image = forms.ImageField(
        label="Imagen",
        widget=forms.FileInput(attrs={"class": "hidden", "id": "id_image"}),
        required=False,
    )

    class Meta:
        model = Profile
        fields = ["image"]

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image and image.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                "El tamaño del archivo de imagen no debe exceder los 5 MB."
            )
        return image


class ProfileCreateForm(ProfileUpdateForm):
    position_FK = forms.ModelChoiceField(
        label="Cargo",
        queryset=Position.objects.exclude(pk=1),
        widget=forms.Select(
            attrs={
                "class": "bg-white focus:outline-none border border-gray-300 rounded-lg py-2 px-4 block w-full appearance-none leading-normal text-gray-700 mb-3"
            }
        ),
    )

    class Meta(ProfileUpdateForm.Meta):
        fields = ProfileUpdateForm.Meta.fields + ["position_FK"]
