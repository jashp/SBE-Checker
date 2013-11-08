from local_settings import *
import json
import urllib, urllib2
import re
import cookielib
import os
import smtplib


# constants
URL_CHECK = "https://sbe.sona-systems.com/all_exp.aspx"
URL_LOGIN = "https://sbe.sona-systems.com/default.aspx"

REGEX_VIEWSTATE = '__VIEWSTATE" value="(.*)"';
REGEX_EVENTVALIDATION = '__EVENTVALIDATION" value="(.*)"';
REGEX_SURVEY = '<a id="ctl00_ContentPlaceHolder1_repStudentStudies_ctl\d+_HyperlinkStudentTimeSlot" href="exp_info.aspx\?experiment_id=(\d+)">Timeslots Available</a>'

DB_FILE = "old.json"

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))

# open the initial page to get validation
response_initial = opener.open(URL_LOGIN).read()
view_state = re.findall(REGEX_VIEWSTATE, response_initial)[0]
event_validation = re.findall(REGEX_EVENTVALIDATION, response_initial)[0]

# set values for post request
values = {'ctl00$ContentPlaceHolder1$userid' : USERNAME,
'ctl00$ContentPlaceHolder1$pw' : PASSWORD,
'ctl00$ContentPlaceHolder1$default_auth_button' : 'Log In',
'__VIEWSTATE' : view_state,
'__EVENTVALIDATION' : event_validation }

# login and open page with surveys
opener.open(URL_LOGIN, urllib.urlencode(values))
html = opener.open(URL_CHECK).read()

# create file if not there
if not os.path.exists(DB_FILE):
	with open(DB_FILE, 'w') as f:
		json.dump([], f)

# read old surveys (that have already sent emails for)
with open(DB_FILE) as f:
	old = json.load(f)

# find all the open surveys and email + add to old list
for open_survey in re.findall(REGEX_SURVEY, html):
	survey_id = int(open_survey)
	if not survey_id in old:
		old.append(survey_id)
		server = smtplib.SMTP(SERVER)
		server.sendmail(FROM_EMAIL, TO_EMAILS, MESSAGE)
		server.quit()

# save changes
with open(DB_FILE, 'w') as f:
	json.dump(old, f)