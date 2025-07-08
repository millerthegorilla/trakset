from django.conf import settings  # import the settings file


def transfer_timeout(request):
    return {"TRANSFER_TIMEOUT": settings.TRANSFER_TIMEOUT}


def app_user(request):
    return {"APP_USER": settings.APP_USER}
