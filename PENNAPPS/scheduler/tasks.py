from celery import task
from twilio.rest import TwilioRestClient

@task()
def msg(recepient, content):
	account_sid = "AC03701871ae569b1ec0facf7b8ad41e19"
	auth_token  = "9908bfe073c98b4ac3fc0afce32ff77f"
	client = TwilioRestClient(account_sid, auth_token)
	
	message = client.sms.messages.create(body=content,
		to=recepient,
		from_="+12024996660")
	print (message.sid)
