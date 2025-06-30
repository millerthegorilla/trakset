from django import forms
from django.utils.translation import gettext_lazy as _

from .models import AssetTransferNotes


class AssetTransferNotesForm(forms.ModelForm):
    class Meta:
        model = AssetTransferNotes
        fields = ["text"]
        labels = {
            "text": _("Notes"),
        }
        help_texts = {
            "text": _("Any additional information regarding the transfer."),
        }
