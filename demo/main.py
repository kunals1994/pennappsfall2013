#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2

from twilio.rest import TwilioRestClient
import json
import urllib2
import datetime
from datetime import timedelta

from google.appengine.api import taskqueue


account_sid = "AC03701871ae569b1ec0facf7b8ad41e19"
auth_token = "9908bfe073c98b4ac3fc0afce32ff77f"

class MessageHandler(webapp2.RequestHandler):
	def get(self):
		number = self.request.get("number")
		message = self.request.get("message")

		client = TwilioRestClient(account_sid, auth_token)
		client.messages.create(to=number, from_="+12159876841", body=message)	

class SchedulingHandler(webapp2.RequestHandler):
	def post(self):
		send_to = self.request.get("number")
		calender_id = self.request.get("pid")

		content = urllib2.urlopen("https://www.googleapis.com/calendar/v3/calendars/"+calender_id+"/events?key=AIzaSyD0lg0dtSNdKV1Ap8OIySXOGtozrzhnuRo")
		maps_json = json.load(content)

		events = maps_json["items"]

		current_datetime = datetime.datetime.now()

		title = ""
		time = datetime.datetime.strptime("9999-12-31T23:59:59", '%Y-%m-%dT%H:%M:%S')
		first = True

		for event in events:
			event_time = event["start"]["dateTime"]
			offset = event_time [-6:]
			offset = int(offset[:3] + offset[4:])

			off_hours = offset / 100
			off_mins = offset - (off_hours * 100)
			offset = timedelta(hours = off_hours, minutes = off_mins)

			event_time = event_time[:-6] 
			event_time = datetime.datetime.strptime(event_time, '%Y-%m-%dT%H:%M:%S')

			event_time -= offset
			
			if event_time < time and (event_time > current_datetime):
				title = event["summary"]
				time = event_time


		offset = timedelta(minutes = 30)

		message_out = title+" on "+time.strftime("%m/%d at %H:%M")
		time -= offset

		cd = time - datetime.datetime.now()

		cd = cd.total_seconds()

		if (cd < 0):
			cd = 1

		taskqueue.add(url = "/cartographr/sms", method = "GET", countdown = cd, params = {"number": send_to, "message": message_out})

		self.response.write('<script>window.location.replace ("http://cartographr.kshar.me");window.alert("'+
			"You'll get a text for " +title+ " half an hour before."
			+'");</script>')



app = webapp2.WSGIApplication([
    ('/cartographr/schedule', SchedulingHandler), ('/cartographr/sms', MessageHandler)
], debug=True)
