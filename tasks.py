from celery import shared_task
from django.core.mail import send_mail

from trakset.models import AssetTransfer
from trakset_app.users.models import User


@shared_task()
def email_admin_on_error(error_message):
    """Email the admin user when an error is encountered."""
    emails = [
        user.email for user in User.objects.filter(is_superuser=True) if user.email
    ]
    send_mail(
        "An error occurred in trakset!",
        f"Hey from trakset!\n\nError details:\n{error_message}",
        "webmaster@mindq.co.uk",
        emails,
    )
    return "Admin emailed on error."


@shared_task()
def email_users_on_asset_transfer(asset_transfer_id):
    """Email the list of users that are subscribed to this assset transfer."""
    try:
        asset_transfer = AssetTransfer.objects.get(id=asset_transfer_id)
    except AssetTransfer.DoesNotExist:
        return "Asset transfer not found."
    users = asset_transfer.asset.send_user_email_on_transfer.all()
    emails = [user.email for user in users if user.email]
    if emails:
        send_mail(
            "An asset that you are subscribed to has been transferred...",
            "Hey from trakset!",
            "webmaster@mindq.co.uk",
            emails,
            html_message=(
                f"<html>Hi from the Mind Assets App!<br><br>The asset \
                <b>{asset_transfer.asset.name}</b> that is based \
                at <b>{asset_transfer.asset.location}</b> has been transferred. \
                The current holder is <b>{asset_transfer.to_user.username}</b> \
                whose email address is <b>{asset_transfer.to_user.email}</b> \
                The asset transfer id is <b>{asset_transfer.id}</b></html>"
            ),
        )
        return "Email sent to users on asset transfer."
    return "No users to email on asset transfer."
