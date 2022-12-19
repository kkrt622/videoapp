from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField("ユーザ名", max_length=50)
    email = models.EmailField("メールアドレス", unique=True)
    profile = models.TextField("プロフィール", max_length=500, null=True)
    icon = models.ImageField("アイコン", upload_to="icon/", blank=True)
    follow = models.ManyToManyField("User", related_name="followed")

    class Meta:
        verbose_name_plural = "User"

    def __str__(self):
        return f"{self.username}"
