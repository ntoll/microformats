# -*- coding: UTF-8 -*-
"""
Models for Microformats. 

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
from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext as __
from django.contrib.auth.models import User
from datetime import date

########################################
# Constant tuples used in several models
########################################

# Timezone representation taken from the hCalendar creator:
# http://microformats.org/code/hcalendar/creator
TIMEZONE = (
        ('-12:00', _('-12 (IDLW)')),
        ('-11:00', _('-11 (NT)')),
        ('-10:00', _('-10 (HST)')),
        ('-09:00', _('-9 (AKST)')),
        ('-08:00', _('-8 (PST/AKDT)')),
        ('-07:00', _('-7 (MST/PDT)')),
        ('-06:00', _('-6 (CST/MDT)')),
        ('-05:00', _('-5 (EST/CDT)')),
        ('-04:00', _('-4 (AST/EDT)')),
        ('-03:45', _('-3:45')),
        ('-03:30', _('-3:30')),
        ('-03:00', _('-3 (ADT)')),
        ('-02:00', _('-2 (AT)')),
        ('-01:00', _('-1 (WAT)')),
        ('Z', _('+0 (GMT/UTC)')),
        ('+01:00', _('+1 (CET/BST/IST/WEST)')),
        ('+02:00', _('+2 (EET/CEST)')),
        ('+03:00', _('+3 (MSK/EEST)')),
        ('+03:30', _('+3:30 (Iran)')),
        ('+04:00', _('+4 (ZP4/MSD)')),
        ('+04:30', _('+4:30 (Afghanistan)')),
        ('+05:00', _('+5 (ZP5)')),
        ('+05:30', _('+5:30 (India)')),
        ('+06:00', _('+6 (ZP6)')),
        ('+06:30', _('+6:30 (Burma)')),
        ('+07:00', _('+7 (WAST)')),
        ('+08:00', _('+8 (WST)')),
        ('+09:00', _('+9 (JST)')),
        ('+09:30', _('+9:30 (Central Australia)')),
        ('+10:00', _('+10 (AEST)')),
        ('+11:00', _('+11 (AEST(summer))')),
        ('+12:00', _('+12 (NZST/IDLE)')),
        )

########
# Models
########

class geo(models.Model):
    """
    Represents the geo microformat.

    See:

    http://microformats.org/wiki/geo

    geo (pronounced "gee-oh") is a simple format for marking up WGS84 geographic
    coordinates (latitude; longitude), suitable for embedding in HTML or XHTML,
    Atom, RSS, and arbitrary XML. geo is a 1:1 representation of the "geo"
    property in the vCard standard (RFC2426) in HTML, one of several open
    microformat standards. 
    """

    latitude = models.FloatField(
            _('Latitude'),
            help_text=_(u'degrees decimal, e.g. 37.408183 (±90)')
            )
    latitude_description = models.CharField(
            _('Latitude description'),
            max_length=32,
            help_text=_(u'e.g. N 37° 24.491'),
            blank=True
            )
    longitude = models.FloatField(
            _('Longitude'),
            help_text=_(u'degrees decimal, e.g. -122.13855 (±180)')
            )
    longitude_description = models.CharField(
            _('Longitude description'),
            max_length=32,
            help_text=_(u'e.g. W 122° 08.313'),
            blank=True
            )

    class Meta:
        verbose_name = _('Geolocation')
        verbose_name_plural = _('Geolocations')

    def __unicode__(self):
        return ' '.join((
            'lat', 
            str(self.latitude), 
            'long', 
            str(self.longitude)
            ))

class hCard(models.Model):
    """ 
    Represents an hCard microformat.

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
    family_name = models.CharField(
            _('Family Name'),
            max_length=64,
            blank=True,
            help_text=_('Surname')
            )
    given_name = models.CharField(
            _('Given Name'),
            max_length=64,
            blank=True,
            help_text=_('Forename')
            )
    additional_name = models.CharField(
            _('Additional Name(s)'),
            max_length=128,
            blank=True,
            help_text=_('e.g. middle names')
            )
    honorific_prefix = models.CharField(
            _('Honorific Prefix'),
            max_length=32,
            blank=True,
            help_text=_('e.g. Dr, Professor etc')
            )
    honorific_suffix = models.CharField(
            _('Honorific Suffix'),
            max_length=32,
            blank=True,
            help_text=_('e.g. BA, MSc etc')
            )
    nickname = models.CharField(
            _('Nickname'),
            max_length=64,
            blank=True,
            help_text=_('For recording nicknames, handles, usernames etc...')
            )
    # A person only has a single physical birthday (reincarnation cannot be 
    # scientifically substantiated and thus constitues the creation of a new 
    # directory object rather than the re-birth of an existing object, and 
    # being 'born again' is not the physical event that 'bday' represents). 
    # Thus 'bday' is singular.
    bday = models.DateField(
            _('Date of Birth'),
            null=True,
            blank=True
            )
    geo = models.ForeignKey(
            geo, 
            null=True,
            help_text=_("The 'geo' property represents the contact's actual"\
                " location, not a coordinate approximation of an 'adr'.")
            )
    # A URL for the person or organization represented by this hCard
    url = models.URLField(
            _('URL'),
            verify_exists=False,
            blank=True,
            help_text=_("e.g. http://www.company.com/")
            )
    # The tz property represents the contact's current timezone.
    tz = models.CharField(
            _('Timezone'),
            max_length=8,
            blank=True,
            choices=TIMEZONE,
            help_text=_("Hour(s) from GMT")
            )
    # When sorting a name, it doesn't make sense for it to have more than one
    # way of sorting it, thus "sort-string" must be singular.
    sort_string = models.CharField(
            _('Sort String'),
            max_length=32,
            blank=True,
            help_text=_("The sort string used when sorting this contact.")
            )
    # The "uid" property is a globally unique identifier corresponding to the
    # individual or resource associated with the hCard. It doesn't make sense
    # for an hCard to have more than one "uid". 
    uid = models.CharField(
            _('UID'),
            max_length=128,
            blank=True,
            help_text=_('Globally Unique ID')
            )
    # The "class" property indicates the confidentiality/access classification
    # of the hCard as a whole, and thus it only makes sense for there to be one
    # (or rather, makes no sense for there to be more than one).
    klass = models.CharField(
            _('Class'),
            max_length=128,
            blank=True,
            help_text=_("The 'class' property indicates the"\
                " confidentiality / access classification of the contact.")
            )
    # The 'rev' property represents the datetime of the revision of the hCard as
    # a whole.
    # Why not use auto_now = True..? Well, this is the (optional) timestamp for
    # the hCard *as a whole* so revisions to data not stored in this table
    # should also cause the 'rev' to be updated. As a result, it is left to the
    # application to control this behaviour.
    rev = models.DateTimeField(
            _('Revision'),
            null=True,
            blank=True,
            help_text=_("Last revised on")
            )
    # Specifies information about other contact(s) acting on behalf of the
    # entity represented by the hCard 
    agents = models.ManyToManyField(
            "self", 
            symmetrical=False
            )

    def n(self):
        """
        Uses the values in honorific-prefix, given-name, additional-name,
        family-name and honorific-suffix to build a name "n".

        Ensures that *at least* given-name, additional-name and family-name
        produce something useful.

        Legal precedents afford a person a single given-name (with multiple
        additional-name(s)) and single family-name, thus, only a single "n"
        property is permitted.
        """
        name = ' '.join((i for i in (
            self.given_name,
            self.additional_name,
            self.family_name) if i.strip()))
        if name:
            return ' '.join((i for i in(
                self.honorific_prefix,
                name,
                self.honorific_suffix) if i.strip()))
        else:
            return '' 

    def fn(self, is_org=False):
        """
        Formatted Name

        Use is_org=True to use organization name if this hCard represents an
        organization. Otherwise this method returns self.n(). If self.n()
        returns nothing then an attempt is made to return an org. If all else
        fails returns 'None'

        A person has only one "best" / most preferred way of formatting their
        name, and legally organizations have only a single name, thus "fn" is
        singular. 
        """
        result = ''
        if is_org:
            o = self.org_set.filter(primary=True).order_by('id')
            if o:
                result = o[0].__unicode__()
            else:
                result = self.n()
        else:
            result = self.n()
            if not result:
                # check we have an organization we should use instead
                o = self.org_set.filter(primary=True).order_by('id')
                if o:
                    result = o[0].__unicode__()

        if result:
            return result
        else:
            return _('None')

    class Meta:
        verbose_name = _('hCard')
        verbose_name_plural = _('hCards')

    def __unicode__(self):
        return self.fn()

class adr_type(models.Model):
    """
    Represents a type of adr Microformat

    See:
    
    http://microformats.org/wiki/hcard#adr_tel_email_types

    Also see: http://www.ietf.org/rfc/rfc2426.txt (quoted below)

    The type parameter values can include:

    "dom" to indicate a domestic delivery address; "intl" to indicate an
    international delivery address; "postal" to indicate a postal
    delivery address; "parcel" to indicate a parcel delivery address;
    "home" to indicate a delivery address for a residence; "work" to
    indicate delivery address for a place of work; and "pref" to indicate
    the preferred delivery address when more than one address is specified.

    """

    TYPE_LIST = (
            ('dom', _('Domestic')),
            ('intl', _('International')),
            ('postal', _('Postal')),
            ('parcel', _('Parcel')),
            ('home', _('Home')),
            ('work', _('Work')),
            ('pref', _('Preferred')),
            )

    name = models.CharField(
            _('Address Type'),
            max_length=8,
            choices=TYPE_LIST,
            default='intl'
            )

    class Meta:
        verbose_name = _('Address Type')
        verbose_name_plural = _('Address Types')

    def __unicode__(self):
        return self.get_name_display()

class adr(models.Model):
    """ 
    Represents an adr Microformat.
    
    See:

    http://microformats.org/wiki/adr

    adr (pronounced "adder"; FAQ: "why 'adr'?") is a simple format for marking
    up address information, suitable for embedding in HTML, XHTML, Atom, RSS,
    and arbitrary XML. adr is a 1:1 representation of the adr property in the
    vCard standard (RFC2426) in HTML, one of several open microformat standards.
    It is also a property of hCard. 
    """

    # A list of all countries stored as (('ISO 3166'), ('Name')) 
    COUNTRY_LIST = (
        ('',_('--- Please Select ---')),
        ('GB', _('United Kingdom')),
        ('US', _('United States')),
        ('CA', _('Canada')),
        ('AU', _('Australia')),
        ('NZ', _('New Zealand')),
        ('IE', _('Ireland')),
        ('FR', _('France')),
        ('DE', _('Germany')),
        ('IT', _('Italy')),
        ('ES', _('Spain')),
        ('AF', _('Afghanistan')),
        ('AL', _('Albania')),
        ('DZ', _('Algeria')),
        ('AS', _('American Samoa')),
        ('AD', _('Andorra')),
        ('AO', _('Angola')),
        ('AI', _('Anguilla')),
        ('AQ', _('Antarctica')),
        ('AG', _('Antigua and Barbuda')),
        ('AR', _('Argentina')),
        ('AM', _('Armenia')),
        ('AW', _('Aruba')),
        ('AT', _('Austria')),
        ('AZ', _('Azerbaidjan')),
        ('BS', _('Bahamas')),
        ('BH', _('Bahrain')),
        ('BD', _('Bangladesh')),
        ('BB', _('Barbados')),
        ('BY', _('Belarus')),
        ('BE', _('Belgium')),
        ('BZ', _('Belize')),
        ('BJ', _('Benin')),
        ('BM', _('Bermuda')),
        ('BT', _('Bhutan')),
        ('BO', _('Bolivia')),
        ('BA', _('Bosnia-Herzegovina')),
        ('BW', _('Botswana')),
        ('BV', _('Bouvet Island')),
        ('BR', _('Brazil')),
        ('IO', _('British Indian Ocean Territory')),
        ('BN', _('Brunei Darussalam')),
        ('BG', _('Bulgaria')),
        ('BF', _('Burkina Faso')),
        ('BI', _('Burundi')),
        ('KH', _('Cambodia')),
        ('CM', _('Cameroon')),
        ('CV', _('Cape Verde')),
        ('KY', _('Cayman Islands')),
        ('CF', _('Central African Republic')),
        ('TD', _('Chad')),
        ('CL', _('Chile')),
        ('CN', _('China')),
        ('CX', _('Christmas Island')),
        ('CC', _('Cocos (Keeling) Islands')),
        ('CO', _('Colombia')),
        ('KM', _('Comoros')),
        ('CG', _('Congo')),
        ('CK', _('Cook Islands')),
        ('CR', _('Costa Rica')),
        ('HR', _('Croatia')),
        ('CU', _('Cuba')),
        ('CY', _('Cyprus')),
        ('CZ', _('Czech Republic')),
        ('DK', _('Denmark')),
        ('DJ', _('Djibouti')),
        ('DM', _('Dominica')),
        ('DO', _('Dominican Republic')),
        ('TP', _('East Timor')),
        ('EC', _('Ecuador')),
        ('EG', _('Egypt')),
        ('SV', _('El Salvador')),
        ('GQ', _('Equatorial Guinea')),
        ('ER', _('Eritrea')),
        ('EE', _('Estonia')),
        ('ET', _('Ethiopia')),
        ('FK', _('Falkland Islands')),
        ('FO', _('Faroe Islands')),
        ('FJ', _('Fiji')),
        ('FI', _('Finland')),
        ('CS', _('Former Czechoslovakia')),
        ('SU', _('Former USSR')),
        ('FX', _('France (European Territory)')),
        ('GF', _('French Guyana')),
        ('TF', _('French Southern Territories')),
        ('GA', _('Gabon')),
        ('GM', _('Gambia')),
        ('GE', _('Georgia')),
        ('GH', _('Ghana')),
        ('GI', _('Gibraltar')),
        ('GR', _('Greece')),
        ('GL', _('Greenland')),
        ('GD', _('Grenada')),
        ('GP', _('Guadeloupe (French)')),
        ('GU', _('Guam (USA)')),
        ('GT', _('Guatemala')),
        ('GN', _('Guinea')),
        ('GW', _('Guinea Bissau')),
        ('GY', _('Guyana')),
        ('HT', _('Haiti')),
        ('HM', _('Heard and McDonald Islands')),
        ('HN', _('Honduras')),
        ('HK', _('Hong Kong')),
        ('HU', _('Hungary')),
        ('IS', _('Iceland')),
        ('IN', _('India')),
        ('ID', _('Indonesia')),
        ('IR', _('Iran')),
        ('IQ', _('Iraq')),
        ('IL', _('Israel')),
        ('CI', _('Ivory Coast (Cote D&#39;Ivoire)')),
        ('JM', _('Jamaica')),
        ('JP', _('Japan')),
        ('JO', _('Jordan')),
        ('KZ', _('Kazakhstan')),
        ('KE', _('Kenya')),
        ('KI', _('Kiribati')),
        ('KW', _('Kuwait')),
        ('KG', _('Kyrgyzstan')),
        ('LA', _('Laos')),
        ('LV', _('Latvia')),
        ('LB', _('Lebanon')),
        ('LS', _('Lesotho')),
        ('LR', _('Liberia')),
        ('LY', _('Libya')),
        ('LI', _('Liechtenstein')),
        ('LT', _('Lithuania')),
        ('LU', _('Luxembourg')),
        ('MO', _('Macau')),
        ('MK', _('Macedonia')),
        ('MG', _('Madagascar')),
        ('MW', _('Malawi')),
        ('MY', _('Malaysia')),
        ('MV', _('Maldives')),
        ('ML', _('Mali')),
        ('MT', _('Malta')),
        ('MH', _('Marshall Islands')),
        ('MQ', _('Martinique (French)')),
        ('MR', _('Mauritania')),
        ('MU', _('Mauritius')),
        ('YT', _('Mayotte')),
        ('MX', _('Mexico')),
        ('FM', _('Micronesia')),
        ('MD', _('Moldavia')),
        ('MC', _('Monaco')),
        ('MN', _('Mongolia')),
        ('MS', _('Montserrat')),
        ('MA', _('Morocco')),
        ('MZ', _('Mozambique')),
        ('MM', _('Myanmar')),
        ('NA', _('Namibia')),
        ('NR', _('Nauru')),
        ('NP', _('Nepal')),
        ('NL', _('Netherlands')),
        ('AN', _('Netherlands Antilles')),
        ('NT', _('Neutral Zone')),
        ('NC', _('New Caledonia (French)')),
        ('NI', _('Nicaragua')),
        ('NE', _('Niger')),
        ('NG', _('Nigeria')),
        ('NU', _('Niue')),
        ('NF', _('Norfolk Island')),
        ('KP', _('North Korea')),
        ('MP', _('Northern Mariana Islands')),
        ('NO', _('Norway')),
        ('OM', _('Oman')),
        ('PK', _('Pakistan')),
        ('PW', _('Palau')),
        ('PA', _('Panama')),
        ('PG', _('Papua New Guinea')),
        ('PY', _('Paraguay')),
        ('PE', _('Peru')),
        ('PH', _('Philippines')),
        ('PN', _('Pitcairn Island')),
        ('PL', _('Poland')),
        ('PF', _('Polynesia (French)')),
        ('PT', _('Portugal')),
        ('PR', _('Puerto Rico')),
        ('QA', _('Qatar')),
        ('RE', _('Reunion (French)')),
        ('RO', _('Romania')),
        ('RU', _('Russian Federation')),
        ('RW', _('Rwanda')),
        ('GS', _('S. Georgia &amp; S. Sandwich Isls.')),
        ('SH', _('Saint Helena')),
        ('KN', _('Saint Kitts &amp; Nevis Anguilla')),
        ('LC', _('Saint Lucia')),
        ('PM', _('Saint Pierre and Miquelon')),
        ('ST', _('Saint Tome (Sao Tome) and Principe')),
        ('VC', _('Saint Vincent &amp; Grenadines')),
        ('WS', _('Samoa')),
        ('SM', _('San Marino')),
        ('SA', _('Saudi Arabia')),
        ('SN', _('Senegal')),
        ('SC', _('Seychelles')),
        ('SL', _('Sierra Leone')),
        ('SG', _('Singapore')),
        ('SK', _('Slovak Republic')),
        ('SI', _('Slovenia')),
        ('SB', _('Solomon Islands')),
        ('SO', _('Somalia')),
        ('ZA', _('South Africa')),
        ('KR', _('South Korea')),
        ('LK', _('Sri Lanka')),
        ('SD', _('Sudan')),
        ('SR', _('Suriname')),
        ('SJ', _('Svalbard and Jan Mayen Islands')),
        ('SZ', _('Swaziland')),
        ('SE', _('Sweden')),
        ('CH', _('Switzerland')),
        ('SY', _('Syria')),
        ('TJ', _('Tadjikistan')),
        ('TW', _('Taiwan')),
        ('TZ', _('Tanzania')),
        ('TH', _('Thailand')),
        ('TG', _('Togo')),
        ('TK', _('Tokelau')),
        ('TO', _('Tonga')),
        ('TT', _('Trinidad and Tobago')),
        ('TN', _('Tunisia')),
        ('TR', _('Turkey')),
        ('TM', _('Turkmenistan')),
        ('TC', _('Turks and Caicos Islands')),
        ('TV', _('Tuvalu')),
        ('UG', _('Uganda')),
        ('UA', _('Ukraine')),
        ('AE', _('United Arab Emirates')),
        ('UY', _('Uruguay')),
        ('MIL', _('USA Military')),
        ('UM', _('USA Minor Outlying Islands')),
        ('UZ', _('Uzbekistan')),
        ('VU', _('Vanuatu')),
        ('VA', _('Vatican City State')),
        ('VE', _('Venezuela')),
        ('VN', _('Vietnam')),
        ('VG', _('Virgin Islands (British)')),
        ('VI', _('Virgin Islands (USA)')),
        ('WF', _('Wallis and Futuna Islands')),
        ('EH', _('Western Sahara')),
        ('YE', _('Yemen')),
        ('YU', _('Yugoslavia')),
        ('ZR', _('Zaire')),
        ('ZM', _('Zambia')),
        ('ZW', _('Zimbabwe')),
    )

    street_address = models.CharField(
            _('Street Address'), 
            max_length=128, 
            blank=True
            ) 
    extended_address = models.CharField(
            _('Extended Address'), 
            max_length=128, 
            blank=True
            )
    locality = models.CharField(
            _('Town / City'), 
            max_length=128, 
            blank=True
            )
    region = models.CharField(
            _('County / State'), 
            max_length=128, 
            blank=True
            )
    country_name = models.CharField(
            _('Country'), 
            max_length=3, 
            choices = COUNTRY_LIST, 
            blank=True
            )
    postal_code = models.CharField(
            _('Post Code'), 
            max_length=32, 
            blank=True
            )
    post_office_box = models.CharField(
            _('Post Office Box'),
            max_length=32,
            blank=True
            )
    types = models.ManyToManyField(adr_type)
    hcard = models.ForeignKey(hCard, null=True)

    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')
    
    def __unicode__(self):
         result = ', '.join((x for x in (
            self.street_address, 
            self.extended_address,
            self.locality, 
            self.region, 
            self.get_country_name_display(), 
            self.postal_code,
            self.post_office_box) if x.strip()))
         if result:
             return result
         else:
             return 'None'

class tel_type(models.Model):
    """ 
    Represents a type of telephone number in the hCard microformat.

    See:

    http://microformats.org/wiki/hcard#adr_tel_email_types

    Also see: http://www.ietf.org/rfc/rfc2426.txt (quoted below)

    The type parameter values can include:
    
    "home" to indicate a telephone number associated with a residence,
    "msg" to indicate the telephone number has voice messaging support,
    "work" to indicate a telephone number associated with a place of
    work, "pref" to indicate a preferred-use telephone number, "voice" to
    indicate a voice telephone number, "fax" to indicate a facsimile
    telephone number, "cell" to indicate a cellular telephone number,
    "video" to indicate a video conferencing telephone number, "pager" to
    indicate a paging device telephone number, "bbs" to indicate a
    bulletin board system telephone number, "modem" to indicate a
    MODEM connected telephone number, "car" to indicate a car-phone telephone
    number, "isdn" to indicate an ISDN service telephone number, "pcs" to 
    indicate a personal communication services telephone number. The
    default type is "voice". These type parameter values can be specified
    as a parameter list (i.e., "TYPE=work;TYPE=voice") or as a value list
    (i.e., "TYPE=work,voice").  The default can be overridden to another
    set of values by specifying one or more alternate values. For example, the
    default TYPE of "voice" can be reset to a WORK and HOME, VOICE and FAX
    telephone number by the value list "TYPE=work,home,voice,fax".

    """

    TYPE_LIST = (
            ('voice', _('Voice')),
            ('home', _('Home')),
            ('msg', _('Message Service')),
            ('work', _('Work')),
            ('pref', _('Preferred')),
            ('fax', _('Fax')),
            ('cell', _('Cell/Mobile')),
            ('video', _('Videoconference')),
            ('pager', _('Pager')),
            ('bbs', _('Bulletin Board Service')),
            ('modem', _('Modem')),
            ('car', _('Carphone (fixed)')),
            ('isdn', _('ISDN')),
            ('pcs', _('Personal Communication Service')),
            )

    name = models.CharField(
            _('Telephone Number Type'),
            max_length=5,
            choices=TYPE_LIST,
            default='voice'
            )

    class Meta:
        verbose_name = _('Telephone Type')
        verbose_name_plural = _('Telephone Types')
    
    def __unicode__(self):
        return self.get_name_display()

class tel(models.Model):
    """
    Represents a telephone number in the hCard microformat.

    See:

    http://microformats.org/wiki/hcard
    
    """
    hcard = models.ForeignKey(hCard)
    # A telephone number can have more than one type. e.g. pref, home, voice
    types = models.ManyToManyField(tel_type)
    value = models.CharField(
            _('Value'),
            max_length=64,
            help_text=_('(e.g. +44(0)1234 567876)')
            )

    class Meta:
        verbose_name = _('Telephone Number')
        verbose_name_plural = _('Telephone Numbers')
    
    def __unicode__(self):
        return self.value
    
class email_type(models.Model):
    """
    Represents a type of email in the hCard microformat.

    See:

    http://microformats.org/wiki/hcard#adr_tel_email_types

    Also see: http://www.ietf.org/rfc/rfc2426.txt (quoted below)

    Used to specify the format or preference of the electronic mail address. 
    The TYPE parameter values can include: "internet" to indicate an Internet
    addressing type, "x400" to indicate a X.400 addressing type or "pref"
    to indicate a preferred-use email address when more than one is
    specified. Another IANA registered address type can also be
    specified. The default email type is "internet". A non-standard value 
    can also be specified.

    """

    TYPE_LIST = (
            ('internet', _('Internet')),
            ('x400', _('x400')),
            ('pref', _('Preferred')),
            ('other', _('Other IANA address type')),
            )

    name = models.CharField(
            _('Email type'),
            max_length=8,
            choices=TYPE_LIST,
            default='internet'
            )

    class Meta:
        verbose_name = _('Email Type')
        verbose_name_plural = _('Email Types')

    def __unicode__(self):
        return self.get_name_display()

class email(models.Model):
    """
    Represents an email address in the hCard microformat.

    See:

    http://microformats.org/wiki/hcard
    
    """
    hcard = models.ForeignKey(hCard)
    # An email address can have more than one type (but won't usually)
    types = models.ManyToManyField(email_type)
    value = models.CharField(
            _('Value'),
            max_length=64,
            help_text=_('(e.g. john.smith@company.com)')
            )
    
    class Meta:
        verbose_name = _('Email Address')
        verbose_name_plural = _('Email Addresses')
    
    def __unicode__(self):
        return self.value

class photo(models.Model):
    """
    Represents a photo associated with an hCard microformat instance

    See:

    http://microformats.org/wiki/hcard
    
    """
    hcard = models.ForeignKey(hCard)
    image = models.ImageField(upload_to='hcardphoto')

    class  Meta:
        verbose_name = _('Photo')
        verbose_name_plural = _('Photos')

    def __unicode__(self):
        return _('Photo for hCard')

class logo(models.Model):
    """
    Represents a logo associated with an hCard microformat instance

    See:

    http://microformats.org/wiki/hcard
    
    """
    hcard = models.ForeignKey(hCard)
    image = models.ImageField(upload_to='hcardlogo')

    class  Meta:
        verbose_name = _('Logo')
        verbose_name_plural = _('Logos')

    def __unicode__(self):
        return _('Logo for hCard')

class sound(models.Model):
    """
    Represents a sound associated with an hCard microformat instance

    See:

    http://microformats.org/wiki/hcard
    
    """
    hcard = models.ForeignKey(hCard)
    recording = models.FileField(upload_to='hcardsounds')

    class  Meta:
        verbose_name = _('Sound')
        verbose_name_plural = _('Sounds')

    def __unicode__(self):
        return _('Sound for hCard')

class title(models.Model):
    """
    Represents a title a person has at the referenced organization associated 
    with an hCard microformat instance

    See:

    http://microformats.org/wiki/hcard
    
    """
    hcard = models.ForeignKey(hCard)
    name = models.CharField(
            _('Title name'),
            max_length=128,
            help_text=_('e.g. CEO, Consultant, Principal')
            )

    class  Meta:
        verbose_name = _('Title')
        verbose_name_plural = _('Title')

    def __unicode__(self):
        return self.name 

class role(models.Model):
    """
    Represents the role a person plays within the organization associated with 
    an hCard microformat instance

    See:

    http://microformats.org/wiki/hcard
    
    """
    hcard = models.ForeignKey(hCard)
    description = models.CharField(
            _('Role name'),
            max_length=256,
            help_text=_('The role played within the organization')
            )

    class  Meta:
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')

    def __unicode__(self):
        return self.description

class org(models.Model):
    """
    Represents an organisation associated with an hCard microformat instance

    See:

    http://microformats.org/wiki/hcard
    
    """
    hcard = models.ForeignKey(hCard)
    name = models.CharField(
            _('Organization Name'),
            max_length=256
            )
    unit = models.CharField(
            _('Organizational Unit'),
            max_length=256,
            blank=True
            )
    primary = models.BooleanField(
            _('Primary organization'),
            default=True,
            help_text=_('This is the primary organization'\
                    ' associated with this contact')
            )
    title = models.ForeignKey(title, null=True)
    role = models.ForeignKey(role, null=True)

    class Meta:
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')

    def __unicode__(self):
        if self.unit:
            return self.unit+', '+self.name
        else:
            return self.name


class note(models.Model):
    """
    Represents supplemental information or a comment associated with an hCard 
    microformat instance

    See:

    http://microformats.org/wiki/hcard
    
    """
    hcard = models.ForeignKey(hCard)
    content = models.TextField(_('Note'))

    class Meta:
        verbose_name = _('Note')
        verbose_name_plural = _('Notes')

    def __unicode__(self):
        return self.content
    
class key(models.Model):
    """
    Represents a public key or authentication certificate associated with an 
    hCard microformat instance

    See:

    http://microformats.org/wiki/hcard
    
    """
    hcard = models.ForeignKey(hCard)
    name = models.TextField(
            _('Key Details'),
            help_text = _('Details of a public key or authentication'\
                    ' certificate associated with this contact')
            )

    class Meta:
        verbose_name = _('Key')
        verbose_name_plural = _('Keys')

    def __unicode__(self):
        return self.name

class mailer(models.Model):
    """
    Represents the type of electronic mail software that is used by the entity 
    associated with an hCard microformat instance

    See:

    http://microformats.org/wiki/hcard
    
    """
    hcard = models.ForeignKey(hCard)
    name = models.CharField(
            _('Mailer'),
            max_length=128,
            help_text = _('The type of email software used by the contact')
            )

    class Meta:
        verbose_name = _('Mailer')
        verbose_name_plural = _('Mailers')

    def __unicode__(self):
        return self.name

class hCalendar(models.Model):
    """
    Represents an hCalendar Microformat. 

    See:

    http://microformats.org/wiki/hcalendar

    hCalendar is a simple, open, distributed calendaring and events format,
    based on the iCalendar standard (RFC2445), suitable for embedding in HTML or
    XHTML, Atom, RSS, and arbitrary XML. hCalendar is one of several open
    microformat standards. 
    """
    summary = models.CharField(
            _('Summary'),
            max_length=256
            )
    location = models.CharField(
            _('Location'),
            max_length=256,
            blank=True
            )
    url = models.URLField(
            _('URL'),
            verify_exists=False,
            blank=True
            )
    dtstart = models.DateTimeField(_('Start'))
    dtend = models.DateTimeField(
            _('End'),
            null=True,
            blank=True
            )
    all_day_event = models.BooleanField(
            _('All day event'),
            default=False
            )
    tz = models.CharField(
            _('Timezone'),
            max_length=8,
            blank=True,
            choices=TIMEZONE,
            help_text=_("Hour(s) from GMT")
            )
    description = models.TextField(
            _('Description'),
            blank=True
            )
    adr = models.ForeignKey(
            adr,
            null=True)
    attendees = models.ManyToManyField(
            hCard,
            related_name='attendees'
            )
    contacts = models.ManyToManyField(
            hCard,
            related_name='contacts'
            )
    organizers = models.ManyToManyField(
            hCard,
            related_name='organizers'
            )

    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')

    def __unicode__(self):
        return self.dtstart.strftime('%a %b %d %Y, %I:%M%p')+' - '+self.summary

class xfn_values(models.Model):
    """
    Potential values to be used in the rel attribute of the XFM "microformat"

    See:

    http://www.gmpg.org/xfn/1

    Summary of values (loaded in the fixtures)

    relationship category         |  XFN values
    ------------------------------+--------------------------------
    friendship (at most one):     |  friend acquaintance contact
    physical:                     |  met
    professional:                 |  co-worker colleague
    geographical (at most one):   |  co-resident neighbor
    family (at most one):         |  child parent sibling spouse kin
    romantic:                     |  muse crush date sweetheart
    identity:                     |  me
    """

    VALUE_LIST = (
            ('friend', _('Friend')),
            ('acquaintance', _('Acquaintance')),
            ('contact', _('Contact')),
            ('met', _('Met')),
            ('co-worker', _('Co-worker')),
            ('colleague', _('Colleague')),
            ('co-resident', _('Co-resident')),
            ('neighbor', _('Neighbour')),
            ('child', _('Child')),
            ('parent', _('Parent')),
            ('sibling', _('Sibling')),
            ('spouse', _('Spouse')),
            ('kin', _('Kin')),
            ('muse', _('Muse')),
            ('crush', _('Crush')),
            ('date', _('Date')),
            ('sweetheart', _('Sweetheart')),
            ('me', _('Me'))
        )
    value = models.CharField(
            _('Relationship'),
            max_length=16,
            choices=VALUE_LIST
            )

    class Meta:
        verbose_name = _('XFN Relationship')
        verbose_name_plural = _('XFN Relationships')
        ordering = ['value']

    def __unicode__(self):
        return self.get_value_display()

class xfn(models.Model):
    """
    XFN™ (XHTML Friends Network) is a simple way to represent human
    relationships using hyperlinks. In recent years, blogs and blogrolls have
    become the fastest growing area of the Web. XFN enables web authors to
    indicate their relationship(s) to the people in their blogrolls simply by
    adding a 'rel' attribute to their <a href> tags, e.g.:

    <a href="http://jeff.example.org" rel="friend met">... 
    """
    # The person who is indicating the relationship - must be a user of the
    # application
    source = models.ForeignKey(
            User,
            related_name='source'
            )
    # The person who is the "friend"
    target = models.CharField(
            max_length=255
            )
    # A URL indicating who is the "friend" (if not a user in the system)
    url = models.URLField(
            _('URL'),
            verify_exists=False,
            )
    # The type of relationship
    relationships = models.ManyToManyField(xfn_values)
    
    class Meta:
        verbose_name = _('XFN')
        verbose_name_plural = _('XFN definitions')

    def __unicode__(self):
        vals = ', '.join(x.__unicode__() for x in self.relationships.all())
        if vals:
            return self.target+u' ('+vals+u')'
        else:
            return self.target 
