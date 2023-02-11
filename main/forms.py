from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model, authenticate
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import AuthenticationCode, Video
from django.core.exceptions import ValidationError
from django.forms.widgets import PasswordInput
from django.utils.translation import gettext_lazy as _
from django.utils.text import capfirst

User = get_user_model()


class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"autofocus": True, "placeholder": "メールアドレス", "class": "form"}
        ),
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput({"placeholder": "パスワード", "class": "form"}),
    )
    error_messages = {
        "invalid_login": _("Eメールアドレスまたはパスワードに誤りがあります。"),
        "inactive": _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)
        self.email_field = User._meta.get_field("email")
        if self.fields["email"].label is None:
            self.fields["email"].label = capfirst(self.email_field.verbose_name)

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email is not None and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages["invalid_login"],
                    code="invalid_login",
                    params={"email": self.email_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages["inactive"],
                code="inactive",
            )

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class EmailForm(forms.ModelForm):
    # 既に本登録されているユーザーは排除する
    def clean_email(self):
        email = self.cleaned_data["email"]
        user = User.objects.filter(email=email)
        if user.exists():
            raise ValidationError("このメールアドレスは既に使われています。")
        return email

    class Meta:
        model = User
        fields = ("email",)
        widgets = {
            "email": forms.TextInput(attrs={"class": "form", "placeholder": "メールアドレス"})
        }


class RegistrationCodeForm(forms.ModelForm):
    class Meta:
        model = AuthenticationCode
        fields = ("code",)
        widgets = {
            "code": forms.TextInput(
                attrs={"class": "form", "placeholder": "認証コード(数字4ケタ)"}
            )
        }


class PasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].widget.attrs["class"] = "old_password"
        self.fields["new_password1"].widget.attrs["class"] = "new_password1"
        self.fields["new_password2"].widget.attrs["class"] = "new_password2"
        self.fields["old_password"].widget.attrs["placeholder"] = "現在のパスワード"
        self.fields["new_password1"].widget.attrs["placeholder"] = "新しいパスワード"
        self.fields["new_password2"].widget.attrs["placeholder"] = "新しいパスワード（確認）"


class PasswordForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("password",)
        widgets = {
            "password": forms.PasswordInput(
                attrs={"autofocus": True, "placeholder": "パスワード", "class": "form"}
            )
        }


class PasswordResetEmailForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"autofocus": True, "placeholder": "メールアドレス", "class": "form"}
        ),
    )


class PasswordResetForm(forms.Form):
    new_password1 = forms.CharField(
        widget=PasswordInput({"placeholder": "新しいパスワード", "class": "form"})
    )
    new_password2 = forms.CharField(
        widget=PasswordInput({"placeholder": "新しいパスワード(確認)", "class": "form"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        new_password1 = self.cleaned_data["new_password1"]
        new_password2 = self.cleaned_data["new_password2"]
        if new_password1 != new_password2:
            raise ValidationError("パスワードが一致しません")


class ProfileChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("icon", "username", "profile")
        labels = {
            "username": "ユーザー名",
            "profile": "紹介文",
        }
        widgets = {"icon": forms.FileInput(attrs={"onchange": "previewImage(this);"})}


class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ("title", "description", "thumbnail", "video")
        widgets = {
            "thumbnail": forms.FileInput(attrs={"class": "thumbnail-form"}),
            "title": forms.Textarea(
                attrs={
                    "class": "title-form",
                    "placeholder": "タイトルを入力",
                    "onkeyup": "ShowTitleLength(value);",
                    "rows": "2",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "description-form",
                    "placeholder": "タイトルを入力",
                    "onkeyup": "ShowDescriptionLength(value);",
                }
            ),
            "video": forms.FileInput(
                attrs={
                    "class": "video-form",
                    "accept": "video/*",
                    "onchange": "VideoPreview(this);",
                    "id": "video-upload-btn",
                }
            ),
        }


class VideoSearchForm(forms.Form):
    keyword = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "動画を検索", "class": "search-form"}),
    )


class VideoUpdateForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ("title", "description", "thumbnail")
        widgets = {
            "thumbnail": forms.FileInput(attrs={"class": "thumbnail-form"}),
            "title": forms.Textarea(
                attrs={
                    "class": "title-form",
                    "rows": "2",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "description-form",
                }
            ),
        }
