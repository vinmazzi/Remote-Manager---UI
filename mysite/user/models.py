from django.db import models
from django.contrib.auth.models import User, Group
from client.models import Client

# Create your models here.

class UserExtraInfo(models.Model):
    user_fk = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    client_fk = models.ForeignKey(Client, on_delete=models.CASCADE, default=0)
