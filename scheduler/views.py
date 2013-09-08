from scheduler.tasks import msg
from datetime import datetime, timedelta
from django.http import HttpResponse, HttpRequest
from pytz import timezone
from twilio.rest import TwilioRestClient

import json
import urllib2
import urllib

def process (request):

	params = 0

	if(request.method == "GET"):
		params = request.GET
	elif (request.method == "POST"):
		params = request.POST


	outgoingPhone = params.__getitem__("sendTo")
	pid = params.__getitem__("pid")

	connect = urllib2.urlopen("https://www.googleapis.com/calendar/v3/calendars/"+pid+"/events?key=AIzaSyD0lg0dtSNdKV1Ap8OIySXOGtozrzhnuRo")

	mapsinput = json.load(connect)

	events = (mapsinput ["items"])

	lastEvent = ""

	scheduledCoffee = False

	scheduledLunch = False

	for event in events:
		if (lastEvent == ""):
			nextStart = event["start"]["dateTime"][:-5]

			if(nextStart [-1] == "-"):
				nextStart = nextStart[:-1]
			nextStart = datetime.strptime(nextStart, '%Y-%m-%dT%H:%M:%S')


			timeToSend = datetime (nextStart.year, nextStart.month, nextStart.day, nextStart.hour-2, nextStart.minute, 0, 1, timezone('America/New_York'))

			msg.apply_async((outgoingPhone, "Your first appointment of the day is in less than an hour"), eta = timeToSend)			

			lastEvent = event
			continue

		lastEnd = lastEvent["end"]["dateTime"][:-5]
		nextStart = event["start"]["dateTime"][:-5]

		if(lastEnd [-1] == "-"):
			lastEnd = lastEnd[:-1]
		if(nextStart [-1] == "-"):
			nextStart = nextStart[:-1]

		lastEnd = datetime.strptime(lastEnd, '%Y-%m-%dT%H:%M:%S')
		nextStart = datetime.strptime(nextStart, '%Y-%m-%dT%H:%M:%S')

		maxTravelTime = nextStart - lastEnd

		maxTravelTime = maxTravelTime.total_seconds()

		requestUrl = "http://maps.googleapis.com/maps/api/directions/json?origin="+lastEvent["location"]+"&destination="+event["location"]+"&sensor=false"
		requestUrl = requestUrl.replace(" ", "%20")

		googleMapRoute = json.load(urllib2.urlopen(requestUrl))


		routeLegs = (googleMapRoute ["routes"][0]["legs"])

		time = 0
		for leg in routeLegs:
			time += leg["duration"]["value"]

		if(maxTravelTime <  time):
			print ("Notifying user of conflict")
			account_sid = "AC03701871ae569b1ec0facf7b8ad41e19"
			auth_token  = "9908bfe073c98b4ac3fc0afce32ff77f"
			client = TwilioRestClient(account_sid, auth_token)
			
			message = client.sms.messages.create(body="You will not have enough time to reach "+event["summary"]+" at "+event["location"]+".",
				to=outgoingPhone,
				from_="+12024996660")


		else:
			nextStart = nextStart - timedelta(seconds = time + 600)

			timeToSend = datetime (nextStart.year, nextStart.month, nextStart.day, nextStart.hour-2, nextStart.minute, 0, 1, timezone('America/New_York'))
			print ("Creating reminder for "+str(timeToSend))
			msg.apply_async((outgoingPhone, "You must leave within 10 minutes to make "+event["summary"]+" at "+event["location"]+"."), eta = timeToSend)


		if(maxTravelTime - time > 45 * 60):
			if(nextStart.hour <11 and (lastEnd.hour<10 or lastEnd.minute <= 30) and not scheduledCoffee):

				account_sid = "AC03701871ae569b1ec0facf7b8ad41e19"
				auth_token  = "9908bfe073c98b4ac3fc0afce32ff77f"
				client = TwilioRestClient(account_sid, auth_token)
			
				message = client.sms.messages.create(body="You have time for coffee at " + str(lastEnd) + ".",
					to=outgoingPhone,
					from_="+12024996660")

 
				
				scheduledCoffee = True
			elif (not scheduledLunch):
				account_sid = "AC03701871ae569b1ec0facf7b8ad41e19"
				auth_token  = "9908bfe073c98b4ac3fc0afce32ff77f"
				client = TwilioRestClient(account_sid, auth_token)
			
				message = client.sms.messages.create(body="You have time for coffee at " +str(lastEnd) +". Making reservations",
					to=outgoingPhone,
					from_="+12024996660")
				scheduledLunch = True


		lastEvent = event
	return HttpResponse("Success")


def scheduleMsg(request):
	param = 0

	if(request.method == "GET"):
		param = request.GET
	elif (request.method == "POST"):
		param = request.POST


	hour = int(param.__getitem__("hour"))

	day = int(param.__getitem__("day"))

	if (hour == 0):
		hour = 24
		day -= 1

	hour -= 1

	timeToSend = datetime (int(param.__getitem__("year")), int(param.__getitem__("month")), day, hour, int(param.__getitem__("minute")), 0, 1, timezone('America/New_York')) 


	recepient = param.__getitem__("sendto")
	content = param.__getitem__("body")

	print ("Scheduled reminder for "+ timeToSend)
	msg.apply_async((recepient, content), eta = timeToSend)


	return HttpResponse("Great Success!")