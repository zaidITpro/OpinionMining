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
import datetime
import re
from textblob import TextBlob
import time




def reddit_sentiment_analysis(reddit):
	positive=0
	negative=0
	neutral=0
	for element in reddit:
		analysis=TextBlob(element['title'])
		if analysis.sentiment.polarity>0:
			positive+=1
		if analysis.sentiment.polarity<0:
			negative+=negative
		else:
			neutral+=1
	polarity={'positive':positive,'negative':negative,'neutral':neutral}
	return polarity



def reddit_detailed_analysis(request):
	if request.user.is_authenticated():
		flag=0
		if request.session.get('search_keyword'):
			flag=1
			search_keyword=request.session['search_keyword']
			form=search_form()
			with open('reddit.json','r') as file:
				data=json.load(file)
			reddit=[]
			it=0
			temp_image='https://i.imgur.com/wesPbMx.jpg'
			whenCreated = {}
			dayofWeek = {}
			for post in data['data']['children']:
				d = time.strftime('%Y-%m-%d',time.localtime(post['data']['created_utc']))
				if not d in whenCreated:
					whenCreated[d] = 1
				else:
					whenCreated[d] += 1
				weekDay = time.strftime('%A',time.localtime(post['data']['created_utc']))
				if not weekDay in dayofWeek:
					dayofWeek[weekDay] = 1
				else:
					dayofWeek[weekDay] += 1
				reddit.append({'title':post['data']['title'],
					           'permalink':post['data']['permalink'],
					           'author':post['data']['author'],
					           'url':post['data']['url'],
					           'thumbnail':post['data']['thumbnail'],
					           'num_comments':post['data']['num_comments'],
					           'subreddit':post['data']['subreddit_name_prefixed'],
					           'thumbnail_height':post['data']['thumbnail_height'],
					           'thumbnail_width':post['data']['thumbnail_width']
					})
			polarity=reddit_sentiment_analysis(reddit)
			if 'https://www.reddit.com' in reddit[it]['url']:
				reddit[it]['url']=""
			if reddit[it]['thumbnail']=='self':
				reddit[it]['thumbnail']=temp_image
			it=it+1
			return render(request,'user/reddit.html',{'search_keyword':search_keyword,
				                                       'search_form':form,
				                                       'reddit':reddit,
				                                       'whenCreated':whenCreated,
				                                       'dayOfWeek':dayofWeek,
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
