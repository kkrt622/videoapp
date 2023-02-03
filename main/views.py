from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
)
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    TemplateView,
    FormView,
    DetailView,
    ListView,
    DeleteView,
)
from django.core.mail import send_mail
from django.template.loader import get_template
from django.conf import settings
from django.urls import reverse_lazy, reverse
from .models import AuthenticationCode, Video
import random
from .forms import (
    EmailAuthenticationForm,
    EmailForm,
    RegistrationCodeForm,
    PasswordForm,
    PasswordResetEmailForm,
    PasswordChangeForm,
    PasswordResetForm,
    ProfileChangeForm,
    VideoUploadForm,
    VideoSearchForm,
)
from django.db.models import Count, Case, When, Prefetch
from django.contrib.auth.decorators import login_required
import hashlib

User = get_user_model()


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "main/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        video = Video.objects.all().order_by("-uploaded_date")
        context["videos"] = video
        return context


def generate_random_code(email):
    random_number = random.randrange(1000, 9999)
    AuthenticationCode.objects.update_or_create(
        email=email, defaults={"code": random_number, "email": email}
    )
    return random_number


def registration_send_email(email):
    message_template = get_template("mail_text/registration.txt")
    random_code = generate_random_code(email)
    context = {
        "email": email,
        "random_code": random_code,
    }
    subject = "Video Appの本登録について"
    message = message_template.render(context)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ([email],)
    send_mail(subject, message, from_email, recipient_list)


def password_reset_send_email(email):
    message_template = get_template("mail_text/password_reset.txt")
    random_code = generate_random_code(email)
    context = {
        "email": email,
        "random_code": random_code,
    }
    subject = "パスワード再設定について"
    message = message_template.render(context)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ([email],)
    send_mail(subject, message, from_email, recipient_list)


def email_reset_send_email(email):
    message_template = get_template("mail_text/email_reset.txt")
    random_code = generate_random_code(email)
    context = {
        "email": email,
        "random_code": random_code,
    }
    subject = "メール再設定について"
    message = message_template.render(context)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ([email],)
    send_mail(subject, message, from_email, recipient_list)


def generate_token(email):
    str = email
    token = hashlib.sha1(str.encode("utf-8")).hexdigest()
    return token


class LoginView(LoginView):
    template_name = "main/login.html"
    form_class = EmailAuthenticationForm
    redirect_authenticated_user = True


class TempRegistrationView(FormView):
    template_name = "main/temp_registration.html"
    form_class = EmailForm
    model = User

    def form_valid(self, form):
        email = self.request.POST.get("email")
        # トークンの生成
        token = generate_token(email)
        # メール送信
        registration_send_email(email)
        # 送信内容をセッションに保存する
        self.request.session["signup_email"] = email
        return redirect("temp_registration_done", token)


class TempRegistrationDoneView(FormView):
    template_name = "main/temp_registration_done.html"
    form_class = RegistrationCodeForm
    model = AuthenticationCode

    def get(self, request, **kwargs):
        if "email" in self.request.GET:
            email = self.request.GET.get("email")
            registration_send_email(email)
        return super().get(request, **kwargs)

    def form_valid(self, form):
        email = self.request.session.get("signup_email")
        token = generate_token(email)
        input_code = self.request.POST["code"]
        authentication_code = AuthenticationCode.objects.get(email=email).code
        context = {"token": token, "form": form, "email": email}
        if int(input_code) == authentication_code:
            return redirect("signup", token)
        else:
            messages.error(self.request, "認証コードが正しくありません")
        return render(self.request, "main/temp_registration_done.html", context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.request.session["signup_email"]
        token = generate_token(email)
        context["email"] = email
        context["token"] = token
        return context


class SignUpView(FormView):
    template_name = "main/signup.html"
    form_class = PasswordForm
    model = User
    success_url = reverse_lazy("login")

    def form_valid(self, form, **kwargs):
        email = self.request.session["signup_email"]
        password = form.cleaned_data["password"]
        password = make_password(password)
        User.objects.create(username="ゲスト", email=email, password=password)
        del self.request.session["signup_email"]
        return super().form_valid(form, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.request.session["signup_email"]
        token = generate_token(email)
        context["email"] = email
        context["token"] = token
        return context


class PasswordResetEmailView(FormView):
    template_name = "main/password_reset_email.html"
    form_class = PasswordResetEmailForm
    model = User

    def form_valid(self, form):
        email = self.request.POST.get("email")
        token = generate_token(email)
        # メール送信
        password_reset_send_email(email)
        # 送信内容をセッションに保存する
        self.request.session["password_reset_email"] = email
        return redirect("password_reset_confirmation", token)


class PasswordResetConfirmationView(FormView):
    template_name = "main/password_reset_confirmation.html"
    form_class = RegistrationCodeForm
    model = AuthenticationCode

    def get(self, request, **kwargs):
        if "email" in self.request.GET:
            email = self.request.GET.get("email")
            registration_send_email(email)
        return super().get(request, **kwargs)

    def form_valid(self, form):
        email = self.request.session.get("password_reset_email")
        token = generate_token(email)
        input_code = self.request.POST.get("code")
        authentication_code = AuthenticationCode.objects.get(email=email).code
        context = {"token": token, "form": form, "email": email}
        if int(input_code) == authentication_code:
            return redirect("password_reset", token)
        else:
            messages.error(self.request, "認証コードが正しくありません")
        return render(self.request, "main/password_reset_confirmation.html", context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.request.session["password_reset_email"]
        token = generate_token(email)
        context["email"] = email
        context["token"] = token
        return context


class PasswordResetView(FormView):
    template_name = "main/password_reset.html"
    form_class = PasswordResetForm
    success_url = reverse_lazy("login")

    def form_valid(self, form, **kwargs):
        email = self.request.session["password_reset_email"]
        new_password = form.cleaned_data["new_password1"]
        new_password = make_password(new_password)
        user = User.objects.filter(email=email)
        user.update(password=new_password)
        return super().form_valid(form, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.request.session["password_reset_email"]
        token = generate_token(email)
        context["email"] = email
        context["token"] = token
        return context


class PasswordChangeView(LoginRequiredMixin, auth_views.PasswordChangeView):
    template_name = "main/password_change.html"
    form_class = PasswordChangeForm

    def get_success_url(self):
        return reverse("account", kwargs={"pk": self.request.user.pk})


class EmailResetView(LoginRequiredMixin, FormView):
    template_name = "main/email_reset.html"
    form_class = EmailForm
    model = User

    def form_valid(self, form):
        new_email = self.request.POST.get("email")
        token = generate_token(new_email)
        # メール送信
        email_reset_send_email(new_email)
        self.request.session["email_reset_email"] = new_email
        return redirect("email_reset_confirmation", token)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        user = get_object_or_404(User, pk=user_id)
        context["user"] = user
        return context


class EmailResetConfirmationView(LoginRequiredMixin, FormView):
    template_name = "main/email_reset_confirmation.html"
    form_class = RegistrationCodeForm
    model = AuthenticationCode

    def get(self, request, **kwargs):
        if "email" in self.request.GET:
            email = self.request.GET.get("email")
            registration_send_email(email)
        return super().get(request, **kwargs)

    def form_valid(self, form):
        new_email = self.request.session["email_reset_email"]
        token = generate_token(new_email)
        input_code = self.request.POST.get("code")
        authentication_code = AuthenticationCode.objects.get(email=new_email).code
        context = {"token": token, "form": form, "email": new_email}
        if int(input_code) == authentication_code:
            # メールアドレスの変更
            user = User.objects.filter(id=self.request.user.id)
            user.update(email=new_email)
            return redirect("account", self.request.user.id)
        else:
            messages.error(self.request, "認証コードが正しくありません")
        return render(self.request, "main/email_reset_confirmation.html", context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        new_email = self.request.session["email_reset_email"]
        token = generate_token(new_email)
        context["email"] = new_email
        context["token"] = token
        return context


@login_required
def following(request):
    following = get_object_or_404(User, id=request.user.id).follow.all()
    context = {"following": following}
    return render(request, "main/following.html", context)


class AccountView(LoginRequiredMixin, DetailView):
    template_name = "main/account.html"
    model = User

    def get(self, request, **kwargs):
        form = ProfileChangeForm(instance=request.user)
        return super().get(request, **kwargs)

    def post(self, request, **kwargs):
        form = ProfileChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("account", self.kwargs["pk"])

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        queryset = (
            User.objects.filter(pk=self.kwargs["pk"])
            .prefetch_related(
                Prefetch("video", queryset=Video.objects.order_by("-uploaded_date"))
            )
            .annotate(
                follower_count=Count("followed", distinct=True),
                video_count=Count("video"),
            )
        )

        if self.kwargs["pk"] != self.request.user.pk:
            follow_list = self.request.user.follow.all().values_list("id", flat=True)
            queryset = queryset.annotate(
                is_follow=Case(
                    When(id__in=follow_list, then=True),
                    default=False,
                )
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = ProfileChangeForm(instance=self.request.user)
        context["form"] = form

        return context


@login_required
def follow(request, pk):
    follow = User.objects.get(pk=pk)
    request.user.follow.add(follow)
    request.user.save()
    return redirect("account", pk)


@login_required
def unfollow(request, pk):
    follow = User.objects.get(pk=pk)
    request.user.follow.remove(follow)
    request.user.save()
    return redirect("account", pk)


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = "main/settings.html"


class TermsView(LoginRequiredMixin, TemplateView):
    template_name = "main/terms.html"


class PrivacyPolicyView(LoginRequiredMixin, TemplateView):
    template_name = "main/privacy_policy.html"


class LogoutView(LogoutView):
    pass


class AccountDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "main/account_delete.html"
    model = User
    success_url = reverse_lazy("account_delete_done")


class AccountDeleteDoneView(TemplateView):
    template_name = "main/account_delete_done.html"


class VideoUploadView(LoginRequiredMixin, FormView):
    template_name = "main/video_upload.html"
    form_class = VideoUploadForm
    # アカウントページに移行する必要あり
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        data = form.cleaned_data
        obj = Video(**data)
        obj.user = self.request.user
        obj.save()
        return super().form_valid(form)


class PlayVideoView(LoginRequiredMixin, DetailView):
    template_name = "main/video_play.html"
    model = Video

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        queryset = queryset.filter(pk=self.kwargs["pk"])
        if "views" in self.request.GET:
            views = self.request.GET.get("views")
            queryset.update(views_count=views)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class SearchVideoView(LoginRequiredMixin, ListView):
    template_name = "main/video_search.html"
    model = Video

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = VideoSearchForm(self.request.GET)
        if form.is_valid():
            context["keyword"] = form.cleaned_data["keyword"]

        context["form"] = form
        return context

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        form = VideoSearchForm(self.request.GET)
        if form.is_valid():
            keyword = form.cleaned_data["keyword"]
            if keyword:
                queryset = queryset.filter(title__icontains=keyword)
        if self.request.GET.get("btnType") == "favorite":
            queryset = queryset.order_by("-views_count")
        else:
            queryset = queryset.order_by("-uploaded_date")
        return queryset
