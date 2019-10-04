from django.shortcuts import render

import numpy as np
import pandas as pd

from extractor.views import get_authenticated_service, get_comments_df, select_script_transcript
from vectorizer.views import bow_transformer, tf_idf_transformer, tf_idf_transform
from sklearn.metrics.pairwise import cosine_similarity


from django.http import HttpResponse
import json
# Create your views here.



def predicted_df(start_time,add_time,comments,tran):
    
    Bow_transformer = bow_transformer(tran)
    Tf_idf_transformer = tf_idf_transformer(df,Bow_transformer)
    
    tran_string_select=tf_idf_transform(select_script_transcript(start,duration,tran),Tf_idf_transformer,Bow_transformer)
    
    comments['sim_score']=comments.Comment.apply(lambda s: cosine_similarity(tran_string_select, tf_idf_transform(s,Tf_idf_transformer,Bow_transformer) )[0][0] )
    
    return comments.sort_values(by='sim_score',ascending=False).head(3)


def comments():
    tran= select_script_transcript(video_id_input)
    comments= get_comments_df(video_id_input)

    comments_relevant_df = predicted_df(0,30,comments,tran)
    comment_list = []

    # if recommendations are found, find events in the list and construct the response dict
    if len(comments_df) != 0:
        found = True
        i=0
        while i < len(comments_relevant_df):
##            comments_relevant_df.iloc[i]
##            commentor_name = comments_relevant_df.iloc[i].name
            comment_likes = comments_relevant_df.iloc[i].Likes
            comment_number_replies = comments_relevant_df.iloc[i].Replies
            comment_text = comments_relevant_df.iloc[i].Comment

            comment_list.append({
                'likes' : comment_likes,
                'Replies' : comment_number_replies,
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


    
