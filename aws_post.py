# -*- coding: utf-8 -*-
import json
import requests
import html
import os
import datetime
import boto3
import pytz
from pytz import timezone
from datetime import date, timedelta
from bs4 import BeautifulSoup
from os.path import join, dirname
from dotenv import load_dotenv
from botocore.exceptions import ClientError



api_url_base = 'https://api.linkedin.com/v2/'

def write_ddb(title,date):

    table = dynamodb.Table('ing-dev-dynamodb-news')

    response = table.put_item(
        Item={
            'date': date,
            'title': title,
            }
    )

def read_ddb(title,date):
    table = dynamodb.Table('ing-dev-dynamodb-news')

    try:
        response = table.get_item(
            Key={
                'title': title,
                'date': date,
                
         }
        )
        print (title)
        if "Item" in response:
            return (True)
        else:
            return (False)
    except ClientError as e:
        print(e.response['Error']['Message'])

def imgurl(page,WebUrl):
    if(page>0):
        url = WebUrl
        code = requests.get(url)
        plain = code.text
        s = BeautifulSoup(plain, "html.parser")
        for link in s.findAll('meta', {'property':'og:image'}):
            imgurl_link = link.get('content')
            return(imgurl_link)

class linkedinPost():
    # Create .env file path
    dotenv_path = join(dirname(__file__), '.env')

    # load file from the path
    load_dotenv(dotenv_path)

    # accessing environment variable

    def post_on_linkedin(comment,title,link,thumbnail):
        access_token = os.getenv('ACCESS_TOKEN')
        urn = os.getenv('URN')
        author = f"urn:li:person:{urn}"
        api_url_base = 'https://api.linkedin.com/v2/'

        headers = {'X-Restli-Protocol-Version': '2.0.0',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'}


        api_url = f'{api_url_base}shares'

        post_data = {
                "content": {
                    "contentEntities": [
                        {
                            "entityLocation": link,
                            "thumbnails": [
                                {
                                    "resolvedUrl": thumbnail,
                                }
                            ]
                        }
                    ],
                    "title": title
                },
                "distribution": {
                    "linkedInDistributionTarget": {}
                },
                "owner": author,
                "subject": "",
                "text": {
                    "text": comment
                }
            }

        #print (post_data)

        response = requests.post(api_url, headers=headers, json=post_data)

        if response.status_code == 201:
            print("Success")
            print(response.content)
        else:
            print(response.content)

def blog_url():
    url = "https://aws.amazon.com/api/dirs/items/search?item.directoryId=blog-posts&sort_by=item.additionalFields.createdDate&sort_order=desc&size=5&item.locale=en_US&tags.id=blog-posts%23category%23news%7Cblog-posts%23category%23compute%7Cblog-posts%23category%23containers%7Cblog-posts%23category%23devops%7Cblog-posts%23category%23infrastructure-automation%7Cblog-posts%23category%23networking-content-delivery"
    code = requests.get(url)
    plain = code.text
    s = BeautifulSoup(plain, "html.parser")
    s = json.loads(str(s))
    #print (s)
    x = 0
    for news in s["items"]:
        if x < 10:
            print (x)
            x+=1
            title = html.unescape(news["item"]["additionalFields"]["title"])
            date = news["item"]["dateCreated"]
            link = news["item"]["additionalFields"]["link"]
            thumbnail = (imgurl(1,link))
            date_day = date.split('T')
            date_str = date_day[0]
            date_obj = datetime.datetime.strptime(date_day[0], '%Y-%m-%d').date()
            print((date_obj))
            today = datetime.date.today()
            print(today)
            if today == date_obj:
                read_status = read_ddb(title,date_str)
                if read_status == False:
                    write_ddb(title,date_str)
                    tags="#aws #amazonwebservices "
                    for tag in news["tags"]:
                            tags = (tags+"#"+(tag["name"]).replace('-','')+" ")
                    comment = (title+"\n\n"+tags)
                    linkedinPost.post_on_linkedin(comment,title,link,thumbnail)

            else:
                break
        else:
                break

def write_event_ddb(title,date):

    table = dynamodb.Table('ing-dev-dynamodb-events')

    response = table.put_item(
        Item={
            'date': date,
            'title': title,
            }
    )

def read_event_ddb(title,date):
    table = dynamodb.Table('ing-dev-dynamodb-events')

    try:
        response = table.get_item(
            Key={
                'title': title,
                'date': date,
         }
        )
        if "Item" in response:
            return (True)
        else:
            return (False)
    except ClientError as e:
        print(e.response['Error']['Message'])

def event_url():
    url = "https://aws.amazon.com/api/dirs/items/search?item.directoryId=events-master&sort_by=item.additionalFields.startDateTime&sort_order=asc&size=20&item.locale=en_US&tags.id=events-master%23type%23virtual&tags.id=events-master%23location%23americas&tags.id=events-master%23categories%23compute%7Cevents-master%23categories%23containers%7Cevents-master%23categories%23devops%7Cevents-master%23categories%23mgmttools%7Cevents-master%23categories%23open-source%7Cevents-master%23categories%23network%7Cevents-master%23categories%23security-identity-compliance%7Cevents-master%23categories%23serverless%7Cevents-master%23categories%23startup%7Cevents-master%23categories%23storage%7Cevents-master%23categories%23databases"
    code = requests.get(url)
    plain = code.text
    s = BeautifulSoup(plain, "html.parser")
    s = json.loads(str(s))
    x = True
    for events in s["items"]:
        if x == True:
            headline = (events["item"]["additionalFields"]["headline"])
            category = events["item"]["additionalFields"]["category"]
            if category in ["AWS Virtual Workshop","AWS Online Tech Talks","Webinars"]:
                link = events["item"]["additionalFields"]["headlineUrl"]
                level = events["item"]["additionalFields"]["expertiseTooltip"]
                start_date = events["item"]["additionalFields"]["startDateTime"]
                event_start_date = datetime.datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S%z')
                event_start_hour_ptc = event_start_date.replace(tzinfo=pytz.timezone('US/Pacific'))
                event_start_hour_brt = event_start_hour_ptc.astimezone(pytz.timezone('America/Sao_Paulo'))-timedelta(minutes=53)
                end_date = events["item"]["additionalFields"]["endDateTime"]
                event_end_date = datetime.datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S%z')
                event_end_hour_ptc = event_end_date.replace(tzinfo=pytz.timezone('US/Pacific'))
                event_end_hour_brt = event_end_hour_ptc.astimezone(pytz.timezone('America/Sao_Paulo'))-timedelta(minutes=53)
                next_week = int(datetime.date.today().strftime("%V"))+1
                event_week = int(event_start_date.strftime("%V"))
                if next_week == event_week:
                    if "duration" in events["item"]["additionalFields"]:
                        duration = events["item"]["additionalFields"]["duration"]
                    else:
                        duration = "to be defined"
                    thumbnail = (imgurl(1,link))
                    tags="#aws #amazonwebservices #growth"
                    read_status = read_event_ddb(headline,event_start_date.strftime('%Y-%m-%d'))
                    if read_status == False:
                        write_event_ddb(headline,event_start_date.strftime('%Y-%m-%d'))
                        when = (event_start_date.strftime("%B %d")+" | "+str(event_start_hour_ptc.strftime("%H:%M %p"))+" - "+str(event_end_hour_ptc.strftime("%H:%M %p"))+" Pacific Time or "+str(event_start_hour_brt.strftime("%H:%M %p"))+" - "+str(event_end_hour_brt.strftime("%H:%M %p")+" Brazilian Time"))
                        comment = ("AWS Online Tech Talks next week. Save the date.\n\n"+headline+"\nWhen: "+when+"\nDuration: "+duration+"\nLevel: "+level+"\n\n"+tags)
                        print (comment)
                        linkedinPost.post_on_linkedin(comment,headline,link,thumbnail)
        else:
            break

def lambda_handler(event, lambda_context):
    blog_url()
    event_url()

if 'OS' in os.environ:
    session = boto3.Session(profile_name='dev')
    dynamodb = session.resource('dynamodb', region_name='us-east-1')
    event="1"
    lambda_context=""
    lambda_handler(event, lambda_context)
else:
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')