from django.views import generic
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm

from django.shortcuts import redirect
from .forms import EditProfileForm
from .models import UserClasses
from .models import Class
import ast
import requests
from itertools import groupby
from .models import Friend_Request
from .models import Class
from .models import FriendList



def index(request):
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
                    thisclass = Class.objects.get(Name=c.subject + str(c.catalog_number))
                except:
                    thisclass = Class.objects.create(Name=c.subject + str(c.catalog_number))

                toAdd.append(thisclass)

            else:
                c.available = False
                c.save()
                try:
                    thisclass = Class.objects.get(Name=c.subject + str(+c.catalog_number))
                    thisclass.students.remove(request.user)
                except:
                    pass
        for each in toAdd:
            each.students.add(request.user)

        return HttpResponseRedirect(reverse('index'))


def send_friend_request(request, userID):
    from_user = request.user
    to_user = User.objects.get(id=userID)
    current_list = FriendList.objects.select_related().filter(user=request.user.id)
    friend_list = current_list.first().friends
    friend_request, created = Friend_Request.objects.get_or_create(from_user=from_user, to_user=to_user)
    if created:
        return HttpResponseRedirect(reverse('index'), {'friend_list': friend_list})
    else:
        return HttpResponseRedirect(reverse('index'), {'friend_list': friend_list})


def accept_friend_request(request, requestID):
    friend_request = Friend_Request.objects.get(id=requestID)
    current_list = FriendList.objects.select_related().filter(user=request.user.id)
    if not current_list.exists():
        friend_list = FriendList()
        friend_list.user = friend_request.to_user
        friend_list.save()
        friend_list.friends.add(friend_request.from_user)
        friend_list.save()
        # trying to add user back on both lists
        # friend_list.from_user
        if request.method == "POST":
            friend_request.delete()
        return HttpResponseRedirect(reverse('friends'), {'friend_list': friend_list.friends})
    for i in current_list:
        i.friends.add(friend_request.from_user)
        if request.method == "POST":
            friend_request.delete()
            return HttpResponseRedirect(reverse('friends'), {'friend_list': i.friends})


    #for i in FriendList.objects.all():
        #if friend_request.to_user.id == i.user.id:
            #i.friends.add(friend_request.from_user)
            #if request.method == "POST":
                #friend_request.delete()
                #return HttpResponseRedirect(reverse('friends'), {'friend_list': i.friends})
            #return HttpResponseRedirect(reverse('friends'), {'friend_list': i.friends})
        # trying to add user back on both lists
        # if friend_request.from_user == i.user.userID:
            # i.friends.add(friend_request.to_user)

    #friend_list = FriendList()
    #friend_list.user = friend_request.to_user
    #friend_list.save()
    #friend_list.friends.add(friend_request.from_user)
    #friend_list.save()
        # trying to add user back on both lists
        # friend_list.from_user
    #if request.method == "POST":
        #friend_request.delete()
    #return HttpResponseRedirect(reverse('friends'), {'friend_list': friend_list.friends})


def decline_friend_request(request,requestID):
    friend_request = Friend_Request.objects.get(id=requestID)
    if request.method == "POST":
        friend_request.delete()
        return HttpResponseRedirect(reverse('friends'))
    return HttpResponseRedirect(reverse('friends'))


def study_partners(request):
    if request.user.UserClasses.available == True:
        same_classes_available = UserClasses.objects.filter(search_classes=request.user.UserClasses.search_class, available=True).exclude(id=request.user.id)
        return render(request, 'welcome/index.html', {'user': request.user, 'other_users': same_classes_available})
    else:
        return render(request, 'welcome/index.html')


def friends(request):
    current_list = FriendList.objects.select_related().filter(user=request.user.id)
    try:
        friend_list = current_list.first().friends
    except(AttributeError):
        friend_list = []

    try:
        friend_request = Friend_Request.objects.filter(to_user=request.user.id)
    except(AttributeError):
        friend_request = []
    return render(request, 'welcome/friends.html', {'friends': friend_request, 'friend_list': friend_list})


# Things to ask about:
# How to disable a button and make it say sent after friend request was sent
# How to make sure you cannot send a friend request to someone twice
# Add a logout feature
# Adding friends to both lists once you accept them
# Removing friends from a list
# Fix HTML so users do not show up multiple times when trying to find buddies
