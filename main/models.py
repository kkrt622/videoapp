from django.contrib.auth.models import AbstractUser
from django.db import models

PLAY_SPEED_CHOICE = (
    ("slow", "スロー"),
    ("standard", "標準"),
    ("double", "倍速"),
)

IMAGE_QUOLITY_CHOICE = (("low", "低画質"), ("standard", "標準"), ("high", "高画質"))


class User(AbstractUser):
    username = models.CharField("ユーザ名", max_length=50, blank=True)
    email = models.EmailField("メールアドレス", unique=True)
    profile = models.TextField("プロフィール", max_length=500, null=True)
    icon = models.ImageField("アイコン", upload_to="icon/", blank=True)
    follow = models.ManyToManyField("User", related_name="followed", symmetrical=False)
    is_registered = models.BooleanField("本登録完了", default=False)

    class Meta:
        verbose_name_plural = "ユーザー"

    def __str__(self):
        return f"{self.email}"


class AuthenticationCode(models.Model):
    code = models.IntegerField()
    email = models.EmailField("メールアドレス", unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "認証コード"


class Video(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField("タイトル", max_length=50)
    description = models.TextField("説明", max_length=500)
    thumbnail = models.ImageField("サムネイル", upload_to="thumbnail/")
    uploaded_date = models.DateTimeField("動画投稿時刻", auto_now_add=True)
    filename = models.CharField("ファイル名", max_length=200)
    views_count = models.IntegerField("視聴回数", default=0)

    class Meta:
        verbose_name_plural = "ビデオ"

    def __str__(self):
        return self.title


class UserVideoSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    play_speed = models.CharField(
        "再生速度", max_length=20, choices=PLAY_SPEED_CHOICE, default="standard"
    )
    image_quality = models.CharField(
        "画質", max_length=20, choices=IMAGE_QUOLITY_CHOICE, default="standard"
    )

    class Meta:
        verbose_name_plural = "動画設定"


class VideoComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    comment = models.CharField("コメント", max_length=500)
    created_at = models.DateTimeField("", auto_now_add=True)

    class Meta:
        verbose_name_plural = "フィードバックコメント"
