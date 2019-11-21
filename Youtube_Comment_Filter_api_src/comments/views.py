from django.shortcuts import render

import numpy as np
import pandas as pd

from extractor.views import get_comments_df, get_transcript_df, select_script_transcript
from vectorizer.views import bow_transformer, tf_idf_transformer, tf_idf_transform
from sklearn.metrics.pairwise import cosine_similarity


from django.http import HttpResponse
import json
from time import time
# Create your views here.



def predicted_df(start_time,add_time,comments,tran):
    # this function retuns a dataframe (df) with the comments relvant to the seleceted time slot
    # inputs are the start and duration times of the sleceted time slot, a data frame with all the comments,
    # and a dataframe with the enitre transcript
    # bag of words and TF_IDF are trained on the trnascript, and then used to transform
    # both the transcript for the selected time slot of the video and all the comments

    Bow_transformer = bow_transformer(tran)
    Tf_idf_transformer = tf_idf_transformer(tran,Bow_transformer)

    tran_string_select=tf_idf_transform(select_script_transcript(start_time,add_time,tran),Tf_idf_transformer,Bow_transformer)

    comments['sim_score']=comments.Comment.apply(lambda s: cosine_similarity(tran_string_select, tf_idf_transform(s,Tf_idf_transformer,Bow_transformer) )[0][0] )

    return comments[comments.sim_score > 0.05].sort_values(by='sim_score',ascending=False)


def comments(request):   #request
    # get inputs from request:
    # get id and isolate it from extra info
    video_id=request.GET['video_id']
    video_id=video_id.split('&')[0]
    video_id=video_id.split('=')[0]

    #get start and duration time for slected time slot of video
    start=int(request.GET['start'])#
    duration=int(request.GET['duration'])#

    #get the transcript and comments of the video
    tran= get_transcript_df(video_id)
    comments= get_comments_df(video_id)

    # retun dataframe (df) with the comments relvant to the seleceted time slot
    comments_relevant_df = predicted_df(start, duration,comments,tran)

    # if comments are found, use comments in the df and construct the response dict
    comment_list = []
    found=False
    if len(comments_relevant_df) != 0:
        found = True
        i=0
        while i < len(comments_relevant_df):
            comment_likes = comments_relevant_df.iloc[i].Likes #number of likes
            comment_number_replies = comments_relevant_df.iloc[i].Replies  #number of replies
            comment_text = comments_relevant_df.iloc[i].Comment #comment text
            comment_author = comments_relevant_df.iloc[i].Author #comment Author
            comment_author_link = comments_relevant_df.iloc[i].Author_link #link to comment Author's page

            # add all the above information to comment list
            comment_list.append({
                'likes' : str(comment_likes),
                'Replies' : str(comment_number_replies),
                'Author' : str(comment_author),
                'Author_link' : str(comment_author_link),
                'comment_text' : comment_text
            })
            i+=1

    comment_dict = {
        'found' : found,
        'comments' : comment_list
    }

    # convert to json
    response = json.dumps(comment_dict)

    #print a time bar in terminal
    tic = time()
    print("Time lapse {}".format(time() - tic))

    #retrun the response that has the relvant comments, this is passsed to the chrome extension
    return HttpResponse(response)


########### scrap

##def index(request):
##    return HttpResponse("Hello, world. testing for comments")

  ##            comments_relevant_df.iloc[i]
##            commentor_name = comments_relevant_df.iloc[i].name  
