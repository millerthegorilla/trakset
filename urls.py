from django.urls import path
from django.views.generic import TemplateView

from .views import AssetSearchView
from .views import AssetTransferCancelView
from .views import AssetTransferDetailView
from .views import AssetTransferView

app_name = "trakset"

urlpatterns = [
    path(
        "assets/transfer/<uuid:uuid>/",
        AssetTransferView.as_view(),
        name="asset_transfer",
    ),
    path(
        "assets/transfer/<uuid:pk>/cancel/",
        AssetTransferCancelView.as_view(),
        name="asset_transfer_cancel",
    ),
    path(
        "assets/transfer/notes_added/<uuid:uuid>/",
        TemplateView.as_view(template_name="asset_transfer_notes_added.html"),
        name="asset_transfer_notes_added",
    ),
    path(
        "assets/transfer/cancel_success/<str:deleted_transfer_id>/<str:deleted_transfer_from_user_name>/",
        TemplateView.as_view(template_name="asset_transfer_cancel_success.html"),
        name="asset_transfer_cancel_success",
    ),
    path(
        "assets/transfer/search/",
        AssetSearchView.as_view(template_name="asset_search.html"),
        name="asset_search",
    ),
    path(
        "assets/transfer/view/<uuid:pk>/",
        AssetTransferDetailView.as_view(),
        name="asset_transfer_detail_view",
    ),
]
