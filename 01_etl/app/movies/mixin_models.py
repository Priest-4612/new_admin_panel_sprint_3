import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class UUIDMixin(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    class Meta(object):
        abstract = True


class CreatedMixin(models.Model):
    created = models.DateTimeField(
        verbose_name=_('created'),
        auto_now_add=True,
        null=True,
    )

    class Meta(object):
        abstract = True


class TimeStampedMixin(CreatedMixin):
    modified = models.DateTimeField(
        verbose_name=_('modified'),
        auto_now=True,
        null=True,
    )

    class Meta(object):
        abstract = True
