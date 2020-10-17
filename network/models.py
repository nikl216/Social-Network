from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    created_by = models.ForeignKey("User", on_delete=models.CASCADE, related_name="posts")
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    liked_users = models.ManyToManyField(User)
    
    def __str__(self):
        return f"{self.created_by} : {self.pk}" 

class UserFollowing(models.Model):
    user_id = models.ForeignKey("User", on_delete=models.CASCADE, related_name="following")
    following_user_id = models.ForeignKey("User", on_delete=models.CASCADE, related_name="followers")

