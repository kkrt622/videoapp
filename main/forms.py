from django.contrib.auth import get_user_model, authenticate
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import AuthenticationCode
from django.forms.widgets import PasswordInput
from django.utils.translation import gettext_lazy as _
from django.utils.text import capfirst

User = get_user_model()


class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={"autofocus": True, "placeholder": "メールアドレス", "class": "form"}
        ),
    )
    password = forms.CharField(
        label=_("Password"),
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
        kwargs.setdefault("label_suffix", "")
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


class RegistrationEmailForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs["class"] = "form"
        self.fields["email"].widget.attrs["placeholder"] = "メールアドレス"

    class Meta:
        model = User
        fields = ("email",)


class RegistrationCodeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["code"].widget.attrs["class"] = "form"
        self.fields["code"].widget.attrs["placeholder"] = "認証コード(数字4ケタ)"

    class Meta:
        model = AuthenticationCode
        fields = ("code",)


class PasswordForm(forms.ModelForm):
    password = forms.CharField(
        widget=PasswordInput(
            attrs={"autofocus": True, "placeholder": "パスワード", "class": "form"}
        ),
    )

    class Meta:
        model = User
        fields = ("password",)
