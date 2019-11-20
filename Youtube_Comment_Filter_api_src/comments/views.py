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

    Bow_transformer = bow_transformer(tran)
    Tf_idf_transformer = tf_idf_transformer(tran,Bow_transformer)

    tran_string_select=tf_idf_transform(select_script_transcript(start_time,add_time,tran),Tf_idf_transformer,Bow_transformer)

    comments['sim_score']=comments.Comment.apply(lambda s: cosine_similarity(tran_string_select, tf_idf_transform(s,Tf_idf_transformer,Bow_transformer) )[0][0] )

    return comments.sort_values(by='sim_score',ascending=False).head(3)


def comments(request):   #request
    video_id=request.GET['video_id']
    video_id=video_id.split('&')[0]
    video_id=video_id.split('=')[0]
    tran= get_transcript_df(video_id)
    comments= get_comments_df(video_id)

    tic = time()

    start=int(request.GET['start'])#
    duration=int(request.GET['duration'])#
    comments_relevant_df = predicted_df(start, duration,comments,tran)
    comment_list = []

    # if recommendations are found, find events in the list and construct the response dict
    if len(comments_relevant_df) != 0:
        found = True
        i=0
        while i < len(comments_relevant_df):
##            comments_relevant_df.iloc[i]
##            commentor_name = comments_relevant_df.iloc[i].name
            comment_likes = comments_relevant_df.iloc[i].Likes
            comment_number_replies = comments_relevant_df.iloc[i].Replies
            comment_text = comments_relevant_df.iloc[i].Comment
            comment_author = comments_relevant_df.iloc[i].Author
            comment_author_link = comments_relevant_df.iloc[i].Author_link


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

    response = json.dumps(comment_dict)

    print("Time lapse {}".format(time() - tic))
    return HttpResponse(response)

##def index(request):
##    return HttpResponse("Hello, world. testing for comments")

    
