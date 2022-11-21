from django.views import generic
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from .forms import EditProfileForm
from .models import UserClasses, Class, UserToUserChat, Time, Day, meeting
import ast
import requests
from itertools import groupby
from django.core.exceptions import ValidationError


def index(request):
    if request.user.is_authenticated:
        if not request.user.day_set.all():
            days = ['M','T','W','Th','F','Sa','Su']
            for day in days:
                thisday = Day.objects.create(user= request.user, day = day)
                for j in range(10, 23):
                    Time.objects.create(day = thisday, time = str(j)+":00")
            

    return render(request, 'welcome/index.html')


class EditView(generic.UpdateView):
    form_class = EditProfileForm
    template_name = 'welcome/profile.html'
    success_url = reverse_lazy('index')

    def get_object(self):
        return self.request.user


def edit_classes(request):
    template_name = 'welcome/edit_classes.html'

    # Basic idea for displaying JSON into a view. Parse the JSON in here (or in another file/function?) 
    # and pass it as a list of lists (or other) in the render.

    dept_list = requests.get('http://luthers-list.herokuapp.com/api/deptlist/?format=json').json()
    return render(request, template_name, {'dept_list': dept_list})


def delete_class(request):
    template_name = 'welcome/edit_classes.html'
    try:
        selected_classes = request.POST.getlist('class_to_delete')
        class_ids = []
        for c in selected_classes:
            class_ids.append(request.user.userclasses_set.get(pk=c))
    except(KeyError):
        return HttpResponseRedirect(reverse('classes'))
    else:
        for id in class_ids:
            try:
                thisclass = Class.objects.get(id.subject +str(id.catalog_number))
                thisclass.students.remove(request.user)
            except:
                pass
            id.delete()

        return HttpResponseRedirect(reverse('classes'))

def add_classes(request):
    try:
        selected_classes = request.POST.getlist('class_to_add')
    except(KeyError):
        return HttpResponseRedirect(reverse('classes'))
    
    else:
        add = True
        for class_to_add in selected_classes:
            c = class_to_add.split("/")
            UserClasses.objects.create(user=request.user,subject=c[0], catalog_number=c[1], component=c[2], section=c[3], professor=c[4])
        return HttpResponseRedirect(reverse('classes'))


def subject_view(request, subject):
    classes = requests.get('http://luthers-list.herokuapp.com/api/dept/' + subject + '/?format=json').json()
    
    
    result = {
            key : list(group) for key, group in groupby(classes,key=lambda x:x['subject'] + " " + x['catalog_number'] + " " + x['description'])
           } 

    return render(request, 'welcome/subject.html', {'classes': result})

def search_classes(request):
    searchPhrase = request.POST['searchbox']
    foundClasses = []
    response = requests.get('http://luthers-list.herokuapp.com/api/dept/CS/?format=json').json()
    for thisClass in response:
        if searchPhrase in thisClass["description"]:
            foundClasses.append(thisClass)
    return render(request, 'welcome/home.html', {'response': foundClasses})

def update(request):
    try:
        selected_classes = request.POST.getlist('class_to_update')
        class_ids = []
        for c in selected_classes:
            class_ids.append(request.user.userclasses_set.get(pk=c))
    except(KeyError):
        return HttpResponseRedirect(reverse('index'))
    
    else:
        toAdd = []
        for c in request.user.userclasses_set.all():
            
            if c in class_ids:
                c.available = True
                c.save()
                try:
                    thisclass = Class.objects.get(Name = c.subject +str(c.catalog_number))
                except:
                    thisclass = Class.objects.create(Name =c.subject +str(c.catalog_number))

                toAdd.append(thisclass)
                
            else:
                c.available = False
                c.save()
                try:
                    thisclass = Class.objects.get(Name= c.subject + str(+c.catalog_number))
                    thisclass.students.remove(request.user)
                except:
                    pass
        for each in toAdd:
            each.students.add(request.user)
                
        return HttpResponseRedirect(reverse('index'))

def rooms(request):
    
    rooms = UserToUserChat.objects.filter(user1=request.user) | UserToUserChat.objects.filter(user2=request.user)

    return render(request, 'welcome/rooms.html', {'rooms': rooms})


def room(request, room_name):
    if not UserToUserChat.objects.filter(roomName=room_name):
        return HttpResponseRedirect(reverse('index')) #doesn't exist
    
    room = UserToUserChat.objects.get(roomName=room_name)
    if(request.user != room.user1 and request.user != room.user2):
        return HttpResponseRedirect(reverse('index')) #not allowed
    
    return render(request, 'welcome/room.html', {'room_name': room_name})
  
def updateTimes(request):
    try:
        ids = request.POST.getlist('available_times')
    except(KeyError):
        return HttpResponseRedirect(reverse('index'))

    for day in request.user.day_set.all():
        for time in day.time_set.all():
            if day.day+time.time in ids:
                time.available = True
                time.save()
            else:
                time.available = False
                time.save()



    return HttpResponseRedirect(reverse('index'))

def new_meeting(request, reciever_id):
    reciever = User.objects.get(pk=reciever_id)
    return render(request, "welcome/newmeeting.html", {'reciever' : reciever, 'errmsg':''})

def confirm_meeting(request, reciever_id):
    reciever = User.objects.get(pk=reciever_id)
    title = request.POST.get('title')
    date = request.POST.get('date')
    time = request.POST.get('time')

    
    try:
        newmeeting= meeting.objects.create(title=title, date=date, time=time)
    except(ValidationError):
        return render(request, "welcome/newmeeting.html", {'reciever' : reciever, 'errmsg':'Please fill out all fields.'})
    newmeeting.participants.add(request.user, reciever)
    newmeeting.save()

    return HttpResponseRedirect(reverse('index'))

