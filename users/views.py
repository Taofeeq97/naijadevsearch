from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.contrib.auth import login,authenticate, logout
from .models import Profile,Skills, Message
from django.contrib.auth.models import User
from .forms import CutomUserCreationForm
from .forms import ProfileForm, SkillForm, MessageForm
from django.db.models import Q
from .utils import searchProfiles, paginateProfile
from .forms import Profile
# Create your views here.


def loginUser(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('profiles')

    if request.method == 'POST':
        username=request.POST['username'].lower()
        password = request.POST['password']

        try:
            user=User.objects.get(username=username)
        except:
            messages.error(request, 'username does not exist')

        user= authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect(request.GET['next'] if 'next' in request.GET else 'account')
        else:
            messages.error(request,'username or password incorrect')
    return render(request, 'users/login_register.html')

def logoutUser(request):
    logout(request)
    messages.info(request, 'user was successfully logged out')
    return redirect('login')

def registerUser(request):
    page='register'
    form=CutomUserCreationForm()

    if request.method=='POST':

        form=CutomUserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.username=user.username.lower()
            user.save()

            messages.success(request, 'User Account Created')

            login(request, user)
            return redirect('edit-account')
        else:
            messages.error(request, 'An error has occurred during registration')


    context={'page':page, 'form':form}
    return render(request, 'users/login_register.html', context)


def profiles(request):
    profiles, search_query = searchProfiles(request)

    custom_range, profiles =paginateProfile(request,profiles,6)
    context={'profiles':profiles, 'search_query':search_query, 'custom_range':custom_range}
    return render(request, 'users/profiles.html', context)


def usersProfile(request, pk):
    profile= Profile.objects.get(id=pk)

    topSkills= profile.skills_set.exclude(description__exact="")
    otherSkills = profile.skills_set.filter(description="")
    context={'profile':profile,'topSkills':topSkills, 'otherSkills':otherSkills}
    return render(request, 'users/user-profile.html', context)

@login_required(login_url='login')
def userAccount(request):
    profile=request.user.profile

    skills = profile.skills_set.all()
    projects= profile.project_set.all()
    context= {'profile':profile,'skills':skills, 'projects':projects}
    return render(request, 'users/account.html', context)


@login_required(login_url='login')
def editAccount(request):
    profile=request.user.profile
    form = ProfileForm(instance=profile)
    if request.method =='POST':
        form=ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()

            return redirect('account')
    context={'form':form}
    return render(request, 'users/profile_form.html', context)

@login_required(login_url='login')
def createSkill(request):
    profile=request.user.profile
    form = SkillForm

    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill= form.save(commit=False)
            skill.owner = profile
            skill.save()
            messages.success(request, 'New skill Added successfully')
            return redirect('account')

    context={'form':form}
    return render(request, 'users/skill_form.html', context)


@login_required(login_url='login')
def updateSkill(request, pk):
    profile = request.user.profile
    skill=profile.skills_set.get(id=pk)
    form = SkillForm(instance=skill)

    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Skill was updated')
            return redirect('account')
    context = {'form': form}
    return render(request, 'users/skill_form.html', context)

@login_required(login_url='login')
def deleteSkill(request, pk):
    profile= request.user.profile
    skill= profile.skills_set.get(id=pk)
    if request.method=='POST':
        skill.delete()
        messages.success(request, 'skill deleted successfully')
        return redirect('account')
    context = {'object':skill}
    return render(request, 'delete.html', context)


@login_required(login_url='login')
def inbox(request):
    profile = request.user.profile
    messageRequests= profile.messages.all()
    unreadCount=messageRequests.filter(is_read=False).count()
    context={'messageRequests':messageRequests, 'unreadCount':unreadCount}
    return render(request, 'users/inbox.html', context)

@login_required(login_url='login')
def viewMessage(request, pk):
    profile=request.user.profile
    message=profile.messages.get(id=pk)
    if message.is_read==False:

        message.is_read=True
        message.save()

    context={'message':message}
    return render(request, 'users/message.html', context)



def createMessage(request, pk):
    recipient= Profile.objects.get(id=pk)
    form= MessageForm()

    try:
        sender=request.user.profile
    except:
        sender=None

    if request.method=='POST':
        form=MessageForm(request.POST)
        if form.is_valid():
            message=form.save(commit=False)
            message.sender=sender
            message.recipient=recipient

            if sender:
                message.name=sender.name
                message.email = sender.email
            message.save()
            messages.success(request, 'Your message was successfully sent')
            return redirect('user-profiles', pk=recipient.id)

    context={'recipient':recipient, 'form':form}
    return render(request, 'users/message_form.html', context)