from django.conf import settings
from django.utils.timezone import activate
# from django.core.exceptions import MiddlewareNotUsed
import pytz


class TZMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # NOTE: I decided not to auto load this since everyone may want to set up timezones differently
        #   todo: add to both projects instructions
        # if 'docrootcms' in settings.INSTALLED_APPS:
        #     raise MiddlewareNotUsed("Disabling TZMiddleware because docrootcms in INSTALLED_APPS")
        if settings.DEFAULT_TZ:
            print(f'TZMiddleware defaulting timezone to [{settings.DEFAULT_TZ}]')

    def __call__(self, request):
        # start by activating our default tz if defined; we can override on call later if they have a profile set
        if settings.DEFAULT_TZ:
            activate(pytz.timezone(settings.DEFAULT_TZ))
        return self.get_response(request)
