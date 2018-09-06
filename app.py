import smtplib
from flask import Flask, request
import requests
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
import json
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

app = Flask(__name__)
CORS(app)
api = Api(app)


users = [
    {"name": "Sam",
     "age": 42,
     "occupation": "Network Engineer"},
    {"name": "Bob",
     "age": 37,
     "occupation": "Frontend Engineer"},
    {"name": "Alice",
     "age": 24,
     "occupation": "Backend Engineer"}
]

class User(Resource):
    def get(self, name):
        for user in users:
            if(name == user["name"]):
                return user, 200
        return "User not found", 404

    def post(self, name):
        d = json.loads(request.data)
        name= d['name']
        email= d['email']
        message=d['message']
        response = d['response']
        dictToSend = {'secret':'6Lcxv24UAAAAABUuKdgGZu-0Jz5BYFywIMW4ortp', 'response':response}
        res = requests.post('https://www.google.com/recaptcha/api/siteverify', data=dictToSend)
        if res.json()['success']:
            gmail_user = 'samtang1430@gmail.com'
            gmail_password = 'J3e8e7z2'
            sent_from = gmail_user
            to = ['samtang1430@gmail.com']
            subject = 'OMG Super Important Message'
            body = 'Hey, what\'s up?\n\n- You'
            msg = MIMEMultipart()
            msg['From'] = sent_from
            msg['To'] = ", ".join(to)
            msg['Subject'] = name + " just left feedback!"
            body = "He/she said: \n" + message + "\n\nHis/her email is: \n" + email
            msg.attach(MIMEText(body, 'plain'))
            try:
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.ehlo()
                server.login(gmail_user, gmail_password)
                server.sendmail(sent_from, to, msg.as_string())
                server.close()
                print ('Email sent!')
            except:
                print ('Something went wrong...')
            return 201
        else:
            return 400



    def put(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("age")
        parser.add_argument("occupation")
        args = parser.parse_args()

        for user in users:
            if(name == user["name"]):
                user["age"] = args["age"]
                user["occupation"] = args["occupation"]
                return user, 200
        user = {
            "name": name,
            "age": args["age"],
            "occupation": args["occupation"]
        }
        users.append(user)
        return user, 201

    def delete(self, name):
        global users
        users = [user for user in users if user["name"] != name]
        return "{} is deleted.".format(name), 200



api.add_resource(User, "/user/<string:name>")

if __name__ == "__main__":
	app.run()
