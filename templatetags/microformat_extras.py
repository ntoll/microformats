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
from django import template
from django.utils.translation import ugettext as _
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
# Well be using all the models at some point or other
import microformats.models
import datetime

register = template.Library()

##################################################################
# Constant field dictionaries for each Microformat containing information about
# those non-span, iregular or shortened fields.
#
# Where key = name of field and "inner" dict is:
#
#   'element': 'an html element' (e.g. 'span')
#   'class': 'the value of the class attribute' (e.g. 'longitude')
#
#   and an optional:
#
#   'attr': 
#       'name': 'the additional element attribute name'
#       'value': 'the prefic of the value of the attribute - e.g. "mailto:"
#
# You'll see what I mean when you look at the dicts
##################################################################
GEO_DICT = {
        'long': {
            'element': 'abbr',
            'class': 'longitude',
            'attr': {
                'name': 'title'
                }
            },
        'lat': {
            'element': 'abbr',
            'class': 'latitude',
            'attr': {
                'name': 'title'
                }
            }
        }

HCARD_DICT = {
        'email': {
            'element': 'a',
            'class': 'email',
            'attr': { 
                'name': 'href',
                'value': 'mailto:'
                }
            },
        'url': {
            'element': 'a',
            'class': 'url',
            'attr': {
                'name': 'href'
                }
            }
        }

def fragment(value, arg=None, autoescape=None, field_dict={}):
    """
    Generic utility function that will correctly process a microformat fragment
    using the given value, an appropriate arg, autoescape and a field_dict
    containing all the valid fields and related element and class information.
    field_dict[arg] should identify the appropriate field *or*, if missing,
    cause the return of the raw value thus.

    <span class="arg">value</span>

    Should arg contain a space separated list then only the first item is used
    for lookup with the others being appended to the class value. e.g.

    arg = 'url org'

    Will result in a lookup against 'url' to get the element and class
    information but will result in something like the following:

    ... class='url org' ...
    """
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    # Make sure we have an arg
    if arg:
        args = arg.split()
        a = args[0]
        # Can we find the arg in the dict..?
        if field_dict.has_key(a): 
            # what html element to use..?
            element = field_dict[a]['element']
            # make sure we have the full number of classes
            class_names = [field_dict[a]['class'],]
            class_names.extend(args[1:])
            klass = ' '.join(class_names) 
            if field_dict[a].has_key('attr'):
                # so we have an additional attribute
                name = field_dict[a]['attr']['name']
                if field_dict[a]['attr'].has_key('value'):
                    pre_val = field_dict[a]['attr']['value']
                else:
                    pre_val = ''
                attr = u'%s="%s%s"' % (name, pre_val, esc(value))
            result = u'<%s class="%s">%s</%s>' % (
                    element, 
                    klass, 
                    esc(value), 
                    element
                    )
        else:
            if isinstance(value, datetime.datetime):
                # check we have a datetime field that might need
                # formatting
                if len(args)>1:
                    # We're assuming these are strftime formatting instructions
                    format = str(' '.join(args[1:]).strip())
                else:
                    # Safe default
                    format = '%c'
                result = u'<abbr class="%s" title="%s">%s</abbr>' % (
                            esc(a),
                            esc(value.isoformat()),
                            esc(value.strftime(format))
                        )
            else:
                # if not just return the raw value in a span with arg as the class
                result = u'<span class="%s">%s</span>' % (esc(arg), esc(value))
    else:
        # We don't have an arg
        result = esc(value)
    return mark_safe(result)

@register.filter
def geo(value, arg=None, autoescape=None):
    """
    Formats a value to conform with the geo microformat.

    {{value|geo:"long"}}

    or

    {{geo_instance|geo}}

    or

    {{geo_instance|geo:"description"}}

    If rendering a fragment arg to be one of ['long', 'lat'] 

    If an instance of the geo model is passed as the value then arg is used as a
    descriptive fragment after the <div class="geo"> element. e.g.

    <div class="geo">
        Whatever you've supplied in the arg
        ...
    </div>

    See:

    http://microformats.org/wiki/geo

    geo (pronounced "gee-oh") is a simple format for marking up WGS84 geographic
    coordinates (latitude; longitude), suitable for embedding in HTML or XHTML,
    Atom, RSS, and arbitrary XML. geo is a 1:1 representation of the "geo"
    property in the vCard standard (RFC2426) in HTML, one of several open
    microformat standards. 
    """
    if isinstance(value, microformats.models.geo):
        # we have a geo model
        if autoescape:
            esc = conditional_escape
        else:
            esc = lambda x: x
        result = u'<div class="geo">%s&nbsp;'\
                 u'<abbr class="latitude" title="%s">%s</abbr>&nbsp;'\
                 u'<abbr class="longitude" title="%s">%s</abbr>'\
                 u'</div>' % (
                            arg and esc(arg) or '',
                            esc(value.latitude), 
                            value.latitude_description and 
                                esc(value.latitude_description) or
                                esc(value.latitude),
                            esc(value.longitude),
                            value.longitude_description and
                                esc(value.longitude_description) or
                                esc(value.longitude)
                            )
        return mark_safe(result)
    else:
        # we have something else 
        return fragment(value, arg, autoescape, GEO_DICT)
geo.needs_autoescape = True

@register.filter
def hcard(value, arg=None, autoescape=None):
    """ 
    Formats a value to conform with the hCard microformat.

    arg to be one of the field names referenced here:

    http://microformats.org/wiki/hcard-cheatsheet

    If an instance of the hCard model is passed as a value then the arg is not
    required.

    See:

    http://microformats.org/wiki/hcard

    hCard is a simple, open, distributed format for representing people,
    companies, organizations, and places, using a 1:1 representation of vCard
    (RFC2426) properties and values in semantic HTML or XHTML. hCard is one of
    several open microformat standards suitable for embedding in HTML, XHTML,
    Atom, RSS, and arbitrary XML. 
    
    Field help text is derived from Microformats site. See:

    http://microformats.org/wiki/hcard-singular-properties
    """
    if isinstance(value, microformats.models.hCard):
        # we have an hCard model
        if autoescape:
            esc = conditional_escape
        else:
            esc = lambda x: x

        # This gets quite complicated but I've based it upon the markup produced
        # by the hCard creator at:
        # http://microformats.org/code/hcard/creator
        content = list()

        # Start vcard div ------------------------------------------------>
        content.append(u'<div id="hcard_%s" class="vcard">' % (
                        esc(value.fn().replace(' ','_' ))
                        )
                )

        # Start fn block ------------------------------------------------->
        content.append(u'<div class="fn n">')
        if value.url:
            content.append(u'<a class="url" href="%s">' % (
                        esc(value.url)
                        )
                )
        # fn block 
        if value.n():
            # We have a valid name to markup
            if value.honorific_prefix:
                content.append(u'<span class="honorific_prefix">%s</span>&nbsp;' %
                        esc(value.honorific_prefix)
                    )
            if value.given_name:
                content.append(u'<span class="given-name">%s</span>&nbsp;' %
                        esc(value.given_name)
                    )
            if value.additional_name:
                content.append(u'<span class="additional-name">%s</span>&nbsp;' %
                        esc(value.additional_name)
                    )
            if value.family_name:
                content.append(u'<span class="family-name">%s</span>&nbsp;' %
                        esc(value.family_name)
                    )
            if value.honorific_suffix:
                content.append(u'<span class="honorific_suffix">%s</span>' %
                        esc(value.honorific_suffix)
                    )
        else:
            # Lets try to use an organization as the fn
            orgs = value.org_set.filter(primary=True).order_by('id')
            if orgs:
                o = orgs[0]
                content.append(u'<span class="org">%s</span>' % (
                        esc(o.name)
                        )
                    )
            else:
                # We don't seem to be able to find anything to act as fn so just
                # return what the model thinks should be the fn as a raw string
                return mark_safe(esc(value.fn()))
        if value.url:
            content.append(u'</a>')
        content.append(u'</div>')
        # End fn block --------------------------------------------------->

        # Start organisation block --------------------------------------->
        if value.n():
            # if we have a value.n() then the fn can't be an organisation so we
            # need to add any organisation information here:
            orgs = value.org_set.filter(primary=True).order_by('id')
            for o in orgs:
                if o.title:
                    content.append(u'<span class="title">%s</span>&nbsp;' % (
                                    esc(o.title)
                                    )
                            )
                content.append(u'<div class="org">')
                if o.unit:
                    content.append(u'<span class="organization-unit">'\
                            u'%s</span>,&nbsp;' % esc(o.unit))
                content.append(u'<span class="organization-name">'\
                            u'%s</span>' % esc(o.name))
                content.append(u'</div>')
        # End organisation block ----------------------------------------->

        # Email
        if value.email_set.all():
            for email in value.email_set.all():
                content.append(u'<a class="email" href="mailto:%s">%s</a><br/>' % (
                            esc(email.value),
                            esc(email.value)
                        )
                )

        # Address
        if value.adr_set.all():
            for address in value.adr_set.all():
                # lets piggy-back on the adr microformat
                content.append(adr(address, autoescape=autoescape))

        # Telephone number
        if value.tel_set.all():
            for tel in value.tel_set.all():
                content.append(u'<div class="tel">')
                content.append(u'<span class="value">%s</span>' % esc(tel.value))
                if tel.types.all():
                    content.append(u'&nbsp;[&nbsp;')
                    for type in tel.types.all():
                        content.append(u'<abbr class="type" title="%s">'\
                                        u'%s</abbr>&nbsp' % (
                                       esc(type.name),
                                       esc(type.get_name_display())
                                      )
                            )
                    content.append(u']')
                content.append(u'</div>')    

        # End vcard div -------------------------------------------------->
        content.append(u'</div>')
        result = ''.join(content) 
        return mark_safe(result)
    else:
        # we have something else 
        return fragment(value, arg, autoescape, HCARD_DICT)
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
    if isinstance(value, microformats.models.adr):
        # we have an adr model
        if autoescape:
            esc = conditional_escape
        else:
            esc = lambda x: x
        content = list()
        content.append(u'<div class="adr">')
        if value.types.all():
            content.append(u'<div>')
            for t in value.types.all():
                content.append(u'<abbr class="type" title="%s">'\
                                u'%s</abbr>&nbsp;' % (
                                esc(t.name),
                                esc(t.get_name_display())
                                )
                        )
            content.append(_('Address'))
            content.append(u'</div>')
        if value.street_address:
            content.append(u'<div class="street-address">%s</div>' % (
                            esc(value.street_address)
                            )
                    )
        if value.extended_address:
            content.append(u'<div class="extended-address">%s</div>' % (
                            esc(value.extended_address)
                            )
                    )
        if value.locality:
            content.append(u'<span class="locality">%s</span>&nbsp;' % (
                            esc(value.locality)
                            )
                    )
        if value.region:
            content.append(u'<span class="region">%s</span>&nbsp;' % (
                            esc(value.region)
                            )
                    )
        if value.postal_code:
            content.append(u'<span class="postal-code">%s</span>&nbsp;' % (
                            esc(value.postal_code)
                            )
                    )
        if value.country_name:
            content.append(u'<span class="region">%s</span>' % (
                            esc(value.get_country_name_display())
                            )
                    )
        content.append(u'</div>')
        result = ''.join(content)
        return mark_safe(result)
    else:
        # we have something else 
        return fragment(value, arg, autoescape)
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
    if isinstance(value, microformats.models.hCalendar):
        # we have an hCalendar model
        if autoescape:
            esc = conditional_escape
        else:
            esc = lambda x: x
        content = list()
        content.append(u'<div id="hcalendar_%s" class="vevent">' % (
                        esc(value.summary.replace(' ','_' ))
                        )
                    )
        # Start URL ------------------------------------------------>
        if value.url:
            content.append(u'<a href="%s" class="url">' % esc(value.url))
        
        if value.all_day_event:
            dtformat = '%a %b %d %Y'
        else:
            dtformat = '%a %b %d %Y, %I:%M%p'

        content.append(u'<abbr title="%s" class="dtstart">%s</abbr>' % (
                        esc(value.dtstart.isoformat()),
                        esc(value.dtstart.strftime(dtformat))
                        )
                    )
        if value.dtend:
            content.append(u'&nbsp;-&nbsp;')
            if value.dtend.date() == value.dtstart.date():
                if value.all_day_event:
                    end = esc(_(u'All day event'))
                else:
                    end = esc(value.dtend.strftime('%I:%M%p'))
            else:
                end = esc(value.dtend.strftime(dtformat))
            content.append(u'<abbr title="%s" class="dtend">%s</abbr>' % (
                        esc(value.dtend.isoformat()),
                        end
                        )
                    )
        content.append(u':&nbsp;')
        content.append(u'<span class="summary">%s</span>' % esc(value.summary))
        if value.location:
            content.append(esc(_(u' at ')))
            content.append(u'<span class="location">%s</span>' % esc(value.location))
        if value.url:
            content.append(u'</a>')
        # End URL ------------------------------------------------->
        if value.adr:
            content.append(adr(value.adr, autoescape=autoescape))
        if value.description:
            content.append(u'<p class="description">%s</p>' % ( 
                            esc(value.description)
                            )
                    )
        content.append(u'</div>')
        result = ''.join(content)
        return mark_safe(result)
    else:
        # we have something else 
        return fragment(value, arg, autoescape)
    pass
hcal.needs_autoescape = True

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
    if isinstance(value, microformats.models.xfn):
        # we have an xfn model
        vals = ' '.join(esc(x.value) for x in value.relationships.all())
        result = u'<a href="%s" rel="%s">%s</a>' % (
                            esc(value.url),
                            vals,
                            esc(value.target)
                            )
        return mark_safe(result)
    else:
        # we have something else 
        return mark_safe(esc(value))
xfn.needs_autoescape = True
