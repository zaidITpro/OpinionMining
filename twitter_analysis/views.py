from django.shortcuts import render

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from log.forms import signup_form,login_form,search_form
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import redirect
from django.template.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.contrib.auth import authenticate,login
from django.contrib.auth import logout
import requests
import json
from twython import Twython
import datetime
import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
# Create your views here.
def clean_tweet(tweet):
	return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z\t])|(\w+:\/\/\S+)"," ",tweet).split())


def get_tweet_sentiment(tweet):
	analysis=TextBlob(clean_tweet(tweet))
	if analysis.sentiment.polarity>0:
		return 'positive'
	elif analysis.sentiment.polarity==0:
		return 'neutral'
	else:
		return 'negative'



def sentiment_analysis(tweet_data):
	count=0
	pos_polarity=[]
	neg_polarity=[]
	neutral_polarity=[]
	likes=0
	for element in tweet_data:
		for j in element['statuses']:
			polarity=get_tweet_sentiment(j['text'])
			if polarity=='positive':
				pos_polarity.append(j['text'])
			elif polarity=='negative':
				neg_polarity.append(j['text'])
			else:
				neutral_polarity.append(j['text'])
			likes=likes+1
	polarity={'positive':len(pos_polarity),
	          'negative':len(neg_polarity),
	          'neutral': len(neutral_polarity),
	          'likes':likes
	}
	return polarity


def twitter_detailed_analysis(request):
	if request.user.is_authenticated():
		flag=0
		if request.session.get('search_keyword'):
			flag=1
			search_keyword=request.session['search_keyword']
			form=search_form()
			with open('twitter_result.json','r') as file:
				data=json.load(file)
			polarity=sentiment_analysis(data)
			return render(request,'user/twitter.html',{'search_keyword':search_keyword,
				                                       'search_form':form,
				                                       'tweets':data,
				                                       'polarity':polarity
				})
		else:
			if not flag:
				error="please enter the keyword first"
				return redirect('user')
			else:
				return render(request,'user/twitter.html',{'search_keyword':search_keyword,'search_form':form})
	else:
		return redirect('signin')


