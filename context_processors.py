from django.conf import settings  # import the settings file


def transfer_timeout(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {"TRANSFER_TIMEOUT": settings.TRANSFER_TIMEOUT}
