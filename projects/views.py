from django.shortcuts import render, redirect
from .models import Project,Review,Tag
from .forms import ProjectForm,ReviewForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .utils import searchProjects, paginateProject
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages






def projects(request):
    projects,search_query = searchProjects(request)

    custom_range, projects=paginateProject(request, projects, 6)
    context={'project':projects, 'search_query':search_query, 'custom_range':custom_range}
    return render(request, 'projects/projects.html',context)

def project(requests, pk):
    projectObj=Project.objects.get(id=pk)
    form=ReviewForm()
    if requests.method=='POST':
        form= ReviewForm(requests.POST)
        review=form.save(commit=False)
        review.project= projectObj
        review.owner= requests.user.profile
        review.save()
        projectObj.getVoteCount
        messages.success(requests, 'Your review was successfully submitted')
        return redirect('project',pk=projectObj.id)

    return render(requests, 'projects/single-project.html',{'projectitem':projectObj, 'form':form})

@login_required(login_url='login')
def createProject(requests):
    profile=requests.user.profile
    form=ProjectForm()
    if requests.method == 'POST':
        newtags = requests.POST.get('newtags').replace(',', ' ').split()
        form=ProjectForm(requests.POST, requests.FILES)
        if form.is_valid():
            project= form.save(commit=False)
            project.owner = profile
            project.save()
            for tag in newtags:
                tag, created = Tag.objects.get_or_create(name=tag)
                project.tags.add(tag)
            return redirect('projects')
    context={'form':form}
    return render(requests, 'projects/project_form.html', context)


@login_required(login_url='login')
def updateProject(requests, pk):
    profile=requests.user.profile
    project=profile.project_set.get(id=pk)
    form=ProjectForm(instance=project)
    if requests.method == 'POST':

        newtags= requests.POST.get('newtags').replace(',',' ').split()

        form=ProjectForm(requests.POST, requests.FILES, instance=project)
        if form.is_valid():
            project = form.save()
            for tag in newtags:
                tag, created =Tag.objects.get_or_create(name=tag)
                project.tags.add(tag)
            return redirect('account')
    context={'form':form, 'project':project}
    return render(requests, 'projects/project_form.html', context)


@login_required(login_url='login')
def deleteProject(requests,pk):
    profile = requests.user.profile
    project=profile.project_set.get(id=pk)
    if requests.method=='POST':
        project.delete()
        return redirect('account')
    context={'object':project}
    return render(requests, 'delete.html', context)