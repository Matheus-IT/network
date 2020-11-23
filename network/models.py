from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms.widgets import Textarea

# adicional models: posts, likes, and followers

class User(AbstractUser):
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username
        }


class Follower(models.Model):
    user_being_followed = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers'
    )

    user_follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='users_being_followed'
    )


class Post(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'Auth {self.poster.username}: {self.content[:30]}... Timestamp: {self.timestamp}'

    def serialize(self):
        return {
            'id': self.id,
            'poster': self.poster.serialize(),
            'content': self.content,
            'timestamp': self.timestamp.strftime('%b %d %Y, %I:%M %p'),
            'likes': self.likes
        }


class Like(models.Model):
    liker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
