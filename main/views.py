import random

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
)
from django.core import signing
from django.core.mail import send_mail
from django.db.models import Count, Case, When, Prefetch
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_POST
from django.views.generic import (
    View,
    TemplateView,
    FormView,
    DetailView,
    ListView,
    DeleteView,
    UpdateView,
)

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
    VideoUpdateForm,
)
from .models import AuthenticationCode, Video

User = get_user_model()


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "main/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        video = Video.objects.all().order_by("-uploaded_at")
        context["videos"] = video
        return context


def generate_random_code(email):
    random_number = "{:0>4}".format(random.randrange(10000))
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
    from_email = None
    recipient_list = [email]
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
    from_email = None
    recipient_list = [email]
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
    from_email = None
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)


class LoginView(LoginView):
    template_name = "main/login.html"
    form_class = EmailAuthenticationForm
    redirect_authenticated_user = True


class TempRegistrationView(FormView):
    template_name = "main/temp_registration.html"
    form_class = EmailForm
    model = User

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        token = signing.dumps(email)
        registration_send_email(email)
        return redirect("temp_registration_done", token)


class TempRegistrationDoneView(FormView):
    template_name = "main/temp_registration_done.html"
    form_class = RegistrationCodeForm
    model = AuthenticationCode

    def get(self, request, **kwargs):
        token = self.kwargs["token"]
        try:
            signing.loads(token)
        except signing.BadSignature:
            messages.error(self.request, "無効なURLです。もう一度やり直してください")
            return redirect("password_reset_email")

        if "email" in self.request.GET:
            email = self.request.GET.get("email")
            registration_send_email(email)
        return super().get(request, **kwargs)

    def form_valid(self, form, **kwargs):
        token = self.kwargs["token"]
        email = signing.loads(token)
        input_code = form.cleaned_data["code"]
        authentication_code_obj = AuthenticationCode.objects.get(email=email)
        authentication_code = authentication_code_obj.code
        context = {"form": form, "email": email}
        if input_code == authentication_code:
            if authentication_code_obj.is_valid():
                return redirect("signup", token)
            else:
                messages.error(self.request, "この認証コードは無効です。新しい認証コードを発行してください。")
        else:
            messages.error(self.request, "認証コードが正しくありません")
        return render(self.request, "main/temp_registration_done.html", context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.kwargs["token"]
        email = signing.loads(token)
        context["email"] = email
        return context


class SignUpView(FormView):
    template_name = "main/signup.html"
    form_class = PasswordForm
    model = User
    success_url = reverse_lazy("login")

    def get(self, request, **kwargs):
        token = self.kwargs["token"]
        try:
            signing.loads(token)
        except signing.BadSignature:
            messages.error(self.request, "無効なURLです。もう一度やり直してください")
            return redirect("temp_registration")
        return super().get(request, **kwargs)

    def form_valid(self, form, **kwargs):
        token = self.kwargs["token"]
        email = signing.loads(token)
        password = form.cleaned_data["password"]
        password = make_password(password)
        User.objects.create(username="ゲスト", email=email, password=password)
        return super().form_valid(form, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.kwargs["token"]
        email = signing.loads(token)
        context["email"] = email
        return context


class PasswordResetEmailView(FormView):
    template_name = "main/password_reset_email.html"
    form_class = PasswordResetEmailForm
    model = User

    def form_valid(self, form):
        token = self.kwargs["token"]
        email = signing.loads(token)
        password_reset_send_email(email)
        return redirect("password_reset_confirmation", token)


class PasswordResetConfirmationView(FormView):
    template_name = "main/password_reset_confirmation.html"
    form_class = RegistrationCodeForm
    model = AuthenticationCode

    def get(self, request, **kwargs):
        token = self.kwargs["token"]
        try:
            signing.loads(token)
        except signing.BadSignature:
            messages.error(self.request, "無効なURLです。もう一度やり直してください")
            return redirect("temp_registration")

        if "email" in self.request.GET:
            email = self.request.GET.get("email")
            registration_send_email(email)
        return super().get(request, **kwargs)

    def form_valid(self, form):
        token = self.kwargs["token"]
        email = signing.loads(token)
        input_code = form.cleaned_data["code"]
        context = {"form": form, "email": email}
        authentication_code_obj = AuthenticationCode.objects.get(email=email)
        authentication_code = authentication_code_obj.code
        if input_code == authentication_code:
            if authentication_code_obj.is_valid():
                return redirect("password_reset", token)
            else:
                messages.error(self.request, "この認証コードは無効です。新しい認証コードを発行してください。")
        else:
            messages.error(self.request, "認証コードが正しくありません")
        return render(self.request, "main/password_reset_confirmation.html", context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.kwargs["token"]
        email = signing.loads(token)
        context["email"] = email
        return context


class PasswordResetView(FormView):
    template_name = "main/password_reset.html"
    form_class = PasswordResetForm
    success_url = reverse_lazy("login")

    def get(self, request, **kwargs):
        token = self.kwargs["token"]
        try:
            signing.loads(token)
        except signing.BadSignature:
            messages.error(self.request, "無効なURLです。もう一度やり直してください")
            return redirect("temp_registration")
        return super().get(request, **kwargs)

    def form_valid(self, form, **kwargs):
        token = self.kwargs["token"]
        email = signing.loads(token)
        new_password = form.cleaned_data["new_password1"]
        new_password = make_password(new_password)
        user = User.objects.filter(email=email)
        user.update(password=new_password)
        return super().form_valid(form, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.kwargs["token"]
        email = signing.loads(token)
        context["email"] = email
        return context


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = "main/password_change.html"
    form_class = PasswordChangeForm

    def get_success_url(self):
        return reverse("account", kwargs={"pk": self.request.user.pk})


class EmailResetView(LoginRequiredMixin, FormView):
    template_name = "main/email_reset.html"
    form_class = EmailForm
    model = User

    def form_valid(self, form):
        new_email = form.cleaned_data["email"]
        token = signing.dumps(new_email)
        email_reset_send_email(new_email)
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
        token = self.kwargs["token"]
        try:
            signing.loads(token)
        except signing.BadSignature:
            messages.error(self.request, "無効なURLです。もう一度やり直してください")
            return redirect("temp_registration")

        if "email" in self.request.GET:
            email = self.request.GET.get("email")
            registration_send_email(email)
        return super().get(request, **kwargs)

    def form_valid(self, form):
        token = self.kwargs["token"]
        new_email = signing.loads(token)
        input_code = form.cleaned_data["code"]
        authentication_code_obj = AuthenticationCode.objects.get(email=new_email)
        authentication_code = authentication_code_obj.code
        context = {"form": form, "email": new_email}
        if input_code == authentication_code:
            if authentication_code_obj.is_valid():
                user = User.objects.filter(id=self.request.user.id)
                user.update(email=new_email)
                return redirect("account", self.request.user.id)
            else:
                messages.error(self.request, "この認証コードは無効です。新しい認証コードを発行してください。")
        else:
            messages.error(self.request, "認証コードが正しくありません")
        return render(self.request, "main/email_reset_confirmation.html", context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.kwargs["token"]
        new_email = signing.loads(token)
        context["email"] = new_email
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
                Prefetch("video", queryset=Video.objects.order_by("-uploaded_at"))
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


class FollowView(LoginRequiredMixin, View):
    def post(self, request, pk):
        follow = User.objects.get(pk=pk)
        request.user.follow.add(follow)
        request.user.save()
        return redirect("account", pk)


class UnfollowView(LoginRequiredMixin, View):
    def post(self, request, pk):
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
        video = form.save(commit=False)
        video.user = self.request.user
        video.save()
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
            queryset = queryset.order_by("-uploaded_at")
        return queryset


class VideoUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "main/video_update.html"
    model = Video
    form_class = VideoUpdateForm

    def get_success_url(self):
        return reverse("account", kwargs={"pk": self.request.user.pk})


@require_POST
def video_delete(request, pk):
    Video.objects.filter(pk=pk).delete()
    return redirect("account", pk)
