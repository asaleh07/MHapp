_author_ = 'Adam Saleh'

#####################################################################################################################################################################
# Importing Libraries
#####################################################################################################################################################################

from twilio.rest import Client
import json
import requests
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse

#####################################################################################################################################################################
# Main code 
#####################################################################################################################################################################
app = Flask(__name__) 

@app.route('/') #www.mysite.com/api/ ##defines an endpoint, when it is triggered, it will run what is below
def MainPage():
    checkstatus()
    return "Ghanta Mobile Health - Running"

@app.route('/incsms')
def incoming_sms():
    # Get the message the user sent our Twilio number
    print "Message Received"
    messagebody = request.values.get('Body', None)
    incnumber = request.values.get('From', None)
    patientfile = {}
    with open('patientstatus.json','r') as json_file:    
        patientfile = json.load(json_file)
        #need to search through the patient file and check that the patient exists. If he/she doesn't, a new profile needs to be created
        exist = False
        index = 0
        for k in patientfile['patients']:
            if k['number'] == incnumber:
                exist = True
                print exist 

        # determines action to be taken according to whether or not patient profile exists 
        if exist == True:
            for i in patientfile['patients']:
                if i['number'] == incnumber:
                    print i['name'] + ' has sent a message'
                    i['incomingmessage'] = messagebody
                    i['status'] = "Received"
                    updatepatientfile(patientfile)
                    outgoing(patientfile,i)
                else: 
                    print i['name'] + " has not sent a message"
        elif exist == False:
            #need to create a new patient entry 
            print 'A new user has sent a message'
            newpatient = {'status': 'none', 'name': 'none', 'counter': '-1', 'number': 'none', 'incomingmessage': 'none', 'outgoingmessage': 'none', 'DOB': 'none'}
            print newpatient
            patientfile["patients"][index].update(newpatient)
            print patientfile
            print index
            index['incomingmessage'] = messagebody
            index['status'] = "Received"
            index['number'] = incnumber
            updatepatientfile(patientfile)
            outgoing(patientfile,index)

def checkstatus():
    #check json file to see which patients need to be dealt with
    with open('patientstatus.json') as data_file:    
        patientfile = json.load(data_file)
        for i in patientfile['patients']:
            if i['status'] == "Received":
                print('Received from ' + i['name'])
            elif i['status'] == "Sent": 
                print('Awaiting Response from ' + i['name'])
            else: 
                print('Need to send initiation message to ' + i['name'])

def updatepatientfile(patientdata):
    #function that dumps data into json file to keep the patient data updated
    with open('patientstatus.json','w') as json_data:    
        json.dump(patientdata,json_data, indent=4)          
        print "Patient File Updated"
    return

def outgoing(patientfile,patientindex):
    #decide what message to send out
    if patientindex['counter'] == "0":
        outgoingmessage = 'Welcome to Mobile Health, ' + patientindex['name'] + '. Would you like to join Mobile Health? Reply to our messages with a "Yes" or "1" or a "No" or "2"'
        patientindex['counter'] = "1"
    elif patientindex['counter'] == "1": 
        outgoingmessage = 'If your shortness of breath the same or better as it was yesterday type 1 (or yes). If it is worse than it was yesterday, type 2.'
        patientindex['counter'] = "2"
    elif patientindex['counter'] == '2':
        if patientindex['incomingmessage'] == 'No' or ' No' or 'No ' or 'no' or ' no' or 'no ' or '2' or '2 ' or ' 2':
            alertdoc(patientfile,patientindex)
            outgoingmessage = 'Your Physician has been notified.'
            patientindex['counter'] = "3"
        elif patientindex['incomingmessage'] == 'Yes' or ' Yes' or 'Yes ' or 'yes' or ' yes' or 'yes ' or '1' or '1 ' or ' 1':
            outgoingmessage = 'Glad to hear! We will continue to follow up with you.'
            patientindex['counter'] = "4"
        else:  
            outgoingmessage = 'We did not understand your response. Please try again.'
    elif patientindex['counter'] == "-1": 
        outgoingmessage = 'Welcome to mobile health!'
    else: 
        outgoingmessage = 'Thank you for using Mobile Health!'
    
    #updates patientfile
    patientindex['outgoingmessage'] = outgoingmessage
    updatepatientfile(patientfile)
    send_sms(patientindex['number'],outgoingmessage)

def alertdoc(patientfile,patientindex): 
    outmessage = patientindex['name'] + ' is having trouble breathing.'
    docnumber = '+12812291629'
    send_sms(docnumber,outmessage)

def send_sms(patientnum,outmessage):
    account_sid = 
    auth_token = 
    client = Client(account_sid, auth_token)

    message = client.messages \
        .create(
          body= outmessage,
          from_='8329059052',
          to= patientnum
        )
    print(message.sid)
    
if __name__ == '__main__':
    app.run(port=5000)
