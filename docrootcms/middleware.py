# Based off of flat pages but no database needed.  Concept is that we have dynamic
# urls based off of a docroot that extend from a template.  Each developer page is a template
# relative to DOCROOT_URL.  The purpose is to bypass having to enter urls for each page we build
# which would get out of hand quickly.  Furthermore, we would like to dynamically inject the
# data context for the page template to avoid having thousands of view functions that the url calls
# based on a naming convention (<dev_page_name>.data.py).  Templates must be named with the .dt extension
# so we and production web servers know what files to send to us to dynamically build.
import logging

from . import views as cms_views
# from django.http import Http404
# from django.conf import settings
# from django.core.exceptions import MiddlewareNotUsed

log = logging.getLogger("docroot.middleware")


# testing the new way of calling middleware
# make get_response=None to test for < 1.9 (see above)
class DocrootFallbackMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        log.info("DocrootFallbackMiddleware initialized...")
        # todo: use this example and import to disable our middleware based on a settings entry
        # raise MiddlewareNotUsed('DISABLE_MIDDLEWARE is set')

    def __call__(self, request):
        # code to be executed before the view/next middleware is called
        response = self.get_response(request)
        # code to be executed after the view/next middleware is called
        log.debug("DocrootFallbackMiddleware called: " + request.path_info)
        if response.status_code == 404:
            log.debug("got a response of 404 would have done something for: " + request.path_info)
            # will be called by apache for all 404's;
            # first attempt to load a static file (should we skip this if nginx arleady processed? DEBUG=FALSE?

            # attempt to load/render as static file
            result = cms_views.static(request)
            if result:
                log.debug("result is a static file...")
                response = result

            # attempt to load as template
            if not result and request.method=='GET':
                result = cms_views.page(request)
                if result:
                    log.debug("result is not none so returning it...")
                    response = result

            # attempt to load an api (determined by extension [.json, .xml etc])
            if not result:
                result = cms_views.api(request)
                if result:
                    log.debug("result is not none so returning it...")
                    response = result

        return response
