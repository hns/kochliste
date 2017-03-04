import logging

from django import forms
from google.appengine.ext import db

import models

class ChildEditor(forms.Form):
    name = forms.CharField(required = True)

    def save(self):
        entry = models.Child(name=self.cleaned_data['name'])
        entry.current = True
        entry.put()
        return entry

class ChildSelector(forms.Form):

    def __init__(self, days, children, *args, **kwargs):
        super(ChildSelector, self).__init__(*args, **kwargs)
        choices = [('', '')]
        for child in children:
            choices.append((child['key'], child['name']))
        for day in days:
            key = str(day['day'])
            initial = day['child'].key() if day['child'] else ''
            self.fields[key] = forms.ChoiceField(label='', choices=choices, initial=initial)
            day['editor'] = self[key]


class MenuForm(forms.Form):
    menu = forms.CharField(label='')
