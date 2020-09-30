from django.db import models
from django.contrib.auth import models as authmodels


# Create your models here.

class Module(models.Model):
    name = models.CharField(max_length=100)
    nr = models.CharField(max_length=20)
    cp = models.SmallIntegerField()
    workload = models.SmallIntegerField()
    self_study = models.SmallIntegerField()
    duration = models.SmallIntegerField()
    wise = models.BooleanField()
    sose = models.BooleanField()
    language = models.CharField(max_length=30)
    learning_content = models.TextField(max_length=5000)
    qualification = models.TextField(max_length=5000)
    requirements = models.TextField(max_length=5000)


class Vote(models.Model):
    user = models.ForeignKey(authmodels.User, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    score = models.SmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'module'], name='unique_vote')
        ]
