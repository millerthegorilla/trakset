import datetime
import uuid

from django.db import models
from django.urls import reverse
from django.utils import timezone

from trakset_app.users.models import (
    User,  # Assuming User model is defined in user.models
)

# Create your models here.


class Location(models.Model):
    # Fields
    id = models.AutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, default="")

    class Meta:
        pass

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse("trakset_location_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("trakset_location_update", args=(self.pk,))


class AssetType(models.Model):
    # Fields
    id = models.AutoField(primary_key=True, unique=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, default="")

    class Meta:
        pass

    def __str__(self):
        return str(self.description)

    def get_absolute_url(self):
        return reverse("trakset_asset_type_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("trakset_asset_type_update", args=(self.pk,))


class Asset(models.Model):
    # Fields
    id = models.AutoField(primary_key=True, unique=True)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    current_holder = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, default="")
    serial_number = models.CharField(max_length=100, blank=True)
    type = models.ForeignKey(
        AssetType,
        null=False,
        on_delete=models.CASCADE,
        related_name="assets",
    )
    status = models.CharField(
        max_length=50,
        blank=False,
        null=False,
        default="available",
    )
    location = models.ForeignKey(
        Location,
        null=False,
        on_delete=models.CASCADE,
        related_name="assets",
    )

    class Meta:
        pass

    def __str__(self):
        return str(self.pk)

    def get_absolute_url(self):
        return reverse("trakset_asset_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("trakset_asset_update", args=(self.pk,))


class AssetTransfer(models.Model):
    # Fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    asset = models.ForeignKey(
        Asset,
        null=False,
        on_delete=models.CASCADE,
        related_name="transfers",
    )
    from_user = models.ForeignKey(
        User,
        null=False,
        on_delete=models.CASCADE,
        related_name="transfers_from",
    )
    to_user = models.ForeignKey(
        User,
        null=False,
        on_delete=models.CASCADE,
        related_name="transfers_to",
    )

    def __str__(self):
        return (
            f"Transfer of {self.asset.name} from {self.from_user.username} "
            f"to {self.to_user.username} on "
            f"{self.created.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def was_transferred_recently(self):
        return self.created >= timezone.now() - datetime.timedelta(hours=3)


class AssetTransferNotes(models.Model):
    # Fields
    id = models.AutoField(primary_key=True, unique=True)
    text = models.TextField(blank=True, default="")
    asset_transfer = models.ForeignKey(
        "AssetTransfer",
        null=True,
        on_delete=models.SET_NULL,
        related_name="notes",
    )
    created = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f"Notes {self.text:50}"
