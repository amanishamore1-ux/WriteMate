from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import (
    AuthenticationForm,
    UsernameField,
    PasswordResetForm,
    PasswordChangeForm,
    SetPasswordForm
)
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password
from .models import UserProfile

from .models import BlogPost, Comment


# ===============================
# REGISTER USER
# ===============================
class RegisterUserForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2:
            if password != password2:
                raise forms.ValidationError("Passwords do not match")

            password_validation.validate_password(password)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


# ===============================
# LOGIN FORM
# ===============================
class LoginForm(AuthenticationForm):
    username = UsernameField(
        widget=forms.TextInput(
            attrs={'autofocus': True, 'class': 'form-control'}
        )
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'current-password',
                'class': 'form-control'
            }
        )
    )


# ===============================
# PASSWORD CHANGE
# ===============================
class MyPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label=_("Old Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control'}
        )
    )

    new_password1 = forms.CharField(
        label=_("New Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control'}
        ),
        help_text=password_validation.password_validators_help_text_html()
    )

    new_password2 = forms.CharField(
        label=_("Confirm New Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control'}
        )
    )


# ===============================
# PASSWORD RESET
# ===============================
class MyPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={'class': 'form-control'}
        )
    )


class MySetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=_("New Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control'}
        ),
        help_text=password_validation.password_validators_help_text_html()
    )

    new_password2 = forms.CharField(
        label=_("Confirm New Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control'}
        )
    )


# ===============================
# BLOG POST FORM
# ===============================
class BlogPostForm(forms.ModelForm):

    # 🔥 NEW FIELD
    new_category = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Or create new category...'
        })
    )

    class Meta:
        model = BlogPost
        fields = [
            'title',
            'category',
            'new_category',   # 🔥 ADD THIS
            'featured_image',
            'video',
            'content',
            'status'
        ]

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),

            'category': forms.Select(attrs={'class': 'form-control'}),

            'featured_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),

            'video': forms.ClearableFileInput(attrs={'class': 'form-control'}),

            'content': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 6,
                    'placeholder': 'Write your blog content here...'
                }
            ),

            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_video(self):
        video = self.cleaned_data.get("video")

        if video and video.size > 20 * 1024 * 1024:
            raise forms.ValidationError("Video must be under 20MB")

        return video
# ===============================
# COMMENT FORM
# ===============================
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Write your comment...'
                }
            )
        }

class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = [
            'bio',
            'profile_image',
            'website',
            'age',
            'address',
            'phone',
            'city'
        ]

        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write about yourself...'
            }),

            'profile_image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),

            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourwebsite.com'
            }),

            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your age'
            }),

            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your address'
            }),

            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),

            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your city'
            }),
        }