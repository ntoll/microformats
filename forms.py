# -*- coding: UTF-8 -*-
"""
Example Forms for Microformats. 

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
# Django
from django import forms
from django.forms.util import ErrorList
from django.utils.translation import ugettext as _

# Microformats
from microformats.models import geo, hCard, adr, adr_type, org, email,\
        email_type, tel, tel_type, hCalendar, hReview, hListing

class GeoForm(forms.ModelForm):
    """
    A ModelForm for the geo microformat that makes sure the degrees decimal
    fields are within the valid ranges:

    Latitude: ±90°
    Longitude: ±180°
    """
    def clean_latitude(self):
        """
        ±90
        """
        value = self.cleaned_data['latitude']
        if value < -90.0 or value > 90.0:
            raise forms.ValidationError(_(u'Latitude is not within the valid'
                u' range (±90)'))
        return value

    def clean_longitude(self):
        """
        ±180
        """
        value = self.cleaned_data['longitude']
        if value < -180.0 or value > 180.0:
            raise forms.ValidationError(_(u'Longitude is not within the valid'
                u' range (±180)'))
        return value

    class Meta:
        model = geo

class LocationAwareForm(forms.ModelForm):
    """
    Used in concert with models derived from the LocationAwareMicroformat model.
    This form makes sure that the geo information is valid.
    """
    def clean(self):
        """
        Checks if you have one of Long or Lat you must have the other
        """
        super(LocationAwareForm, self).clean()
        cleaned_data = self.cleaned_data
        # Make sure we have a longitude and latitude
        lat = cleaned_data.get("latitude", False)
        long = cleaned_data.get("longitude", False)
        if long and not lat:
            self._errors['longitude'] = ErrorList([_("You must supply both a"\
                    " longitude and latitude")])
            del cleaned_data['longitude']
        if lat and not long: 
            self._errors['latitude'] = ErrorList([_("You must supply both a"\
                    " longitude and latitude")])
            del cleaned_data['latitude']
        return cleaned_data

    def clean_latitude(self):
        """
        ±90
        """
        value = self.cleaned_data.get('latitude', False)
        if value:
            if value < -90.0 or value > 90.0:
                raise forms.ValidationError(_(u'Latitude is not within the valid'
                    u' range (±90)'))
        return value

    def clean_longitude(self):
        """
        ±180
        """
        value = self.cleaned_data.get('longitude', False)
        if value:
            if value < -180.0 or value > 180.0:
                raise forms.ValidationError(_(u'Longitude is not within the valid'
                    u' range (±180)'))
        return value

class hCardForm(LocationAwareForm):
    """
    A simple form to use for gathering basic information for an hCard. Use in
    conjunction with the AdrForm, OrgForm, EmailForm and TelForm to build
    something more complex. 

    This form assumes the hCard will be for a person (rather than an
    organisation) - so the constructor sets the given_name as a required field
    so we always get a valid fn.

    Don't use this form for hCards relating to organisations only (that don't
    require personal name details like this form does).
    
    Inspired by:

    http://microformats.org/code/hcard/creator
    """
    def clean(self):
        """
        Checks you have something useful to use as fn
        """
        super(hCardForm, self).clean()
        cleaned_data = self.cleaned_data

        # Some minimum fields needed to create a fn
        org = cleaned_data.get('org', False)
        given_name = cleaned_data.get('given_name', False)
        family_name = cleaned_data.get('family_name', False)
        nickname = cleaned_data.get('nickname', False)

        # What the following if statement means:
        # if the user hasn't supplied either and organization name or provided
        # at least a nickname or a given name then raise an error
        if not (org or nickname or given_name):
            raise forms.ValidationError("You must supply some sort of namimg"\
                    " information (given name or nickname"\
                    " or an organization name)")
        return cleaned_data
    
    class Meta:
        model = hCard

class hCalForm(LocationAwareForm):
    """
    A simple form for gathering information for an hCalendar event. Inspired by
    the form found here:

    http://microformats.org/code/hcalendar/creator
    """
    class Meta:
        model = hCalendar
        exclude = [
                'attendees',
                'contacts',
                'organizers',
                ]

class hReviewForm(LocationAwareForm):
    """
    A simple form for gathering information for an hReview microformat. Inspired
    by the form found here:

    http://microformats.org/code/hreview/creator
    """
    class Meta:
        model = hReview

class hListingForm(LocationAwareForm):
    """
    A simple form for gathering information for an hListing microforat.
    """
    class Meta:
        model = hListing

class AdrForm(forms.ModelForm):
    """
    A simple form to use for gathering basic information for an adr microformat. 
    Use in conjunction with the hCardForm, OrgForm, EmailForm and TelForm to 
    build something more complex. 

    Inspired by:

    http://microformats.org/code/hcard/creator
    """
    def __init__(self, *args, **kwargs): 
        super(AdrForm, self).__init__(*args, **kwargs) 
        self.fields['types'].widget = forms.CheckboxSelectMultiple()
        self.fields['types'].label = _('Address Type')
        self.fields['types'].help_text = _('Please select as many that apply')
        self.fields['types'].queryset = adr_type.objects.all()

    class Meta:
        model = adr
        exclude = ['hcard', 'post_office_box']

class OrgForm(forms.ModelForm):
    """
    A simple form to use for gathering basic information for an organisation
    associated with an hCard.  Use in conjunction with the AdrForm, EmailForm 
    and TelForm to build something more complex. 

    Inspired by:

    http://microformats.org/code/hcard/creator
    """
    class Meta:
        model = org
        exclude = ['hcard']

class EmailForm(forms.ModelForm):
    """
    A simple form to use for gathering basic email information for an hCard. 
    Use in conjunction with the hCardForm, AdrForm, OrgForm and TelForm to 
    build something more complex. 

    Inspired by:

    http://microformats.org/code/hcard/creator
    """
    def __init__(self, *args, **kwargs): 
        super(EmailForm, self).__init__(*args, **kwargs) 
        self.fields['types'].widget = forms.CheckboxSelectMultiple()
        self.fields['types'].label = _('Email Type')
        self.fields['types'].help_text = _('Please select as many that apply')
        self.fields['types'].queryset = email_type.objects.all()

    class Meta:
        model = email 
        exclude = ['hcard']

class TelForm(forms.ModelForm):
    """
    A simple form to use for gathering basic telephone information for an hCard. 
    Use in conjunction with the hCardForm, AdrForm, OrgForm and EmailForm to 
    build something more complex. 

    Inspired by:

    http://microformats.org/code/hcard/creator
    """
    def __init__(self, *args, **kwargs): 
        super(TelForm, self).__init__(*args, **kwargs) 
        self.fields['types'].widget = forms.CheckboxSelectMultiple()
        self.fields['types'].label = _('Telephone Type')
        self.fields['types'].help_text = _('Please select as many that apply')
        self.fields['types'].queryset = tel_type.objects.all()

    class Meta:
        model = tel 
        exclude = ['hcard']
