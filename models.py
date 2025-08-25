import datetime
import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django_softdelete.models import SoftDeleteModel

from trakset_app.users.models import (
    User,  # Assuming User model is defined in user.models
)

# Create your models here.


class Location(SoftDeleteModel):
    # Fields
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
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


class LocationProxy(Location):
    class Meta:
        proxy = True
        verbose_name = "Location"
        verbose_name_plural = "Locations"


class AssetType(SoftDeleteModel):
    # Fields
    id = models.AutoField(primary_key=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, default="")

    class Meta:
        pass

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse("trakset_assettype_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("trakset_assettype_update", args=(self.pk,))


class AssetTypeProxy(AssetType):
    class Meta:
        proxy = True
        verbose_name = "Asset Type"
        verbose_name_plural = "Asset Types"


class Status(SoftDeleteModel):
    status_type = models.CharField(
        max_length=50,
        blank=False,
        null=False,
        primary_key=True,
    )

    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Statuses"

    def __str__(self):
        return str(self.status_type)


class StatusProxy(Status):
    class Meta:
        proxy = True
        verbose_name = "Status"
        verbose_name_plural = "Statuses"


def get_admin_for_default():
    """Get the default admin user for the current environment."""
    try:
        return User.objects.get(username="admin").id
    except User.DoesNotExist:
        return None  # Handle case where admin user does not exist


class Asset(SoftDeleteModel):
    # Fields
    id = models.AutoField(primary_key=True, unique=True)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    send_user_email_on_transfer = models.ManyToManyField(
        User,
        related_name="send_user_email_on_transfer",
        blank=True,
        verbose_name="Email on Transfer",
    )
    current_holder = models.ForeignKey(
        User,
        null=False,
        on_delete=models.SET_DEFAULT,
        related_name="current_holders",
        default=get_admin_for_default,
        verbose_name="Current Holder",
    )
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, default="")
    serial_number = models.CharField(max_length=100, blank=True, default="")
    security_tag_number = models.PositiveIntegerField(
        blank=True,
        unique=True,
        null=True,
    )
    asset_type = models.ForeignKey(
        AssetType,
        null=True,
        on_delete=models.SET_NULL,
        related_name="asset_types",
        verbose_name="Asset Type",
    )
    status = models.ForeignKey(
        Status,
        null=True,
        on_delete=models.SET_NULL,
        related_name="statuses",
        verbose_name="Status",
    )
    location = models.ForeignKey(
        Location,
        null=True,
        on_delete=models.SET_NULL,
        related_name="asset_locations",
        verbose_name="Asset Location",
    )

    class Meta:
        pass

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse("trakset_asset_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("trakset_asset_update", args=(self.pk,))


class AssetProxy(Asset):
    class Meta:
        proxy = True
        verbose_name = "Asset"
        verbose_name_plural = "Assets"


class AssetTransfer(SoftDeleteModel):
    # Fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    asset = models.ForeignKey(
        Asset,
        null=True,
        on_delete=models.SET_NULL,
        related_name="transfers",
        verbose_name="Asset Name",
    )
    from_user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name="transfers_from",
        verbose_name="From User",
    )
    to_user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name="transfers_to",
        verbose_name="To User",
    )

    def __str__(self):
        name = self.asset.name if self.asset is not None else "Deleted Asset!"
        return (
            f"Transfer of {name} from {self.from_user.username} "
            f"to {self.to_user.username} on "
            f"{self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def was_transferred_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(
            hours=settings.TRANSFER_TIMEOUT,
        )


class AssetTransferProxy(AssetTransfer):
    class Meta:
        proxy = True
        verbose_name = "Asset Transfer"
        verbose_name_plural = "Asset Transfers"


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
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f"Notes {self.text:50}"
