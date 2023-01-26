from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import timedelta
from django.utils import timezone
import os
import uuid


class User(AbstractUser):
    email = models.EmailField("メールアドレス", unique=True)
    username = models.CharField("ユーザ名", max_length=50, default="ゲスト", unique=False)
    profile = models.TextField("プロフィール", max_length=500, null=True)
    icon = models.ImageField("アイコン", upload_to="icon/", blank=True)
    follow = models.ManyToManyField("User", related_name="followed", symmetrical=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

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


def video_directory_path(instance, filename):
    return "uploaded_video/{}.{}".format(str(uuid.uuid4()), filename.split(".")[-1])


class Video(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="video")
    title = models.TextField("タイトル", max_length=50)
    description = models.TextField("説明", max_length=500)
    thumbnail = models.ImageField("サムネイル", upload_to="thumbnail/")
    uploaded_date = models.DateTimeField("動画投稿時刻", auto_now_add=True)
    video = models.FileField("ビデオファイル", upload_to=video_directory_path)
    views_count = models.IntegerField("視聴回数", default=0)

    class Meta:
        verbose_name_plural = "ビデオ"

    def file_name(self):
        return os.path.basename(self.video.name).split(".")[0]

    def get_elapsed_time(self):
        delta = timezone.now() - self.uploaded_date

        zero = timedelta()
        one_hour = timedelta(hours=1)
        one_day = timedelta(days=1)
        one_week = timedelta(days=7)

        if delta < zero:
            raise ValueError("未来の時刻です。")

        if delta < one_hour:
            return f"{delta.seconds // 60} 分前"
        elif delta < one_day:
            return f"{delta.seconds // 3600} 時間前"
        elif delta < one_week:
            return f"{delta.days} 日前"
        else:
            return "1 週間以上前"

    def __str__(self):
        return self.title


class VideoComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    comment = models.CharField("コメント", max_length=500)
    created_at = models.DateTimeField("", auto_now_add=True)

    class Meta:
        verbose_name_plural = "フィードバックコメント"
