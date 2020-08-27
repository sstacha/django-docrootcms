"""
Markdown tags to convert markdown to HTML for rendering on the template
NOTE: templates will need to use |safe filter to show html and not the escaped text
"""
from django import template
from django.template.defaultfilters import stringfilter
from django.utils import timezone
import datetime
from markdownx.utils import markdownify

register = template.Library()


@register.filter
@stringfilter
def markdown_to_html(markdown_content):
    return markdownify(markdown_content)


@register.simple_tag
def time_since(timestamp=None):
    """
    Returns a humanized rstring representing time difference
    between now() and the input timestamp.

    The output rounds up to days, hours, minutes, or seconds.
    4 days 5 hours returns '4 days'
    0 days 4 hours 3 minutes returns '4 hours', etc...
    """
    rstr = ""
    if not timestamp or not isinstance(timestamp, datetime.datetime):
        return rstr

    now = timezone.now()
    timediff = now - timestamp
    days = timediff.days
    weeks = days//7
    months = days//30
    minutes = timediff.seconds % 3600 // 60
    seconds = timediff.seconds % 3600 % 60
    hours = minutes // 60

    if days > 365:
        return "> a year"
    if months > 0:
        if months == 1:
            tstr = "month"
        else:
            tstr = "months"
        rstr = rstr + "%s %s" % (months, tstr)
        return rstr
    if weeks > 0:
        if weeks == 1:
            tstr = "week"
        else:
            tstr = "weeks"
        rstr = rstr + "%s %s" % (weeks, tstr)
        return rstr
    if days > 0:
        if days == 1:
            tstr = "day"
        else:
            tstr = "days"
        rstr = rstr + "%s %s" % (days, tstr)
        return rstr
    elif hours > 0:
        if hours == 1:
            tstr = "hour"
        else:
            tstr = "hours"
        rstr = rstr + "%s %s" % (hours, tstr)
        return rstr
    elif minutes > 0:
        if minutes == 1:
            tstr = "min"
        else:
            tstr = "mins"
        rstr = rstr + "%s %s" % (minutes, tstr)
        return rstr
    elif seconds > 0:
        if seconds == 1:
            tstr = "sec"
        else:
            tstr = "secs"
        rstr = rstr + "%s %s" % (seconds, tstr)
        return rstr
    else:
        return "Now"
