from django.contrib import admin
from django.utils.html import format_html
from qr_code import qrcode
from shortener import shortener

from .models import Asset
from .models import AssetTransfer
from .models import AssetType
from .models import Location


# Register your models here.
@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    def qr_tag(self, obj):
        url = self.uri + f"trakset/asset_transfer/{obj.unique_id}/"
        url_short = f"{shortener.get_or_create(self.user, url, refresh=True)}"
        final_url = f"{self.uri}s/{url_short}"
        options = qrcode.utils.QRCodeOptions(image_format="svg", size=5)
        qrcode_url = qrcode.maker.make_embedded_qr_code(
            final_url,
            options,
            force_text=True,
            use_data_uri_for_svg=False,
            alt_text=url,
            class_names="qr-code",
        )
        return format_html("{}<br><p><small>{}</small></p>", qrcode_url, final_url)

    def changelist_view(self, request, extra_context=None):
        self.user = request.user
        self.uri = f"{request.scheme}://{request.get_host()}/"
        return super().changelist_view(
            request,
            extra_context=extra_context,
        )

    list_display = (
        "id",
        "unique_id",
        "created",
        "last_updated",
        "current_holder",
        "name",
        "description",
        "type",
        "status",
        "location",
        "serial_number",
        "qr_tag",
    )
    search_fields = ("name", "description", "type", "status")
    list_filter = ("type", "status")
    ordering = ("-created",)
    readonly_fields = ("created", "last_updated")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("current_holder")


@admin.register(AssetType)
class AssetTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("-id",)
    readonly_fields = ("created", "last_updated")

    # def get_queryset(self, request):
    #     return super().get_queryset(request).select_related("type_name",
    # "type_description")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("-id",)
    readonly_fields = ("created", "last_updated")

    # def get_queryset(self, request):
    #     return super().get_queryset(request).select_related("location_name",
    # "location_description")


@admin.register(AssetTransfer)
class AssetTransferAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "asset",
        "from_user",
        "to_user",
        "get_notes_text",
        "created",
        "last_updated",
    )
    search_fields = ("asset__name", "from_user__username", "to_user__username")
    list_filter = ("asset", "from_user", "to_user")
    ordering = ("-created",)
    readonly_fields = ("created", "last_updated")

    @admin.display(description="Transfer Notes", ordering="asset_transfer__notes")
    def get_notes_text(self, obj):
        html_string = ""
        idx = 1
        for note in obj.notes.all():
            html_string += "<li>Note" + str(idx) + ": " + note.text + "</li>"
            idx += 1
        return format_html(html_string)

    # def get_queryset(self, request):
    #     return super().get_queryset(request).select_related("asset",
    # "from_user", "to_user")
