import calendar
import datetime
import logging
import urllib
import sys

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.html import strip_tags
from google.appengine.ext import db
from google.appengine.api import users

import models
import forms


# workaround for calendar.day_name using wrong locale
day_name = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag']
month_name = ['Jaenner', 'Februar', 'Maerz', 'April', 'Mai', 'Juni',
              'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']

def index(request, year=None, month=None):
    if request.method == 'POST':
        try:
            return HttpResponse(store_day(request, year, month))
        except:
            logging.info("Error updating menu: %s", sys.exc_info()[0])
            return HttpResponse("Fehler beim Speichern. Sorry!")
    data = get_month_data(year, month, False)
    return render_to_response('index.html', data)

def plan(request, year=None, month=None):
    if request.method == 'POST':
        store_month(request, year, month)
        return HttpResponseRedirect(request.path)
    data = get_month_data(year, month, True)
    return render_to_response('calendar.html', data)

def normalize_month(year, month):
    if not year or not month:
        today = datetime.date.today()
        return today.year, today.month
    return int(year), int(month)

def store_day(request, year, month):
    year, month = normalize_month(year, month)
    month_key = format_month(year, month)
    logging.info("got menu: %s" % request['menu'])
    item = models.get_day(month_key, int(request['day']))
    menu = strip_tags(urllib.unquote(request['menu']))
    item.menu = unicode(menu, 'utf-8')
    item.put()
    return item.menu


def store_month(request, year, month):
    year, month = normalize_month(year, month)
    month_key = format_month(year, month)
    day_dict, count_dict = models.get_days_for_month(month_key)
    days = calendar.Calendar().itermonthdays(year, month)
    for day in days:
        if day > 0 and request.has_key(str(day)):
            child_key = request[str(day)]
            child = models.Child.get(child_key) if child_key else None
            # logging.info("Creating day: %d %s %s", day, month_key, child)
            if day_dict.has_key(day):
                item = day_dict[day]
                item.child = child
            else:
                item = models.Day(month=month_key, day=day, child=child)
            item.put()

def format_month(year, month):
    return "/%04d/%02d" % (year, month)

def get_month(year, month):
    return {'url': format_month(year, month),
            'month': month_name[month-1],
            'year': year}

def get_previous_month(year, month):
    previous_month = (month - 2) % 12 + 1
    previous_year = year if previous_month < 12 else year -1
    return get_month(previous_year, previous_month)

def get_next_month(year, month):
    next_month = month % 12 + 1
    next_year = year if next_month > 1 else year + 1
    return get_month(next_year, next_month)


def get_month_data(year, month, plan_view):
    year, month = normalize_month(year, month)
    month_data = get_month(year, month)
    # prev/next month
    previous = get_previous_month(year, month)
    next = get_next_month(year, month)
    # get day list
    dates = calendar.Calendar().itermonthdates(year, month)
    day_dict, count_dict = models.get_days_for_month(month_data['url'])
    days = []
    today = datetime.date.today()
    for date in dates:
        if date.month == month and date.weekday() < 5:
            day = {'weekday': day_name[date.weekday()],
                    'day': date.day,
                    'child': None}
            if day_dict.has_key(date.day):
                day['child'] = day_dict[date.day].child
                day['menu'] = day_dict[date.day].menu or ''
                day['menulink'] = '+' if day['menu'] else '?'
            day['rowclass'] = 'odd' if date.isocalendar()[1] % 2 else 'even'
            day['cellclass'] =  'today' if date == today else ''
            days.append(day)
    # get childlist
    childlist = models.get_current_children()
    children = [{'key': child.key(),
                 'id': child.key().id(),
                 'name': child.name,
                 'count': count_dict.get(child.key().id(), 0),
             } for idx, child in enumerate(childlist)]
    form = forms.ChildSelector(days, children) if plan_view else forms.MenuForm()
    return dict(days=days, month=month_data, previous=previous, next=next,
                form=form, children=children)


def list_children(request, all=None):
    if not users.is_current_user_admin():
        data = {'login_url': users.create_login_url("/kinder/")}
        return render_to_response('login.html', data)
    entries = models.Child.all()
    if not all:
        entries = entries.filter('current =', True)
    data = dict(entries=entries.order('name'), all=all)
    return render_to_response('list.html', data)

def create_child(request):
    if not users.is_current_user_admin():
        data = {'login_url': users.create_login_url("/kinder/")}
        return render_to_response('login.html', data)

    if request.method == 'POST':
        form = forms.ChildEditor(request.POST)
        print request.POST
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('../')
    if request.method == 'GET':
        form = forms.ChildEditor()
    data = dict(form=form)
    return render_to_response('create.html', data)

def edit_child(request):
    if not users.is_current_user_admin():
        data = {'login_url': users.create_login_url("/kinder/")}
        return render_to_response('login.html', data)

    entry = models.Child.get(request.GET['key'])
    # print entry
    if request.method == 'POST':
        form = forms.ChildEditor(request.POST)
        if form.is_valid():
            entry.name = form.clean_data['name']
        if 'hide' in request.POST:
            entry.current = False;
        entry.put()
        return HttpResponseRedirect('../')
    else:
        form = forms.ChildEditor({'name': entry.name})
    data = dict(form=form)
    return render_to_response('edit.html', data)

def set_visible_child(request):
    if not users.is_current_user_admin():
        data = {'login_url': users.create_login_url("/kinder/")}
        return render_to_response('login.html', data)

    entry = models.Child.get(request.GET['key'])
    # print entry
    value = request.GET['v']
    if entry and value in ['true', 'false']:
        entry.current = value == 'true'
        entry.save()
    return HttpResponseRedirect('../')

def delete_child(request):
    if not users.is_current_user_admin():
        data = {'login_url': users.create_login_url("/kinder/")}
        return render_to_response('login.html', data)

    entry = models.Child.get(request.GET['key'])
    # print entry
    if entry:
        entry.delete()
    return HttpResponseRedirect('../')
