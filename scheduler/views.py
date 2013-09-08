from scheduler.tasks import msg
from datetime import datetime, timedelta
from django.http import HttpResponse, HttpRequest
from pytz import timezone

import json
import urllib2

def process (request):

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
			urllib2.urlopen("/scheduleMsg")

			lastEvent = event
			continue

		lastEnd = lastEvent["end"]["dateTime"][:-5]
		nextStart = lastEvent["end"]["dateTime"][:-5]

		if(lastEnd [-1] == "-"):
			lastEnd = lastEnd[:-1]
		if(nextStart [-1] == "-"):
			nextStart = nextStart[:-1]

		maxTravelTime = datetime.strptime(lastEnd, '%Y-%m-%dT%H:%M:%S') - datetime.strptime(nextStart, '%Y-%m-%dT%H:%M:%S')

		maxTravelTime = maxTravelTime.total_seconds()

		requestUrl = "http://maps.googleapis.com/maps/api/directions/json?origin="+lastEvent["location"]+"&destination="+event["location"]+"&sensor=false"
		requestUrl = requestUrl.replace(" ", "%20")

		googleMapRoute = json.load(urllib2.urlopen(requestUrl))


		routeLegs = (googleMapRoute ["routes"][0]["legs"])

		time = 0
		for leg in routeLegs:
			time += leg["duration"]["value"]

		if(maxTravelTime <  time):
			print ("Send SMS to user")
		else:
			print ("Schedule SMS to user")

		if(maxTravelTime - time > 45 * 60):
			if(nextStart.hour <11 and (lastEnd.hour<10 or lastEnd.minutes <= 30) and not scheduledCoffee):
				print ("Schedule coffee")
				scheduledCoffee = True
			elif (not scheduledLunch):
				print ("Schedule lunch")
				scheduledLunch = True


		lastEvent = event


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

	print (timeToSend)


	recepient = param.__getitem__("sendto")
	content = param.__getitem__("body")

	msg.apply_async((recepient, content), eta = timeToSend)


	return HttpResponse("Great Success!")