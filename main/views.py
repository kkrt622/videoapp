from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    LogoutView,
)
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model, login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, FormView, DetailView, ListView
from django.core.mail import send_mail
from django.template.loader import get_template
from django.conf import settings
from django.urls import reverse_lazy
from .models import AuthenticationCode, Video
import random
from .forms import (
    EmailAuthenticationForm,
    RegistrationEmailForm,
    RegistrationCodeForm,
    PasswordForm,
    PasswordResetForm,
    PasswordResetConfirmationForm,
    PasswordChangeForm,
    ProfileChangeForm,
    VideoUploadForm,
)

from django.db.models import Q

from django.db.models import Count 

from django.contrib.auth.decorators import login_required

import uuid

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


def registration_send_mail(email):
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


def password_reset_send_mail(email):
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


class LoginView(LoginView):
    template_name = "main/login.html"
    form_class = EmailAuthenticationForm
    redirect_authenticated_user = True


class TempRegistrationView(FormView):
    template_name = "main/temp_registration.html"
    form_class = RegistrationEmailForm
    model = User

    def form_valid(self, form, **kwargs):
        context = super().get_context_data(**kwargs)
        context["email"] = form.cleaned_data["email"]
        email = self.request.POST.get("email")

        # メール送信
        registration_send_mail(email)

        # 仮登録処理
        user, created = User.objects.get_or_create(
            username=email, email=email, defaults={"is_registered": False}
        )
        return redirect("temp_registration_done", user.id)


class TempRegistrationDoneView(FormView):
    template_name = "main/temp_registration_done.html"
    form_class = RegistrationCodeForm
    model = AuthenticationCode
    success_url = reverse_lazy("temp_registration_done")

    def form_valid(self, form, **kwargs):
        user_id = self.kwargs["user_id"]
        user = get_object_or_404(User, pk=user_id)
        email = user.email
        input_code = self.request.POST.get("code")
        authentication_code = AuthenticationCode.objects.get(email=email).code
        if int(input_code) == authentication_code:
            return redirect("signup", user.id)
        return render(self.request, "main/temp_registration_done.html")

    def get_context_data(self, **kwargs):
        if "email" in self.request.GET:
            email = self.request.GET.get("email")
            registration_send_mail(email)

        context = super().get_context_data(**kwargs)
        user_id = self.kwargs["user_id"]
        user = get_object_or_404(User, pk=user_id)
        context["user"] = user
        return context


def regenerate_code(request):
    random_number = random.randrange(1000, 9999)
    return render(request, "main/temp_registration_done.html")


class SignUpView(FormView):
    template_name = "main/signup.html"
    form_class = PasswordForm
    model = User
    success_url = reverse_lazy("home")

    def form_valid(self, form, **kwargs):
        user_id = self.kwargs["user_id"]
        user = User.objects.filter(id=user_id)
        email = get_object_or_404(User, id=user_id).email
        password = form.cleaned_data["password"]
        password = make_password(password)
        user.update(password=password, is_registered=True)
        user = authenticate(email=email, password=password)
        if user:
            login(self.request, user)
        return super().form_valid(form, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs["user_id"]
        user = get_object_or_404(User, pk=user_id)
        context["user"] = user
        return context


class PasswordResetView(FormView):
    template_name = "main/password_reset.html"
    form_class = PasswordResetForm
    model = User

    def form_valid(self, form, **kwargs):
        context = super().get_context_data(**kwargs)
        context["email"] = form.cleaned_data["email"]
        email = self.request.POST.get("email")

        # メール送信
        password_reset_send_mail(email)

        user = get_object_or_404(User, email=email)
        return redirect("password_reset_confirmation", user.id)


class PasswordResetConfirmationView(FormView):
    template_name = "main/password_reset_confirmation.html"
    form_class = PasswordResetConfirmationForm
    model = AuthenticationCode
    success_url = reverse_lazy("password_reset_confirmation")

    def form_valid(self, form, **kwargs):
        user_id = self.kwargs["user_id"]
        user = get_object_or_404(User, pk=user_id)
        email = user.email
        input_code = self.request.POST.get("code")
        authentication_code = AuthenticationCode.objects.get(email=email).code
        if int(input_code) == authentication_code:
            return redirect("password_change", user.id)
        return render(self.request, "main/password_reset_confirmation.html")

    def get_context_data(self, **kwargs):
        # メール再送信
        if "email" in self.request.GET:
            email = self.request.GET.get("email")
            password_reset_send_mail(email)

        context = super().get_context_data(**kwargs)
        user_id = self.kwargs["user_id"]
        user = get_object_or_404(User, pk=user_id)
        context["user"] = user
        return context


class PasswordChangeView(FormView):
    template_name = "main/password_change.html"
    form_class = PasswordChangeForm
    success_url = reverse_lazy("login")

    def form_valid(self, form, **kwargs):
        user_id = self.kwargs["user_id"]
        user = User.objects.filter(id=user_id)
        new_password = form.cleaned_data["new_password1"]
        new_password = make_password(new_password)
        user.update(password=new_password)
        return super().form_valid(form, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs["user_id"]
        user = get_object_or_404(User, pk=user_id)
        context["user"] = user
        return context

@login_required
def following(request):
    following = get_object_or_404(User, id=request.user.id).follow.all()
    context = {"following": following}
    return render(request, "main/following.html", context)

@login_required
def my_account(request):
    account = User.objects.annotate(
        follower_count = Count("followed")
    ).get(id = request.user.id)

    videos = Video.objects.filter(
    Q(user = account)
    ).all()
    video_count =videos.count()

    # プロフィール編集の処理
    if request.method == "GET":
        form = ProfileChangeForm(instance=request.user)
    elif request.method == "POST":
        form = ProfileChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            # 保存後、完了ページに遷移します
            return redirect("my_account")

    context = {
        "account": account,
        "form": form,
        "videos": videos,
        "video_count": video_count,
    }
    return render(request, "main/account.html", context)

@login_required
def others_account(request, user_id):
    others_account = User.objects.annotate(
        follower_count = Count("followed")
    ).get(id = user_id)

    videos = Video.objects.filter(
        Q(user = others_account)
    ).all()
    video_count =videos.count()

    my_account = User.objects.annotate(
    follower_count = Count("followed")
    ).get(id = request.user.id)
    # 自分がフォロー中の相手を取得
    followers = my_account.follow.all()
    # プロフィール表示をしようとしている相手をフォローしているかのチェック
    if followers:
        for follower in followers:
            if follower.id == others_account.id :
                follow = True
                break
            else:
                follow = False
    else:
        # フォローが0でも変数"follow"を定義
        follow = None
        
    context = {
        "account": others_account,
        "videos": videos,
        "video_count": video_count,
        "follow" : follow,
    }
    return render(request, "main/account.html", context)

@login_required
def follow(request, user_id):
    follow = User.objects.get(id = user_id)
    request.user.follow.add(follow)
    request.user.save()
    return redirect("others_account", user_id)

@login_required    
def unfollow(request, user_id):
    follow = User.objects.get(id = user_id)
    request.user.follow.remove(follow)
    request.user.save()
    return redirect("others_account", user_id)

@login_required
def settings(request):
    return render(request, "main/settings.html")

def terms(request):
    return render(request, "main/terms.html")

def privacy_policy(request):
    return render(request, "main/privacy_policy.html")


class LogoutView(LogoutView):
    pass

class AccountDeleteView(generic.edit.DeleteView):
    template_name = "main/account_delete.html"
    model = User
    success_url = reverse_lazy("account_delete_done")

class AccountDeleteDoneView(generic.base.TemplateView):
    template_name = "main/account_delete_done.html"

class VideoUploadView(LoginRequiredMixin, FormView):
    template_name = "main/video_upload.html"
    form_class = VideoUploadForm
    # アカウントページに移行する必要あり
    success_url = reverse_lazy("home")

    def form_valid(self, form, **kwargs):
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
        queryset = queryset.filter(id=self.kwargs["pk"])
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

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        if "keyword" in self.request.GET:
            keyword = self.request.GET.get("keyword")
            if keyword:
                keywords = keyword.split()
                for k in keywords:
                    queryset = queryset.filter(title__icontains=k)
        if self.request.GET.get("btnType") == "favorite":
            queryset = queryset.order_by("-views_count")[:2]
        else:
            queryset = queryset.order_by("-uploaded_date")
        return queryset
