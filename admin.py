from django.contrib import admin
from django.utils.html import format_html
from django_softdelete.admin import GlobalObjectsModelAdmin
from qr_code import qrcode
from shortener import shortener

from .models import AssetProxy
from .models import AssetTransferProxy
from .models import AssetTypeProxy
from .models import LocationProxy
from .models import StatusProxy


# Register your models here.
@admin.register(AssetProxy)
class AssetAdmin(GlobalObjectsModelAdmin):
    def qr_tag(self, obj):
        url = self.uri + f"trakset/assets/transfer/{obj.unique_id}/"
        url_short = f"{shortener.get_or_create(self.user, url, refresh=True)}"
        self.final_url = f"{self.uri}s/{url_short}"
        options = qrcode.utils.QRCodeOptions(image_format="png", size=5)
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

    @admin.display(description="Status", ordering="-asset_type")
    def status_display_name(self, obj):
        return str(obj.status.status_type)

    @admin.display(description="Asset Type", ordering=("-name"))
    def asset_type_name(self, obj):
        return str(obj.asset_type.name)

    @admin.display(description="Description")
    def asset_description(self, obj):
        return str(obj.description)[:25] + "..."

    @admin.display(
        description="Users to Email on Transfer",
    )
    @admin.display(description="Email Users on Transfer")
    def get_send_user_email_on_transfer(self, obj):
        return ", ".join(
            [user.username for user in obj.send_user_email_on_transfer.all()],
        )

    @admin.display(description="Is deleted", boolean=True)
    def has_been_deleted(self, obj):
        return obj.is_deleted

    list_display = (
        "unique_id",
        "created_at",
        "last_updated",
        "has_been_deleted",
        "current_holder",
        "name",
        "asset_description",
        "asset_type_name",
        "status_display_name",
        "location__name",
        "serial_number",
        "security_tag_number",
        "get_send_user_email_on_transfer",
        "qr_tag",
        "transfer_url",
    )

    search_fields = (
        "name",
        "description",
        "asset_type__name",
        "status__status_type",
        "location__name",
        "serial_number",
        "security_tag_number",
        "current_holder__username",
        "transfers__to_user__username",
        "transfers__from_user__username",
    )
    list_filter = ("type__name", "status__status_type", "location__name")
    ordering = ("-deleted_at",)
    readonly_fields = ("created_at", "last_updated")
    filter_horizontal = ("send_user_email_on_transfer",)
    exclude = ("deleted_at", "restored_at", "transaction_id")

    def get_queryset(self, request):
        qs = (
            self.model.global_objects.select_related(
                "asset_type",
                "location",
                "current_holder",
            )
            .prefetch_related("transfers")
            .defer("id")
        )
        ordering = (
            self.ordering or ()
        )  # otherwise we might try to *None, which is bad ;)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


@admin.register(AssetTypeProxy)
class TypeAdmin(GlobalObjectsModelAdmin):
    search_fields = ("name", "description")
    ordering = ("-id",)
    readonly_fields = ("created_at", "last_updated")
    exclude = ("deleted_at", "restored_at", "transaction_id")

    @admin.display(description="Is deleted", boolean=True)
    def has_been_deleted(self, obj):
        return obj.is_deleted

    list_display = ("id", "name", "description", "has_been_deleted")

    def get_queryset(self, request):
        qs = self.model.global_objects.get_queryset()

        # we need this from the superclass method
        ordering = (
            self.ordering or ()
        )  # otherwise we might try to *None, which is bad ;)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


@admin.register(LocationProxy)
class LocationAdmin(GlobalObjectsModelAdmin):
    list_display = ("id", "name", "description", "has_been_deleted")
    search_fields = ("name", "description")
    ordering = ("-id",)
    readonly_fields = ("created_at", "last_updated")
    exclude = ("deleted_at", "restored_at", "transaction_id")

    @admin.display(description="Is deleted", boolean=True)
    def has_been_deleted(self, obj):
        return obj.is_deleted

    def get_queryset(self, request):
        qs = self.model.global_objects.get_queryset()

        # we need this from the superclass method
        ordering = (
            self.ordering or ()
        )  # otherwise we might try to *None, which is bad ;)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


@admin.register(StatusProxy)
class StatusAdmin(GlobalObjectsModelAdmin):
    fields = ["status_type"]
    list_display = ("status_type", "has_been_deleted")
    exclude = ("deleted_at", "restored_at", "transaction_id")

    @admin.display(description="Is deleted", boolean=True)
    def has_been_deleted(self, obj):
        return obj.is_deleted

    def get_queryset(self, request):
        qs = self.model.global_objects.get_queryset()

        # we need this from the superclass method
        ordering = (
            self.ordering or ()
        )  # otherwise we might try to *None, which is bad ;)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


@admin.register(AssetTransferProxy)
class AssetTransferAdmin(GlobalObjectsModelAdmin):
    list_display_links = None
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
        "asset__current_holder__username",
        "asset__current_holder__email",
        "asset__location__name",
        "asset__asset_type__name",
        "asset__status__status_type",
        "asset__serial_number",
        "asset__security_tag_number",
        "asset__name",
        "from_user__username",
        "to_user__username",
    )
    list_filter = ("asset__name", "from_user__username", "to_user__username")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "last_updated", "get_notes_text")
    exclude = ("deleted_at", "restored_at", "transaction_id")
    actions = ["soft_delete_selected", "restore_selected"]

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
