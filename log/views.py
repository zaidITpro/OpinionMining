from django.shortcuts import render

# Create your views here.

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
import facebook
import json
from twython import Twython

def home(request):
	if request.user.is_authenticated():
		return redirect('user')
	return render(request,"home.html")

def signup(request):
	if request.method=="POST":
		form=signup_form(request.POST or None)
		if form.is_valid():
			user_name=form.cleaned_data['user_name']
			try:
				User.objects.get(username=user_name)
				error="This username is already registered"
				return render(request,'signup.html',{'form':form,'error':error})
			except:
				IntegrityError
			useremail=request.POST.get('user_email')
			try:
				User.objects.get(email=useremail)
				error="User with this email already exist"
				return render(request,"signup.html",{'form':form,'error':error})
			except:
				ObjectDoesNotExist
			user_password=request.POST.get('user_password')
			if len(user_password)<8:
				error="Password length should not be less than 8"
				return render(request,"signup.html",{'form':form,'error':error})
			user_confirmpassword=request.POST.get('user_confirmpassword')
			if user_password!=user_confirmpassword:
				error="password do not match"
				return render(request,'signup.html',{'form':form,'error':error})
			user_email=form.cleaned_data['user_email']
			user_password=form.cleaned_data['user_password']
			user=User.objects.create_user(username=user_name,password=user_password,email=user_email)
			login(request,user)
			return redirect('user')
	else:
		form=signup_form()
	args={}
	args.update(csrf(request))
	return render(request,"signup.html",{'form':form})




def signin(request):
	if request.user.is_authenticated():
		return redirect('user')
	if request.method=="POST":
		form=login_form(request.POST)
		user=authenticate(username=request.POST.get('user_name'),password=request.POST.get('user_password'))
		if user is not None:
			login(request,user)
			return redirect('user')
		else:
			error="Username and password do not match"
			return render(request,'login.html',{'form':form,'error':error})
	form=login_form()
	return render(request,'login.html',{'form':form})


def user(request):
	if request.user.is_authenticated():
		flag=0
		if request.method=="POST":
			form=search_form(request.POST)
			search_keyword=request.POST.get('search_query')
			request.session['search_keyword']=search_keyword
			#twitter_data=twitter_scraper(search_keyword)
			twitter_data=dict()
			reddit_data=reddit_scraper(search_keyword)
			return render(request,'user/user.html',{'search_form':search_form,
				                                    'twitter_data':twitter_data,
				                                    'search_keyword':search_keyword,
				                                    'reddit_data':reddit_data,
			})
		else:
			form=search_form()
			return render(request,'user/user.html',{'search_form':form,'flag':flag})
	else:
		return redirect('signin')



def loggedin(request):
	return render(request,'loggedin.html')

def logout_view(request):
	logout(request)
	return redirect('signin')


#functions called by the user view
#fb_data Scraper
def page_id_scraper(input_string,access_token):
	graph=facebook.GraphAPI(access_token)
	initial_result=graph.request('/search?q='+input_string+'&type=page&limit=5')
	page_id_list=[]
	for j in range(0,len(initial_result['data'])):
		page_id_list.append(initial_result['data'][j]['id'])
	return page_id_list



def facebook_scraper(input_string):
	base="https://graph.facebook.com/v2.10"
	access_token='EAAEUBL0BioABAFZCNiJVwueBJLu4z0NW1oAJZBhremDYKnmWJr2SOhPuvTWZCCq94IutkedUDZB8PvAkFZAfkLoBtna1UzZBZBZCPh0T5K1yayZBucLDCDhyVwouz6CW1ZBAC5xnspzq9t9z9SBLe4l5IYgqeOg0FUF70ZCHCQLKZAT1QgZDZD'
	page_id_list=page_id_scraper(input_string,access_token)
	likes_count="reactions.type(LIKE).limit(0).summary(total_count).as(like),"
	love_count="reactions.type(LOVE).limit(0).summary(total_count).as(love),"
	wow_count="reactions.type(WOW).limit(0).summary(total_count).as(wow),"
	haha_count="reactions.type(HAHA).limit(0).summary(total_count).as(haha),"
	sad_count="reactions.type(SAD).limit(0).summary(total_count).as(sad),"
	angry_count="reactions.type(ANGRY).limit(0).summary(total_count).as(angry)"
	fields="/?fields=comments,"+likes_count+love_count+wow_count+haha_count+sad_count+angry_count
	comment_result=[]
	total_like_count=0
	total_love_count=0
	total_haha_count=0
	total_wow_count=0
	total_sad_count=0
	total_angry_count=0
	parameters='&limit=%s&access_token=%s' % (5,access_token)
	for j in range(0,len(page_id_list)):
		node='/%s/posts' % page_id_list[j]
		url=base+node+fields+parameters
		response=requests.get(url)
		result=response.json()
		for k in range(0,len(result['data'])):
			comment_result.append(result)
			total_like_count=total_like_count+result['data'][k]['like']['summary']['total_count']
			total_love_count=total_love_count+result['data'][k]['love']['summary']['total_count']
			total_wow_count=total_wow_count+result['data'][k]['wow']['summary']['total_count']
			total_haha_count=total_haha_count+result['data'][k]['haha']['summary']['total_count']
			total_sad_count=total_sad_count+result['data'][k]['sad']['summary']['total_count']
			total_angry_count=total_angry_count+result['data'][k]['angry']['summary']['total_count']
	with open('facebook_result.json','w') as fp:
		json.dump(comment_result,fp,indent=2)
	fb_data_list={'like':total_like_count,'love':total_love_count,
	              'haha':total_haha_count,'sad':total_sad_count,
	              'angry':total_angry_count,'wow':total_wow_count
	}
	return fb_data_list


#facebook sraper ends

#Twitter Scraper Starts
def twitter_scraper(input_string):
	tweets                          =   []
	MAX_ATTEMPTS                    =   40
	COUNT_OF_TWEETS_TO_BE_FETCHED   =   1000
	client_api='FM3nYXvUHfNAPTEBgM69pKAdb'
	client_secret='8LXbtMybMsEZe0Bz3OoWvIzK4crV9HVZBRNUi2agNOVfyuiu6A'
	access_token='4834720380-dzufecsaD6GfMCG24OCSACLUtnMlOte1zBxUo8a'
	access_token_secret='lZd7RiVbY3Bhn2iK2r7n8kC9fPXy7yUANz8WhqAwmQGWO'
	api=Twython(client_api,client_secret,access_token,access_token_secret)
	retweetcount=0
	favoritecount=0
	next_max_id=0
	length=0
	for i in range(0,MAX_ATTEMPTS):
		if(i==0):
			results=api.search(q=input_string,include_entities=True,result_type='popular')
		else:
			results=api.search(q=input_string,include_entities=True,max_id=next_max_id,result_type='recent')
		tweets.append(results)
		length=length+len(results['statuses'])
		for key in range(0,len(results['statuses'])):
			retweetcount=retweetcount+results['statuses'][key]['retweet_count']
			favoritecount=favoritecount+results['statuses'][key]['favorite_count']
			try:
				next_results_url_params=results['search_metadata']['next_results']
				next_max_id=next_results_url_params.split('max_id=')[1].split('&')[0]
			except:
				break
	with open('twitter_result.json','w') as fp:
		json.dump(tweets,fp,indent=2)
	return {'retweet_count':retweetcount,'favorite_count':favoritecount}



def reddit_scraper(input_string):
	client_id='Xt33Q1ZzsJUYug'
	client_secret='4zvXkE-r32e8plH1O8oSq5qg1Xc'
	password='Zaidcool#004'
	username='zaid9910'
	user_agent='my agent'
	up_vote=0
	num_comments=0
	try:
		base_url='https://www.reddit.com/search.json?q='+input_string+'&sort=new&limit=1000'
		data=requests.get(base_url,headers={"User-agent":'my agent'})
		if data.status_code!=200:
			return {'up_vote':up_vote,'num_comments':num_comments}
		else:
			content=data.json()
			for post in content['data']['children']:
				up_vote=up_vote+post['data']['ups']
				num_comments=num_comments+post['data']['num_comments']
			with open('reddit.json','w') as file:
				json.dump(content,file,indent=2)
	except:
		pass
	return {'up_vote':up_vote,'num_comments':num_comments}