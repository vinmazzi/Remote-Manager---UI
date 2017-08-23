from django.db import models
class Client(models.Model):
    client_name = models.CharField(max_length=20)

    def __str__(self):
        return self.client_name
