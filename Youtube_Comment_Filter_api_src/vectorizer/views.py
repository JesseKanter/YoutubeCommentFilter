from django.shortcuts import render

# Create your views here.
import pandas as pd
import string
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from nltk.corpus import stopwords

def text_process(mess):
    """
    Takes in a string of text, then performs the following:
    1. Remove all punctuation
    2. Remove all stopwords
    3. Returns a list of the cleaned text
    """
    # Check characters to see if they are in punctuation
    nopunc = [char for char in mess if char not in string.punctuation]

    # Join the characters again to form the string.
    nopunc = ''.join(nopunc)
    
    # Now just remove any stopwords
    return [word for word in nopunc.split() if word.lower() not in stopwords.words('english')]

#creates a bag of words transformer for a data frame with a text column
def bow_transformer(df):
    return CountVectorizer(analyzer=text_process).fit(df['text'])

#creates a Tf_Idf transformer for a specific Bag of words (Bow) transformed data frame with a text column
def tf_idf_transformer(df,Bow_transformer):
    return TfidfTransformer().fit(Bow_transformer.transform(df['text']))

#trnasforms a given text with a specific Tf_idf and Bow transformer
def tf_idf_transform(text,Tf_idf_transformer,Bow_transformer):
    return Tf_idf_transformer.transform(Bow_transformer.transform([text]))
    
