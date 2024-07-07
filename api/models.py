import uuid

from django.db import models

from accounts.models import CustomUser


class Organisation(models.Model):
    org_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, null=False)
    description = models.TextField(null=True)
    users = models.ManyToManyField(CustomUser, related_name="organisations")
