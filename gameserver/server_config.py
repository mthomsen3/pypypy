'''


'''
#import os
import json

with open("config.json") as config_file:
	# this turns json into a python dictionary
	config = json.load(config_file)

class Config:
    #TODO - PUT THESE IN ENVIRONMENT VARIABLES ON SERVER
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = config.get('EMAIL_USER')
    MAIL_PASSWORD = config.get('EMAIL_PASS')
    SECRET_KEY = config.get('SECRET_KEY')


	#note: if stored as environment variables
	#MAIL_PASSWORD = os.environ.get('EMAIL_PASS')