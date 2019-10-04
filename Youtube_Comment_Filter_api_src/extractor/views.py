from django.shortcuts import render

import pandas as pd

import pickle
from google.auth.transport.requests import Request
import time
import os
import string
import google.oauth2.credentials
 
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

from youtube_transcript_api import YouTubeTranscriptApi

# Create your views here.


def get_authenticated_service():
    CLIENT_SECRETS_FILE = "my_ytce_client_secret.json" #This is the name of your JSON file

    # This OAuth 2.0 access scope allows for full read/write access to the
    # authenticated user's account and requires requests to use an SSL connection.
    SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
    API_SERVICE_NAME = 'youtube'
    API_VERSION = 'v3'
    credentials = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    #  Check if the credentials are invalid or do not exist
    if not credentials or not credentials.valid:
        # Check if the credentials have expired
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_console()
 
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
 
    return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)


def get_comments_df(video_id_input):

     
    query_results = get_authenticated_service().videos().list(
            part = 'snippet',
            id = video_id_input,
            ).execute()


    video_id = []
    channel = []
    video_title = []
    video_desc = []

    #for me I dont need a for loop here 
    video_id.append(query_results['items'][0]['id'])
    channel.append(query_results['items'][0]['snippet']['channelTitle'])
    video_title.append(query_results['items'][0]['snippet']['title'])
    video_desc.append(query_results['items'][0]['snippet']['description'])
    # for item in query_results['items']:
    #     video_id.append(item['id']['videoId'])
    #     channel.append(item['snippet']['channelTitle'])
    #     video_title.append(item['snippet']['title'])
    #     video_desc.append(item['snippet']['description'])



    video_id_pop = []
    channel_pop = []
    video_title_pop = []
    video_desc_pop = []
    comments_pop = []
    comment_id_pop = []
    reply_count_pop = []
    like_count_pop = []


    for i, video in enumerate(tqdm(video_id, ncols = 100)):
        response = service.commentThreads().list(
                        part = 'snippet',
                        videoId = video,
                        maxResults = 100, # Only take top 100 comments...
                        order = 'relevance', #... ranked on relevance
                        textFormat = 'plainText',
                        ).execute()

        comments_temp = []
        comment_id_temp = []
        reply_count_temp = []
        like_count_temp = []
        for item in response['items']:
            comments_temp.append(item['snippet']['topLevelComment']['snippet']['textDisplay'])
            comment_id_temp.append(item['snippet']['topLevelComment']['id'])
            reply_count_temp.append(item['snippet']['totalReplyCount'])
            like_count_temp.append(item['snippet']['topLevelComment']['snippet']['likeCount'])
        comments_pop.extend(comments_temp)
        comment_id_pop.extend(comment_id_temp)
        reply_count_pop.extend(reply_count_temp)
        like_count_pop.extend(like_count_temp)

        video_id_pop.extend([video_id[i]]*len(comments_temp))
        channel_pop.extend([channel[i]]*len(comments_temp))
        video_title_pop.extend([video_title[i]]*len(comments_temp))
        video_desc_pop.extend([video_desc[i]]*len(comments_temp))

    #query_pop = [query] * len(video_id_pop)

    # The _pop lists are the lists we'll use to populate the dataframe later.

    # The _temp lists are created as temporary placeholders to determine the length or number of comments pulled from the particular video so we can lengthen the initial list of video ID, channel name, video title and video descriptions accordingly to build the dataframe.

    # We're done now. We build the dataframe with the following code snippet and output to Google Sheets.

    # =============================================================================
    # Populate to Dataframe
    # =============================================================================


    #'Query': query_pop,
    output_dict = {
            'Channel': channel_pop,
            'Video Title': video_title_pop,
            'Video Description': video_desc_pop,
            'Video ID': video_id_pop,
            'Comment': comments_pop,
            'Comment ID': comment_id_pop,
            'Replies': reply_count_pop,
            'Likes': like_count_pop,
            }

    return pd.DataFrame(output_dict, columns = output_dict.keys())

def get_transcript_df(video_id_input):
    text=[]
    start=[]
    duration=[]

    for dic in YouTubeTranscriptApi.get_transcript(video_id_input):
        text+=[dic['text']]
        start+=[dic['start']]
        duration+=[dic['duration']]


    output_dict_tran = {
                'text': text,
                'start': start,
                'duration': duration,
                }    
    return pd.DataFrame(output_dict_tran, columns = output_dict_tran.keys())

def select_script_transcript(start_time,added_time,tran):
    #start_time=20
    end_time=start_time+added_time
    #a[0] <= b[0] <= a[1] or b[0] <= a[0] <= b[1]
    #tran[((start_time<=tran['start'])&(tran['start']<=end_time))]
    #tran[((tran['start']<=start_time)&(start_time<=tran['end']))]

    transelection=tran[((start_time<=tran['start'])&(tran['start']<=end_time)) | ((tran['start']<=start_time)&(start_time<=tran['end']))]

    transelection_text=''
    for s in transelection.text:
        transelection_text+=s+' '
    return(transelection_text)
