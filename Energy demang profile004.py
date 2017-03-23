#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 11:45:46 2017

@author: pchanvittaya
"""
import netCDF4 as nc
import numpy as np
import datetime as dt
import math
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import plotly.plotly as py
import plotly.graph_objs as go

data = nc.Dataset("ALL_DEMAND.nc","r")
time = data.variables["date"][:]
state = data.variables[str("States")]
price = data.variables["price"][:]
#for i,val in enumerate(price):
 #   if -99999.8984375 in val:
  #      price[i] = np.nan
prc = np.array(price)
prc[prc < -2000] = 0
prc
demand = data.variables["demand"][:]
#for i,val in enumerate(demand):
 #   if -99999.8984375 in val:
  #      demand[i] = np.nan
dem2 = np.array(demand)
dem2[dem2 < 0] = 0
dem2

def mjd_to_jd(mjd):
    return mjd + 2400000.5
def jd_to_mjd(jd):
    return jd - 2400000.5
def date_to_jd(year,month,day):
    if month == 1 or month == 2:
        yearp = year - 1
        monthp = month + 12
    else:
        yearp = year
        monthp = month
        
    if ((year < 1582) or (year == 1582 and month < 10) or (year == 1582 and month == 10 and day < 15)):
# before start of Gregorian calendar
        B = 0
    else:
# after start of Gregorian calendar
        A = math.trunc(yearp / 100.)
        B = 2 - A + math.trunc(A / 4.)
        
    if yearp < 0:
        C = math.trunc((365.25 * yearp) - 0.75)
    else:
        C = math.trunc(365.25 * yearp)
    D = math.trunc(30.6001 * (monthp + 1))
    jd = B + C + D + day + 1720994.5
    return jd
    
def jd_to_date(jd):
    jd = jd + 0.5
    F, I = np.modf(jd)
    I = int(I)
    A = math.trunc((I - 1867216.25)/36524.25)
    
    if I > 2299160:
        B = I + 1 + A - np.trunc(A / 4.)
    else:
        B = I    
    C = B + 1524
    D = math.trunc((C - 122.1) / 365.25)
    E = math.trunc(365.25 * D)
    G = math.trunc((C - E) / 30.6001)
    
    day = C - E + F - math.trunc(30.6001 * G)

    if G < 13.5:
        month = G - 1
    else:
        month = G - 13
        
    if month > 2.5:
        year = D - 4716
    else:
        year = D - 4715
        
    return year, month, day

def hmsm_to_days(hour=0,min=0,sec=0,micro=0):
    """ Convert hours, minutes, seconds, and microseconds to fractional days.
        
    Examples
    --------
    >>> hmsm_to_days(hour=6)  0.25"""
    days = sec + (micro / 1.e6)
    
    days = min + (days / 60.)
    
    days = hour + (days / 60.)
    
    return days / 24.
    
    
def days_to_hmsm(days):
    """
    Convert fractional days to hours, minutes, seconds, and microseconds.
    Precision beyond microseconds is rounded to the nearest microsecond.
    
    Examples
    --------
    >>> days_to_hmsm(0.1)
    (2, 24, 0, 0)"""
    
    hours = days * 24.
    hours, hour = math.modf(hours)
    
    mins = hours * 60.
    mins, min = math.modf(mins)
    
    secs = mins * 60.
    secs, sec = math.modf(secs)
    
    micro = round(secs * 1.e6)
    
    return int(hour), int(min), int(sec), int(micro)
    

def datetime_to_jd(date):
    """
    Convert a `datetime.datetime` object to Julian Day.
    
    Examples
    --------
    >>> d = datetime.datetime(1985,2,17,6)  
    >>> d
    datetime.datetime(1985, 2, 17, 6, 0)
    >>> jdutil.datetime_to_jd(d)
    2446113.75"""
    
    days = date.day + hmsm_to_days(date.hour,date.minute,date.second,date.microsecond)
    
    return date_to_jd(date.year,date.month,days)
    
    
def jd_to_datetime(jd):
    """
    Convert a Julian Day to an `jdutil.datetime` object.
    
    Parameters
    ----------
    jd : float
        Julian day.
        
    Returns
    -------
    dt : `jdutil.datetime` object
        `jdutil.datetime` equivalent of Julian day.
    
    Examples
    --------
    >>> jd_to_datetime(2446113.75)
    datetime(1985, 2, 17, 6, 0)
    
    """
    year, month, day = jd_to_date(jd)
    
    frac_days,day = math.modf(day)
    day = int(day)
    
    hour,min,sec,micro = days_to_hmsm(frac_days)
    
    return datetime(year,month,day,hour,min,sec,micro)


def timedelta_to_days(td):
    """
    Convert a `datetime.timedelta` object to a total number of days.
    
    Parameters
    ----------
    td : `datetime.timedelta` instance
    
    Returns
    -------
    days : float
        Total number of days in the `datetime.timedelta` object.
        
    Examples
    --------
    >>> td = datetime.timedelta(4.5)
    >>> td
    datetime.timedelta(4, 43200)
    >>> timedelta_to_days(td)
    4.5
    
    """
    seconds_in_day = 24. * 3600.
    
    days = td.days + (td.seconds + (td.microseconds * 10.e6)) / seconds_in_day
    
    return days
    
    
class datetime(dt.datetime):
    """
    A subclass of `datetime.datetime` that performs math operations by first
    converting to Julian Day, then back to a `jdutil.datetime` object.
    
    Addition works with `datetime.timedelta` objects, subtraction works with
    `datetime.timedelta`, `datetime.datetime`, and `jdutil.datetime` objects.
    Not all combinations work in all directions, e.g.
    `timedelta - datetime` is meaningless.
    
    See Also
    --------
    datetime.datetime : Parent class.
    
    """
    def __add__(self,other):
        if not isinstance(other,dt.timedelta):
            s = "jdutil.datetime supports '+' only with datetime.timedelta"
            raise TypeError(s)
        
        days = timedelta_to_days(other)
        
        combined = datetime_to_jd(self) + days
        
        return jd_to_datetime(combined)
        
    def __radd__(self,other):
        if not isinstance(other,dt.timedelta):
            s = "jdutil.datetime supports '+' only with datetime.timedelta"
            raise TypeError(s)
        
        days = timedelta_to_days(other)
        
        combined = datetime_to_jd(self) + days
        
        return jd_to_datetime(combined)
        
    def __sub__(self,other):
        if isinstance(other,dt.timedelta):
            days = timedelta_to_days(other)
            
            combined = datetime_to_jd(self) - days
            
            return jd_to_datetime(combined)
            
        elif isinstance(other, (datetime,dt.datetime)):
            diff = datetime_to_jd(self) - datetime_to_jd(other)
            
            return dt.timedelta(diff)
            
        else:
            s = "jdutil.datetime supports '-' with: "
            s += "datetime.timedelta, jdutil.datetime and datetime.datetime"
            raise TypeError(s)
            
    def __rsub__(self,other):
        if not isinstance(other, (datetime,dt.datetime)):
            s = "jdutil.datetime supports '-' with: "
            s += "jdutil.datetime and datetime.datetime"
            raise TypeError(s)
            
        diff = datetime_to_jd(other) - datetime_to_jd(self)
            
        return dt.timedelta(diff)
        
    def to_jd(self):
        """
        Return the date converted to Julian Day."""
        return datetime_to_jd(self)
        
    def to_mjd(self):
        """
        Return the date converted to Modified Julian Day."""
        return jd_to_mjd(self.to_jd())

# define a dictionary which maps month number to number of days
# in the month
monthdays = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
        
time_adj = ([jd_to_datetime(var).year for i,var in enumerate(time)])
datetimes = [jd_to_datetime(var) for i,var in enumerate(time)]
time_adj = [dt.minute + \
            60*dt.hour + \
            60*24*dt.day + \
            60*24*monthdays[dt.month]*dt.month + \
            60*8760*dt.year \
            for dt in datetimes]
#for i,var in enumerate(time):
    #time_adj = jd_to_datetime(var)
year_cov = 60*8760
time_adj2 = [i/year_cov for i in time_adj]   

fig_size = plt.rcParams["figure.figsize"]
fig_size[0] = 10
fig_size[1] = 6
plt.rcParams["figure.figsize"] = fig_size
fig, ax = plt.subplots()
#fig = plt.figure()
#plt.plot(time_adj,demand)
ax.plot(time_adj2,dem2)

fig.suptitle('Energy Demand profile', fontsize=14, fontweight='bold')
plt.xlabel('Time', fontsize=11, fontweight='bold')
plt.ylabel('Demand in MW', fontsize=11, fontweight='bold')

start, end = ax.get_xlim()
ax.xaxis.set_ticks(np.arange(math.floor(start), math.floor(end), 2))

ax.set_xlim([2000,2017])
ax.set_ylim([-100,16000])
#ax.xaxis.set_major_formatter(ticker.MultipleLocator('%1f'))

#X = np.arange(math.floor(min(time_adj)/(8760*60)), math.floor(max(time_adj)/(8760*60)), 87600)
#Y = demand

#ax = plt.axes()
#ax.xaxis.set_major_locator(ticker.MultipleLocator(8760))
#ax.xaxis.set_minor_locator(ticker.MultipleLocator(2000))
#plt.plot(X, Y, c = 'k')
plt.show()


fig1 = plt.figure()
plt.plot(time_adj2,prc)
plt.ylim([-1000,1500])
plt.xlim(2000,2017)
plt.show()

#def to_unix_time(dtu):
 #   epoch =  dt.dt.utcfromtimestamp(0)
  #  return (dtu - epoch).total_seconds() * 1000
#data1 = [go.Area(dem2)]
#layout = go.Layout(xaxis = dict(\
 #                   range = [to_unix_time(min(time_adj2)), \
  #                           to_unix_time(max(time_adj2))]))
#fig2 = go.Figure(data1 = data1, layout = layout)
#py.iplot(fig2)

#y0 = np.random.rand(100)
#y1 = y0 + np.random.rand(100)
#y2 = y1 + np.random.rand(100)
#capacity = 3*np.ones(100)

# make the mpl plot (no fill yet)
#fig, ax = plt.subplots()
#ax.plot(y0, label='y0')
#ax.plot(y1, label='y1')
#ax.plot(y2, label='y2')
#ax.plot(capacity, label='capacity')
#update = {'data':[{'fill': 'tonexty'}]}
#plot_url = py.plot_mpl(fig, update=update, strip_style=True, filename='mpl-stacked-line')