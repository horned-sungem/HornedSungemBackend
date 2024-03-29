from django.db import models
from django.contrib.auth import models as authmodels

import json

# TODO: Adjust for new module_data
# Only used for better representation in /admin
f = open('sungem/output.json')
module_data = json.load(f)
f.close()
module_nr_map = {module['Modul Nr.']: (module, index) for index, module in enumerate(module_data)}


# Create your models here.

class Module(models.Model):
    """
    Model for a single module. Maybe most information can be removed later since the data and similarity can be
    preprocessed without knowledge of Module attributes.
    """

    # TODO: Change model or remove entirely since it won't be used

    name = models.CharField(max_length=100)
    nr = models.CharField(max_length=20)
    cp = models.SmallIntegerField()
    workload = models.SmallIntegerField()
    self_study = models.SmallIntegerField()
    duration = models.SmallIntegerField()
    cycle = models.TextField()
    language = models.TextField()
    responsible = models.TextField()
    learning_content = models.TextField()
    qualification = models.TextField()
    paritcipation_requirements = models.TextField()
    exam_form = models.TextField()
    cp_requirements = models.TextField()
    grading = models.TextField()
    usability = models.TextField()
    literature = models.TextField()
    comment = models.TextField()


class Vote(models.Model):
    """
    Model for votes. Incorporates many-to-many relationship between Users and Modules. Score is kept as an integer
    which may be changed in favor of a continuous float value.
    """
    user = models.ForeignKey(authmodels.User, on_delete=models.CASCADE)
    module = models.CharField(max_length=20)
    score = models.SmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'module'], name='unique_vote')
        ]

    def __str__(self):
        return self.user.username + ' voted on ' + self.module + ': ' + str(self.score) + ' (' \
               + module_nr_map[self.module][0]['Modulname'] + ')'
