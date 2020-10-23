import re
from django.conf import settings
from django.http import JsonResponse
from datetime import datetime

# static context definition
context = {}


# dynamic context return
# NOTE: don't forget to use .update to add/replace instead of = which will ignore static definition
def get_context(request):
    regex_http_ = re.compile(r'^HTTP_.+$')
    regex_content_type = re.compile(r'^CONTENT_TYPE$')
    regex_content_length = re.compile(r'^CONTENT_LENGTH$')

    request_headers = {}
    for header in request.META:
        if regex_http_.match(header) or regex_content_type.match(header) or regex_content_length.match(header):
            request_headers[header] = request.META[header]

    b = getattr(settings, "BOOGER", "")
    b2 = getattr(settings, "BOOGER2", "")
    request_ip = request.META.get('REMOTE_ADDR')
    real_ip = request.META.get('HTTP_X_REAL_IP')
    context.update({'headers': request_headers, 'request_ip': str(request_ip), 'real_ip': str(real_ip), 'b': b, 'b2': b2})
    return context


# web service definitions
# NOTE: if not defined or commented will return 405-method not supported if called
#   if no data file or no web service methods defined returns 404-not found
# BEST PRACTICE: GET does not update only reads and returns data
def GET(request):
    ctx = get_context(request)
    now = datetime.now()
    ctx['freshness_date'] = str(now)
    return JsonResponse(ctx, safe=False)
#
#
# BEST PRACTICE: POST inserts/updates a single record and returns data/response (form post encoded body)
# def POST(request):
#     pass
#
#
# BEST PRACTICE: PUT inserts/updates record(s) and returns data/response (various body formats like json/xml etc)
# def PUT(request):
#     pass
#
#
# BEST PRACTICE: DELETE deletes (maybe soft delete like marking record deleted) record and returns data/response
#   best practice is to pass just unique identifier not a lot complete data set
# def DELETE(request):
#     pass
