from celery import task
from twilio.rest import TwilioRestClient

@task()
def msg(recepient, content):
	client = TwilioRestClient(account_sid, auth_token)
	
	message = client.sms.messages.create(body=content,
		to=recepient,
		from_="+12024996660")
	print (message.sid)
