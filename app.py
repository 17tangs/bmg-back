import smtplib
from flask import Flask, request
import requests
from flask_restful import Api, Resource, reqparse
from flask_mail import Message
from flask_cors import CORS
import json
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)
api = Api(app)

def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def fetch_jobs():
    url = "https://www.indeed.com/cmp/Boston-Meditech-Group/jobs"
    #url = "https://www.indeed.com/cmp/Asea/jobs"
    response = simple_get(url)
    jobs = []
    if response is not None:
        html = BeautifulSoup(response, 'html.parser')
        for li in html.select('.cmp-job-entry'):
            h3 = li.select('h3 a')[0].get_text()
            link = "https://indeed.com" + li.select('a')[0].get('href')
            loc = li.select('.cmp-note')[0].get_text()
            des = li.select('.cmp-job-snippet')[0].get_text()
            job = {'title': h3, 'link': link, 'location': loc, 'description': des}
            jobs.append(job)
    return jobs

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
    def get(self):
        jobs = fetch_jobs()
        return jobs, 404

    def post(self):
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
            subject = name + " just left feedback!"
            body = "He/she said: \n" + message + "\n\nHis/her email is: \n" + email
            text = "From: " + sent_from + "\nTo: " + ', '.join(to)+'\nSubject: ' + subject + '\n' + body
            try:
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.ehlo()
                server.login(gmail_user, gmail_password)
                server.sendmail(sent_from, to, text)
                server.close()
                print ('Email sent!')
            except:
                print ('Something went wrong...')
                return 402
            return 201
        else:
            return 400





api.add_resource(User, "/api")
if __name__ == '__main__':
    app.run(debug=True)


