from django.contrib import admin
from django.utils.html import format_html
from qr_code import qrcode
from shortener import shortener

from .models import Asset
from .models import AssetTransfer
from .models import AssetType
from .models import Location
from .models import Status


# Register your models here.
@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    def qr_tag(self, obj):
        url = self.uri + f"trakset/asset_transfer/{obj.unique_id}/"
        url_short = f"{shortener.get_or_create(self.user, url, refresh=True)}"
        self.final_url = f"{self.uri}s/{url_short}"
        options = qrcode.utils.QRCodeOptions(image_format="svg", size=5)
        qrcode_url = qrcode.maker.make_embedded_qr_code(
            self.final_url,
            options,
            force_text=True,
            use_data_uri_for_svg=False,
            alt_text=url,
            class_names="qr-code",
        )
        return format_html("{}", qrcode_url)

    def transfer_url(self, obj):
        return format_html("{}", self.final_url)

    def changelist_view(self, request, extra_context=None):
        self.user = request.user
        self.uri = f"{request.scheme}://{request.get_host()}/"
        return super().changelist_view(
            request,
            extra_context=extra_context,
        )

    @admin.display(description="Status", ordering="-type")
    def status_display_name(self, obj):
        return str(obj.status.type)

    @admin.display(description="Asset Type", ordering=("-name"))
    def type_name(self, obj):
        return str(obj.type.name)

    @admin.display(description="Description")
    def asset_description(self, obj):
        return str(obj.description)[:25] + "..."

    list_display = (
        "unique_id",
        "created_at",
        "last_updated",
        "current_holder",
        "name",
        "asset_description",
        "type_name",
        "status_display_name",
        "location__name",
        "serial_number",
        "qr_tag",
        "transfer_url",
    )

    search_fields = (
        "name",
        "description",
        "type__name",
        "status__type",
        "location__name",
        "transfers__to_user__username",
        "transfers__from_user__username",
    )
    list_filter = ("type__name", "status__type", "location__name")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "last_updated")

    def get_queryset(self, request):
        return (
            self.model.objects.select_related("type", "location", "current_holder")
            .prefetch_related("transfers")
            .defer("id")
        )


@admin.register(AssetType)
class AssetTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name", "description")
    ordering = ("-id",)
    readonly_fields = ("created_at", "last_updated")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name", "description")
    ordering = ("-id",)
    readonly_fields = ("created_at", "last_updated")


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    fields = ["type"]
    list_display = ("type",)


@admin.register(AssetTransfer)
class AssetTransferAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "asset__name",
        "asset__current_holder",
        "from_user",
        "to_user",
        "get_notes_text",
        "created_at",
        "has_been_deleted",
        "deleted_at",
        "is_restored",
        "last_updated",
    )
    search_fields = (
        "id",
        "asset__name",
        "from_user__username",
        "to_user__username",
        "notes__text",
    )
    list_filter = ("asset__name", "from_user__username", "to_user__username")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "last_updated", "get_notes_text")

    @admin.display(description="Is deleted", boolean=True)
    def has_been_deleted(self, obj):
        return obj.is_deleted

    @admin.display(description="Transfer Notes", ordering="notes")
    def get_notes_text(self, obj):
        html_string = ""
        idx = 1
        for note in obj.notes.all():
            html_string += "<li>Note" + str(idx) + ": " + note.text + "</li>"
            idx += 1
        return format_html(html_string)

    def get_queryset(self, request):
        qs = self.model.global_objects.get_queryset()

        # we need this from the superclass method
        ordering = (
            self.ordering or ()
        )  # otherwise we might try to *None, which is bad ;)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs
