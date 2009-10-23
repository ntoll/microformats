# -*- coding: UTF-8 -*-
"""
Custom Django template filters and template tags for Microformats. 

Copyright (c) 2009 Nicholas H.Tollervey (http://ntoll.org/contact)

All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in
the documentation and/or other materials provided with the
distribution.
* Neither the name of ntoll.org nor the names of its
contributors may be used to endorse or promote products
derived from this software without specific prior written
permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
from django.template import Template, Context
from django import template
from django.template.loader import select_template
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.forms.fields import email_re, url_re
# We'll be using all the models at some point or other
import microformats.models
import datetime

################################################
# Default templates (over-ridden in settings.py)
################################################
GEO_MICROFORMAT_TEMPLATE = 'geo.html'
HCARD_MICROFORMAT_TEMPLATE = 'hcard.html'
HCAL_MICROFORMAT_TEMPLATE = 'hcal.html'
HLISTING_MICROFORMAT_TEMPLATE = 'hlisting.html'
HREVIEW_MICROFORMAT_TEMPLATE = 'hreview.html'
ADR_MICROFORMAT_TEMPLATE = 'adr.html'
HFEED_MICROFORMAT_TEMPLATE = 'hfeed.html'
HENTRY_MICROFORMAT_TEMPLATE = 'hentry.html'
HNEWS_MICROFORMAT_TEMPLATE = 'hnews.html'

# For registering the templates
register = template.Library()

########################
# Some utility functions
########################

def is_valid_email(email):
    """ 
    Is the string a valid email? 
    
    (We use the regex Django uses to define an email address)
    """
    return True if email_re.match(email) else False

def is_valid_url(url):
    """ 
    Is the string a valid url? 
    
    (We use the regex Django uses to define a URL)
    """
    return True if url_re.match(url) else False

def fragment(value, arg, autoescape=None):
    """
    A generic utility function that takes the value and arg and returns a
    <span> enclosed version.

    The arg should contain the contents of what is to be the class attribute of
    the <span> element.

    For example, where value = "Microsoft" and arg = "org fn" then the result
    will be:

    <span class="org fn">Microsoft</span>

    The function does inspect the value type and attempts to select the most
    appropriate element for display (99.9% of the time this will be a <span>
    element, but for the case of datetime values <abbr> is more appropriate). It
    also checks if the arg is either longitude or latitude and uses the more
    appropriate <abbr> element.

    In the case of a datetime value only the first arg will be used for the
    class, anything else will be assumed to be arguments for strftime. e.g. an
    arg containing "dtstart %a %d %b %y" will result in "dtstart" as the <attr>
    class and the rest as arguments for date/time formatting:

    <abbr class="dtstart" title="2009-05-03">Sun 3 May 2009</abbr>

    Verging of the redundant, this function *does* save typing, incorporates
    some useful heuristics and abstracts the output of individual field values 
    in a neat way.
    """
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    # Make sure we have an arg
    if arg:
        if isinstance(value, datetime.datetime):
            # check we have a datetime field that might need
            # formatting
            args = arg.split()
            klass = args[0]
            if len(args)>1:
                # We're assuming these are strftime formatting instructions
                format = str(' '.join(args[1:]).strip())
            else:
                # Safe default
                format = '%c'
            result = u'<abbr class="%s" title="%s">%s</abbr>' % (
                            esc(klass),
                            esc(value.isoformat()),
                            esc(value.strftime(format))
                        )
        elif arg == 'longitude' or arg == 'latitude' or arg == 'long' or arg == 'lat':
            # Check for geo related fields so we can use the abbr pattern
            if arg == 'latitude' or arg == 'lat':
                klass = u'latitude'
            else:
                klass = u'longitude'
            result = u'<abbr class="%s" title="%s">%s</abbr>' % (
                            esc(klass),
                            esc(value),
                            esc(value)
                        )
        elif is_valid_email(esc(value)):
            # If the field is an email address we need to wrap it in an anchor
            # element
            result = u'<a class="%s" href="mailto:%s">%s</a>'%(
                            esc(arg),
                            esc(value), 
                            esc(value)
                        )
        elif is_valid_url(esc(value)):
            # If the field is a URL we need to wrap it in an anchor element
            result = u'<a class="%s" href="%s">%s</a>'%(
                            esc(arg),
                            esc(value), 
                            esc(value)
                        )
        else:
            # if not just return the raw value in a span with arg as the class
            result = u'<span class="%s">%s</span>' % (esc(arg), esc(value))
    else:
        # We don't have an arg
        result = esc(value)
    return mark_safe(result)

def render_microformat(instance, template_name):
    """
    A generic function that simply takes an instance of a microformat and a
    template name, creates an appropriate context object and returns the rendered
    result.
    """
    template = select_template([template_name,])
    adr_template = getattr(settings, 'ADR_MICROFORMAT_TEMPLATE', False) and settings.ADR_MICROFORMAT_TEMPLATE or ADR_MICROFORMAT_TEMPLATE
    context = Context({
        'instance': instance,
        'adr_microformat_template': adr_template,
        })
    return template.render(context)

@register.filter
def geo(value, arg=None, autoescape=None):
    """
    Formats a value to conform with the geo microformat.

    {{value|geo:"longitude"}}

    or

    {{geo_instance|geo}}

    If rendering a fragment arg to be one of:
    
    ['long', 'lat', 'longitude', 'latitude'] 

    See:

    http://microformats.org/wiki/geo

    geo (pronounced "gee-oh") is a simple format for marking up WGS84 geographic
    coordinates (latitude; longitude), suitable for embedding in HTML or XHTML,
    Atom, RSS, and arbitrary XML. geo is a 1:1 representation of the "geo"
    property in the vCard standard (RFC2426) in HTML, one of several open
    microformat standards. 
    """
    if isinstance(value, datetime.datetime) or isinstance(value, str) or isinstance(value, unicode) or isinstance(value, float) or isinstance(value, int) or isinstance(value, long) or isinstance(value, complex):
        return fragment(value, arg, autoescape)
    else:
        # lets try rendering something with the correct attributes for this
        # microformat
        template_name = getattr(settings, 'GEO_MICROFORMAT_TEMPLATE', False) and settings.GEO_MICROFORMAT_TEMPLATE or GEO_MICROFORMAT_TEMPLATE
        return mark_safe(render_microformat(value, template_name))
geo.needs_autoescape = True

@register.filter
def hcard(value, arg=None, autoescape=None):
    """ 
    Formats a value to conform with the hCard microformat.

    arg to be one of the field names referenced here:

    http://microformats.org/wiki/hcard-cheatsheet

    If an instance of the hCard model is passed as a value then the arg is not
    required and the microformat will be rendered using the hcard template
    specified in settings.HCARD_MICROFORMAT_TEMPLATE (attempts to default to 
    the one found in the templates directory of this application).

    See:

    http://microformats.org/wiki/hcard

    hCard is a simple, open, distributed format for representing people,
    companies, organizations, and places, using a 1:1 representation of vCard
    (RFC2426) properties and values in semantic HTML or XHTML. hCard is one of
    several open microformat standards suitable for embedding in HTML, XHTML,
    Atom, RSS, and arbitrary XML. 
    """
    if isinstance(value, datetime.datetime) or isinstance(value, str) or isinstance(value, unicode) or isinstance(value, float) or isinstance(value, int) or isinstance(value, long) or isinstance(value, complex):
        return fragment(value, arg, autoescape)
    else:
        # lets try rendering something with the correct attributes for this
        # microformat
        template_name = getattr(settings, 'HCARD_MICROFORMAT_TEMPLATE', False) and settings.HCARD_MICROFORMAT_TEMPLATE or HCARD_MICROFORMAT_TEMPLATE
        return mark_safe(render_microformat(value, template_name))
hcard.needs_autoescape = True

@register.filter
def adr(value, arg=None, autoescape=None):
    """ 
    Formats a value to conform with the adr Microformat.

    args to be one of the field names referenced here:

    http://microformats.org/wiki/adr-cheatsheet

    If an instance of the adr model is passed as a value then the arg is not
    required.
    
    See:

    http://microformats.org/wiki/adr

    adr (pronounced "adder"; FAQ: "why 'adr'?") is a simple format for marking
    up address information, suitable for embedding in HTML, XHTML, Atom, RSS,
    and arbitrary XML. adr is a 1:1 representation of the adr property in the
    vCard standard (RFC2426) in HTML, one of several open microformat standards.
    It is also a property of hCard. 
    """
    if isinstance(value, datetime.datetime) or isinstance(value, str) or isinstance(value, unicode) or isinstance(value, float) or isinstance(value, int) or isinstance(value, long) or isinstance(value, complex):
        return fragment(value, arg, autoescape)
    else:
        # lets try rendering something with the correct attributes for this
        # microformat
        template_name = getattr(settings, 'ADR_MICROFORMAT_TEMPLATE', False) and settings.ADR_MICROFORMAT_TEMPLATE or ADR_MICROFORMAT_TEMPLATE
        return mark_safe(render_microformat(value, template_name))
adr.needs_autoescape = True

@register.filter
def hcal(value, arg=None, autoescape=None):
    """
    Formats a value to conform with the hCalendar Microformat. 

    args to be one of the field names referenced here:

    http://microformats.org/wiki/hcalendar-cheatsheet

    If an instance of the hCalendar model is passed as a value then the arg is
    not required.

    Inspired by the markup found here:

    http://microformats.org/code/hcalendar/creator

    For more information see:

    http://microformats.org/wiki/hcalendar

    hCalendar is a simple, open, distributed calendaring and events format,
    based on the iCalendar standard (RFC2445), suitable for embedding in HTML or
    XHTML, Atom, RSS, and arbitrary XML. hCalendar is one of several open
    microformat standards. 
    """
    if isinstance(value, datetime.datetime) or isinstance(value, str) or isinstance(value, unicode) or isinstance(value, float) or isinstance(value, int) or isinstance(value, long) or isinstance(value, complex):
        return fragment(value, arg, autoescape)
    else:
        # lets try rendering something with the correct attributes for this
        # microformat
        template_name = getattr(settings, 'HCAL_MICROFORMAT_TEMPLATE', False) and settings.HCAL_MICROFORMAT_TEMPLATE or HCAL_MICROFORMAT_TEMPLATE
        return mark_safe(render_microformat(value, template_name))
hcal.needs_autoescape = True

@register.filter
def hlisting(value, arg=None, autoescape=None):
    """
    Formats a value to conform with the hListing Microformat
    """
    if isinstance(value, datetime.datetime) or isinstance(value, str) or isinstance(value, unicode) or isinstance(value, float) or isinstance(value, int) or isinstance(value, long) or isinstance(value, complex):
        return fragment(value, arg, autoescape)
    else:
        # lets try rendering something with the correct attributes for this
        # microformat
        template_name = getattr(settings, 'HLISTING_MICROFORMAT_TEMPLATE', False) and settings.HLISTING_MICROFORMAT_TEMPLATE or HLISTING_MICROFORMAT_TEMPLATE
        return mark_safe(render_microformat(value, template_name))
hlisting.needs_autoescape = True

@register.filter
def hreview(value, arg=None, autoescape=None):
    """
    Formats a value to conform with the hReview Microformat
    
    Inspired by the markup found here:

    http://microformats.org/code/hreview/creator
    """
    if isinstance(value, datetime.datetime) or isinstance(value, str) or isinstance(value, unicode) or isinstance(value, float) or isinstance(value, int) or isinstance(value, long) or isinstance(value, complex):
        return fragment(value, arg, autoescape)
    else:
        # lets try rendering something with the correct attributes for this
        # microformat
        template_name = getattr(settings, 'HREVIEW_MICROFORMAT_TEMPLATE', False) and settings.HREVIEW_MICROFORMAT_TEMPLATE or HREVIEW_MICROFORMAT_TEMPLATE
        return mark_safe(render_microformat(value, template_name))
hreview.needs_autoescape = True

@register.filter
def xfn(value, arg=None, autoescape=None):
    """
    Formats an instance of the xfn model to conform with the XFN microformat.

    XFN™ (XHTML Friends Network) is a simple way to represent human
    relationships using hyperlinks. In recent years, blogs and blogrolls have
    become the fastest growing area of the Web. XFN enables web authors to
    indicate their relationship(s) to the people in their blogrolls simply by
    adding a 'rel' attribute to their <a href> tags, e.g.:

    <a href="http://jeff.example.org" rel="friend met">... 
    """
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    if isinstance(value, datetime.datetime) or isinstance(value, str) or isinstance(value, unicode) or isinstance(value, float) or isinstance(value, int) or isinstance(value, long) or isinstance(value, complex):
        return mark_safe(esc(value))
    else:
        # lets try rendering something with the correct attributes for this
        # microformat
        vals = ' '.join(esc(x.value) for x in value.relationships.all())
        result = u'<a href="%s" rel="%s">%s</a>' % (
                            esc(value.url),
                            vals,
                            esc(value.target)
                            )
        return mark_safe(result)
xfn.needs_autoescape = True

@register.filter
def hfeed(value, arg=None, autoescape=None):
    """
    Formats a value to conform with the hFeed Microformat fragment
    
    Inspired by the markup found here:

    http://microformats.org/wiki/hatom-examples
    """
    if isinstance(value, datetime.datetime) or isinstance(value, str) or isinstance(value, unicode) or isinstance(value, float) or isinstance(value, int) or isinstance(value, long) or isinstance(value, complex):
        return fragment(value, arg, autoescape)
    else:
        # lets try rendering something with the correct attributes for this
        # microformat
        template_name = getattr(settings, 'HFEED_MICROFORMAT_TEMPLATE', False) and settings.HFEED_MICROFORMAT_TEMPLATE or HFEED_MICROFORMAT_TEMPLATE
        return mark_safe(render_microformat(value, template_name))
hfeed.needs_autoescape = True

@register.filter
def hentry(value, arg=None, autoescape=None):
    """
    Formats a value to conform with the hEntry Microformat fragment
    
    Inspired by the markup found here:

    http://microformats.org/wiki/hatom-examples
    """
    if isinstance(value, datetime.datetime) or isinstance(value, str) or isinstance(value, unicode) or isinstance(value, float) or isinstance(value, int) or isinstance(value, long) or isinstance(value, complex):
        return fragment(value, arg, autoescape)
    else:
        # lets try rendering something with the correct attributes for this
        # microformat
        template_name = getattr(settings, 'HENTRY_MICROFORMAT_TEMPLATE', False) and settings.HENTRY_MICROFORMAT_TEMPLATE or HENTRY_MICROFORMAT_TEMPLATE
        return mark_safe(render_microformat(value, template_name))
hentry.needs_autoescape = True

@register.filter
def hnews(value, arg=None, autoescape=None):
    """
    Formats a value to conform with the hNews Microformat fragment
    
    Inspired by the markup found here:

    http://microformats.org/wiki/hnews-examples
    """
    if isinstance(value, datetime.datetime) or isinstance(value, str) or isinstance(value, unicode) or isinstance(value, float) or isinstance(value, int) or isinstance(value, long) or isinstance(value, complex):
        return fragment(value, arg, autoescape)
    else:
        # lets try rendering something with the correct attributes for this
        # microformat
        template_name = getattr(settings, 'HNEWS_MICROFORMAT_TEMPLATE', False) and settings.HNEWS_MICROFORMAT_TEMPLATE or HNEWS_MICROFORMAT_TEMPLATE
        return mark_safe(render_microformat(value, template_name))
hentry.needs_autoescape = True