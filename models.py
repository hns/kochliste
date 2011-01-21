import logging

from django.db import models
from google.appengine.ext import db
from google.appengine.api.users import User

class Child(db.Model):
    """Child"""
    name = db.StringProperty(required = True)
    current = db.BooleanProperty(default = True)

class Day(db.Model):
    """Day"""
    day = db.IntegerProperty(required = False)
    month = db.StringProperty(required = False)
    menu = db.StringProperty()
    child = db.ReferenceProperty(Child)

def get_days_for_month(month_key):
    query = db.Query(Day).filter("month = ", month_key)
    days = {}
    count = {}
    for day in query:
        days[day.day] = day
        if day.child:
            id = day.child.key().id()
            count[id] = count.get(id, 0) + 1
    return days, count

def get_day(month, day):
    query = db.Query(Day).filter("month = ", month).filter("day = ", day)
    if query.count() > 1:
        logging.info("More than one day stored!")
        for x in query.fetch(10):
            db.delete(x)
        query = db.Query(Day).filter("month = ", month).filter("day = ", day)
    item = query.get()
    if item:
        logging.info("returning existing day: %s", item)
        return item
    else:
        logging.info("returning new day %s %s", month, day)
        return Day(month=month, day=day)


def get_current_children():
    query = db.Query(Child).filter("current = ", True).order("name")
    return query.fetch(20)
