from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from .models import User, Theater
from django.contrib import messages
from django.utils import timezone, timesince
import pytz
import bcrypt
import requests
import isodate

def youtubeSearch(count, searchContent):
    URL_s = "https://www.googleapis.com/youtube/v3/search"
    URL_v = "https://www.googleapis.com/youtube/v3/videos"

    # location given here
    part = 'snippet'
    maxResults = count
    order = 'relevance'
    q = searchContent
    key = 'AIzaSyBZIVFuvqKuE_rL--VRA0gsuWUCvOCDU-w'

    # defining a params dict for the parameters to be sent to the API 
    PARAMS = {
        'part'          :   part,
        'maxResults'    :   maxResults,
        'order'         :   order,
        'q'             :   q,
        'type'          :   'video',
        'key'           :   key,
        }
    
    # sending get request and saving the response as response object 
    r = requests.get(url = URL_s, params = PARAMS) 
    
    raw_data = r.json()
    
    results = raw_data['items']
    videos = []
    # Print the first video's title
    for result in results:
        raw_data = youtubeSearchVideo(result['id']['videoId'], 'contentDetails')
        raw_duration = raw_data['items'][0]['contentDetails']['duration']
        duration = str(isodate.parse_duration(raw_duration))

        video = {
            'title' :   result['snippet']['title'],
            'img'   :   result['snippet']['thumbnails']['medium']['url'],
            'id'    :   result['id']['videoId'],
            'length':   duration,
        }
        videos.append(video)
    
    return videos

# Get info
def youtubeSearchVideo(vid, part):
    URL_v = "https://www.googleapis.com/youtube/v3/videos"

    # location given here
    key = 'AIzaSyBZIVFuvqKuE_rL--VRA0gsuWUCvOCDU-w'

    # defining a params dict for the parameters to be sent to the API 
    PARAMS = {
        'id'            :   str(vid),
        'key'           :   key,
        'part'          :   part,
    }
    
    # sending get request and saving the response as response object 
    r = requests.get(url = URL_v, params = PARAMS) 
    
    raw_data = r.json()
    return raw_data

# Create your views here.
def index(request):
    return redirect('/utubegroupies')

def home(request):
    if 'id' in request.session:
        return redirect('/utubegroupies/dashboard')

    return render(request, 'home.html')

def regLoginPage(request):
    return render(request, 'login.html')

def processRegister(request):
    if 'id' in request.session:
        return redirect('/utubegroupies/dashboard')
    
    errors = User.objects.reg_validator(request.POST)
    print(errors)
    
    if len(errors):
        for key, value in errors.items():
            messages.error(request, value, extra_tags=key)
        return redirect('/utubegroupies/signup')
            
    currentTime = timezone.now()
    
    # Hash password and prepare for registration
    pw_hash = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt())
    newUser = User.objects.create(first_name=request.POST['fName'], last_name=request.POST['lName'], 
        email=request.POST['email'], password=pw_hash, created_at = currentTime, updated_at = currentTime)
    request.session['id'] = newUser.id

    return redirect('/utubegroupies/dashboard')

def processRegisterEmail(request):
    email = request.POST['email']

    data = {
        'is_valid'  :   User.objects.email_validator_regex(email)
    }
    print(data['is_valid'])
    if not data['is_valid']:
        data['error_message'] = "Please enter a valid email address"
        return JsonResponse(data)

    data['is_taken'] =User.objects.email_validator_db(email)

    if data['is_taken']:
        # messages.error(request, "Email address already taken", extra_tags='email')
        data['error_message'] = "Email address already taken"
    else:
        print("Email is free to use")
    
    return JsonResponse(data)


def processLogin(request):
    if 'id' in request.session:
        return redirect('/utubegroupies/dashboard')
    
    print(request.POST)
    errors = User.objects.login_validator(request.POST)

    if len(errors):
        for key, value in errors.items():
            messages.error(request, value, extra_tags=key)
        return redirect('/utubegroupies/signup')
    
    user = User.objects.get(email=request.POST['emailL'])
    
    request.session['id'] = user.id

    return redirect('/utubegroupies/dashboard')

def processLoginEmail(request):
    email = request.POST['email']
    data = {
        'is_taken'  :   User.objects.email_validator_db(email)
    }
    if not data['is_taken']:
        data['error_message'] = "Email address entered was not found, please register"
    
    return JsonResponse(data)

def dashboard(request):
    if 'id' not in request.session:
        return redirect('/')

    this_user = User.objects.get(id=request.session['id'])
    
    data = {
        'user'          :   this_user,
        'events'        :   this_user.events.all(),
        'invitations'   :   this_user.invitations.all(),
    }
    print("Data is", data)
    return render(request, 'dashboard.html', data)

def createSesh(request):
    if 'id' not in request.session:
        return redirect('/')
    
    data = {}
    if 'sesh_name' in request.session:
        data['sesh_name'] = request.session['sesh_name']
        data['video_search'] = request.session['video_search']

    return render(request, 'create_sesh.html', data)

def searchYoutube(request):
    if 'id' not in request.session:
        return redirect('/')

    print(request.POST)
    
    request.session['sesh_name'] = request.POST['name']
    request.session['video_search'] = request.POST['video_search']

    request.session['videos'] = youtubeSearch(5, request.POST['video_search'])
    
    return redirect('/utubegroupies/dashboard/createSesh/videoSearch/videoResults')

def searchUsers(request):
    if 'id' not in request.session:
        return redirect('/')

    if 'invitees' not in request.session:
        request.session['invitees'] = []
    
    rawData = youtubeSearchVideo(request.session['videoId'], "snippet")
    img_url = rawData['items'][0]['snippet']['thumbnails']['medium']['url']
    title = rawData['items'][0]['snippet']['title']

        
    data = {
        'sesh_name' :   request.session['sesh_name'],
        'video_name':   title,
        'video_img' :   img_url,
        'invitees'  :   request.session['invitees'],
    }

    print(data)

    return render(request, 'cs-searchUsers.html', data)

def searchResultsYT(request):
    data = {}

    if 'videos' in request.session:
        data['videos'] = request.session['videos']
        request.session.pop('videos')

    return render(request, 'cs-resultsVids.html', data)

def searchResultsUsers(request):
    searchStr = request.POST['userStr']
    uid = request.session['id']
    users = (User.objects.filter(first_name__contains=searchStr).exclude(id=uid) | 
        User.objects.filter(last_name__contains=searchStr).exclude(id=uid) | 
        User.objects.filter(email__contains=searchStr).exclude(id=uid))        

    data = {
        'users' :   [],
    }
    for user in users:
        newUser = {}
        newUser['first'] = user.first_name
        newUser['last'] = user.last_name
        newUser['id'] = user.id
        data['users'].append(newUser)

    return JsonResponse(data)


def addVideoToSesh(request, vid):
    print(vid)

    request.session['videoId'] = str(vid)

    return redirect('/utubegroupies/dashboard/createSesh/usersSearch')

def addUserToSesh(request, uid):
    print(uid)

    raw_user = User.objects.get(id=uid)
    print(raw_user)
    user = {
        'first_name'    :   raw_user.first_name,
        'last_name'     :   raw_user.last_name,
        'user_ID'       :   raw_user.id,
    }
    users = request.session['invitees']
    users.append(user)
    request.session['invitees'] = users

    return redirect('/utubegroupies/dashboard/createSesh/usersSearch')

def submitSesh(request):
    currentTime = timezone.now()

    rawData = youtubeSearchVideo(request.session['videoId'], "snippet")
    img_url = rawData['items'][0]['snippet']['thumbnails']['medium']['url']

    sesh = {
        'name'      :   request.session['sesh_name'],
        'video'     :   request.session['videoId'],        
        'organizer' :   User.objects.get(id=request.session['id']),
    }
    print(sesh)

    new_sesh = Theater.objects.create(name=sesh['name'], video_id=sesh['video'], video_img=img_url, created_at=currentTime, updated_at=currentTime, organizer=sesh['organizer'])
    print(new_sesh)
    for invitee in request.session['invitees']:
        new_invitee = User.objects.get(id=invitee['user_ID'])
        new_sesh.invitees.add(new_invitee)
        new_sesh.save()
        print(new_sesh.invitees.all())
    
    new_sesh.attendees.add(sesh['organizer'])

    request.session.pop('sesh_name')
    request.session.pop('videoId')

    return redirect('/')

def acceptInvitation(request, id):
    if 'id' not in request.session:
        return redirect('/')

    sesh = Theater.objects.get(id=id)
    user = User.objects.get(id=request.session['id'])
    sesh.attendees.remove(user)
    sesh.attendees.add(user)
    sesh.save()
    user.invitations.remove(sesh)
    user.save()

    return redirect('/')

def showSesh(request, id):
    if 'id' not in request.session:
        return redirect('/')
    
    user = User.objects.get(id=request.session['id'])
    sesh = Theater.objects.get(id=id)
    sesh.crashers.add(user)
    uid = sesh.video_id
    raw_video = youtubeSearchVideo(uid, 'snippet')
    print(raw_video)
    img_url = raw_video['items'][0]['snippet']['thumbnails']['maxres']['url']
    print(img_url)
    
    data = {
        'video_id'      :   sesh.video_id,
        'img_url'       :   img_url,
    }

    return render(request, 'theater_room.html', data)

def logout(request):
    if 'id' not in request.session:
        return redirect('/')
    
    request.session.clear()

    return redirect('/')