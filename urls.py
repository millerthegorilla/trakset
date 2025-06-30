from django.urls import path
from django.views.generic import TemplateView

from .views import AssetTransferCancelView
from .views import AssetTransferDetailView
from .views import AssetTransferHistoryView
from .views import AssetTransferView

app_name = "trakset"

urlpatterns = [
    path(
        "asset_transfer/<uuid:uuid>/",
        AssetTransferView.as_view(),
        name="asset_transfer",
    ),
    path(
        "asset_transfer/<uuid:pk>/cancel/",
        AssetTransferCancelView.as_view(),
        name="asset_transfer_cancel",
    ),
    path(
        "asset_transfer/notes_added/<uuid:uuid>/",
        TemplateView.as_view(template_name="asset_transfer_notes_added.html"),
        name="asset_transfer_notes_added",
    ),
    path(
        "asset_transfer/cancel_success/",
        TemplateView.as_view(template_name="asset_transfer_cancel_success.html"),
        name="asset_transfer_cancel_success",
    ),
    path(
        "asset_transfer/history/",
        AssetTransferHistoryView.as_view(template_name="asset_transfer_history.html"),
        name="asset_transfer_history",
    ),
    path(
        "asset_transfer/view/<uuid:pk>/",
        AssetTransferDetailView.as_view(),
        name="asset_transfer_detail_view",
    ),
]
