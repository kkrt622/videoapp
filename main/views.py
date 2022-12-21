from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.views import generic
from django.contrib.auth import get_user_model, login, authenticate
from django.core.mail import send_mail
from django.template.loader import get_template
from django.conf import settings
from django.urls import reverse_lazy
from .models import AuthenticationCode
import random
from .forms import (
    EmailAuthenticationForm,
    RegistrationEmailForm,
    RegistrationCodeForm,
    PasswordForm,
)

User = get_user_model()


def home(request):
    return render(request, "main/home.html")


class LoginView(LoginView):
    template_name = "main/login.html"
    form_class = EmailAuthenticationForm
    redirect_authenticated_user = True


class TempRegistrationView(generic.FormView):
    template_name = "main/temp_registration.html"
    form_class = RegistrationEmailForm
    model = User

    def generate_random_code(self, email):
        random_number = random.randrange(1000, 9999)
        AuthenticationCode.objects.update_or_create(
            email=email, defaults={"code": random_number, "email": email}
        )
        return random_number

    def form_valid(self, form, **kwargs):
        context = super().get_context_data(**kwargs)
        context["email"] = form.cleaned_data["email"]
        email = self.request.POST.get("email")

        # メール送信
        message_template = get_template("mail_text/registration.txt")
        random_code = self.generate_random_code(email)
        context = {
            "email": email,
            "random_code": random_code,
        }
        subject = "Video Appの本登録について"
        message = message_template.render(context)
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = ([email],)
        send_mail(subject, message, from_email, recipient_list)

        # 仮登録処理
        user = form.save(commit=False)
        user.is_registered = False
        user.save()
        return redirect("temp_registration_done", user.id)


class TempRegistrationDoneView(generic.FormView):
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
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs["user_id"]
        user = get_object_or_404(User, pk=user_id)
        context["user"] = user
        return context


def regenerate_code(request):
    random_number = random.randrange(1000, 9999)
    return render(request, "main/temp_registration_done.html")


class SignUpView(generic.FormView):
    template_name = "main/signup.html"
    form_class = PasswordForm
    model = User
    success_url = reverse_lazy("home")

    def form_valid(self, form, **kwargs):
        user_id = self.kwargs["user_id"]
        user = User.objects.filter(id=user_id)
        email = get_object_or_404(User, id=user_id).email
        password = form.cleaned_data["password"]
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
