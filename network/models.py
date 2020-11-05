from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms.widgets import Textarea

# adicional models: posts, likes, and followers

class User(AbstractUser):
    pass


class Post(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    likes = models.IntegerField(default=0)

    def __str__(self):
        return f'Auth {self.poster.username}: {self.content[:30]}... Timestamp: {self.timestamp}'
