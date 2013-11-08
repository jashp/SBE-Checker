from local_settings import *
import json
import urllib, urllib2
import re
import cookielib
import os

def sendEmail():
	print "found new"
	
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

URL_CHECK = "https://sbe.sona-systems.com/all_exp.aspx"
URL_LOGIN = "https://sbe.sona-systems.com/default.aspx"

REGEX_VIEWSTATE = '__VIEWSTATE" value="(.*)"';
REGEX_EVENTVALIDATION = '__EVENTVALIDATION" value="(.*)"';
REGEX_SURVEY = '<a id="ctl00_ContentPlaceHolder1_repStudentStudies_ctl\d+_HyperlinkStudentTimeSlot" href="exp_info.aspx\?experiment_id=(\d+)">Timeslots Available</a>'

DB_FILE = "seen.json"

response_initial = opener.open(URL_LOGIN).read()

view_state = re.findall(REGEX_VIEWSTATE, response_initial)[0]
event_validation = re.findall(REGEX_EVENTVALIDATION, response_initial)[0]

values = {'ctl00$ContentPlaceHolder1$userid' : USERNAME,
'ctl00$ContentPlaceHolder1$pw' : PASSWORD,
'ctl00$ContentPlaceHolder1$default_auth_button' : 'Log In',
'__VIEWSTATE' : view_state,
'__EVENTVALIDATION' : event_validation }

opener.open(URL_LOGIN, urllib.urlencode(values))

html = opener.open(URL_CHECK).read()

if not os.path.exists(DB_FILE):
	with open(DB_FILE, 'w') as f:
		json.dump([], f)

with open(DB_FILE) as f:
	all_seen = json.load(f)

for open_survey in re.findall(REGEX_SURVEY, html):
	survey_id = int(open_survey)
	if not survey_id in all_seen:
		all_seen.append(survey_id)
		sendEmail()

with open(DB_FILE, 'w') as f:
	json.dump(all_seen, f)