from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import TrigramSimilarity
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import View
from django.views.generic.edit import DeleteView

from trakset_app.tasks import email_users_on_asset_transfer

from .forms import AssetTransferNotesForm
from .models import Asset
from .models import AssetTransfer
from .models import AssetTransferNotes


# Create your views here.
@method_decorator(login_required, name="dispatch")
class AssetTransferView(FormView):
    model = AssetTransferNotes
    form_class = AssetTransferNotesForm
    template_name = "asset_transfer.html"
    success_url = "asset_transfer_success.html"

    def get(self, request, uuid, *args, **kwargs):
        super().get(request, *args, **kwargs)
        asset = Asset.objects.get(unique_id=uuid)
        asset_transfer = (
            AssetTransfer.objects.order_by("created_at").last()
            if AssetTransfer.objects.exists()
            else None
        )
        if (
            asset_transfer
            and asset_transfer.to_user == request.user
            and asset_transfer.was_transferred_recently()
        ):
            messages.warning(
                request,
                "This asset has been transferred to you recently. \
                 Do you want to cancel the transfer?",
            )
        else:
            asset_transfer = AssetTransfer.objects.create(
                asset=asset,
                from_user=asset.current_holder,
                to_user=request.user,
            )
            if asset_transfer.asset.send_user_email_on_transfer.exists():
                email_users_on_asset_transfer.delay(asset_transfer.id)
            asset.current_holder = request.user
            asset.save()
        context_data = self.get_context_data(**kwargs)
        context_data["transfer"] = asset_transfer
        return self.render_to_response(context_data)

    def get_form(self, form_class=None):
        """Override to pass the asset transfer instance to the form."""
        super().get_form(form_class)
        last_asset_transfer_notes = AssetTransferNotes.objects.filter(
            asset_transfer__asset__unique_id=self.kwargs["uuid"],
        ).last()
        if last_asset_transfer_notes:
            asset_transfer_text = last_asset_transfer_notes.text
        else:
            asset_transfer_text = ""
        asset_transfer_notes = AssetTransferNotes.objects.create(
            text=asset_transfer_text,
        )
        return AssetTransferNotesForm(instance=asset_transfer_notes)

    def get_context_data(self, **kwargs):
        super().get_context_data(**kwargs)
        asset = Asset.objects.get(unique_id=self.kwargs["uuid"])
        context = super().get_context_data(**kwargs)
        context["asset_name"] = asset.name
        context["asset_location"] = asset.location.name
        context["asset_id"] = str(self.kwargs["uuid"])
        return context

    def post(self, request, uuid):
        form = AssetTransferNotesForm(request.POST)
        asset_transfer = AssetTransfer.objects.filter(
            to_user=request.user,
            asset__unique_id=self.kwargs["uuid"],
        ).last()
        notes = asset_transfer.notes.last()
        form_text = form.data.get("text", "")
        if notes is None and form_text != "":
            asset_transfer.notes.create(text=form_text)
            asset_transfer.save()
        elif notes is not None:
            text_to_save = form_text
            asset_transfer.notes.create(text=text_to_save)
            asset_transfer.save()
        return redirect("trakset:asset_transfer_notes_added", uuid=uuid)


@method_decorator(login_required, name="dispatch")
class AssetTransferCancelView(DeleteView):
    template_name = "asset_confirm_cancel.html"
    success_url = "trakset:asset_transfer_cancel_success"
    model = AssetTransfer

    def form_valid(self, form):
        """Render the form again, with current form data and custom context."""
        context = self.get_context_data(form=form)
        transfer = context["object"]
        transfer.asset.current_holder = transfer.from_user
        transfer.asset.save()
        transfer_id = transfer.id
        transfer_from_user_name = transfer.from_user.username
        transfer.delete()
        context.pop("object")
        return redirect(
            reverse(
                "trakset:asset_transfer_cancel_success",
                kwargs={
                    "deleted_transfer_id": transfer_id,
                    "deleted_transfer_from_user_name": transfer_from_user_name,
                },
            ),
        )


# a view to choose an asset and view its asset_transfer history
@method_decorator(login_required, name="dispatch")
@method_decorator(staff_member_required, name="dispatch")
class AssetSearchView(View):
    template_name = "asset_search.html"

    def get(self, request, *args, **kwargs):
        context = {}
        search = request.GET.get("search", "")
        if not search:
            messages.info(request, "Please enter an asset name to search.")
            return render(request, self.template_name, context)
        assets = (
            Asset.objects.annotate(similarity=TrigramSimilarity("name", search))
            .filter(
                similarity__gt=0.2,
            )
            .order_by("-similarity")
        )
        if not assets:
            messages.info(request, "No assets found.")
        else:
            context.update(
                {"assets": assets, "search_type": request.GET.get("search_type")},
            )
            if request.GET.get("search_type") == "transfers":
                if request.GET.get("deleted_cb") == "on":
                    search_results = (
                        AssetTransfer.global_objects.select_related(
                            "asset",
                            "from_user",
                            "to_user",
                            "asset__type",
                            "asset__location",
                            "asset__status",
                        )
                        .filter(
                            asset=assets.first(),
                        )
                        .order_by("-created_at")
                        .only(
                            "id",
                            "asset__id",
                            "asset__name",
                            "created_at",
                            "from_user__username",
                            "to_user__username",
                            "asset__location__name",
                            "asset__type__name",
                            "asset__status__type",
                        )
                    )
                else:
                    search_results = (
                        AssetTransfer.objects.select_related(
                            "asset",
                            "from_user",
                            "to_user",
                            "asset__type",
                            "asset__location",
                            "asset__status",
                        )
                        .filter(
                            asset=assets.first(),
                        )
                        .order_by("-created_at")
                        .only(
                            "id",
                            "asset__id",
                            "asset__name",
                            "created_at",
                            "from_user__username",
                            "to_user__username",
                            "asset__location__name",
                            "asset__type__name",
                            "asset__status__type",
                        )
                    )
                if not search_results:
                    messages.info(request, "Asset has no asset transfer history.")
                else:
                    context.update(
                        {
                            "search_results": search_results,
                        },
                    )
            elif request.GET.get("search_type") == "assets":
                search_results = (
                    Asset.objects.select_related(
                        "type",
                        "location",
                        "status",
                    )
                    .filter(
                        id=assets.first().id,
                    )
                    .order_by("-created_at")
                    .only(
                        "current_holder",
                        "name",
                        "created_at",
                        "location__name",
                        "type__name",
                        "status__type",
                    )
                )
                if not search_results:
                    messages.info(request, "Error, unable to find asset.")
                else:
                    context.update(
                        {
                            "search_results": search_results,
                        },
                    )
        return render(request, self.template_name, context)


class AssetTransferDetailView(DetailView):
    template_name = "asset_transfer_detail.html"
    context_object_name = "asset_transfer"
    queryset = AssetTransfer.global_objects.all()
