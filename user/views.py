import os
import uuid
from datetime import datetime
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.conf import settings

from blog.models import Blog
from .utils import create_thumbnail, save_image_file

# Create your views here.


def user_blogs(request, username):
    author = User.objects.filter(username=username).first()
    if author is None:
        messages.add_message(request, messages.INFO, "Blogger don't exist")
        return redirect(reverse('core:front_page'))

    author_blogs = Blog.objects.filter(author__username=username)
    displayable_blogs = author_blogs
    is_visitor_author = author.username == request.user.username
    if not is_visitor_author:
        displayable_blogs = author_blogs.filter(status=Blog.ACTIVE)
    displayable_blogs = displayable_blogs.order_by('-created_at')[:10]

    return render(request, 'user/user_blogs.html', {
        'blogs': displayable_blogs,
        'author': author,
        'is_visitor_author': is_visitor_author,
        'BLOG_STATUS': {
            'DRAFT': Blog.DRAFT,
            'ACTIVE': Blog.ACTIVE,
        },
    })


@login_required(login_url=reverse_lazy('core:login'))
def profile(request, username):
    if request.user.username != username:
        raise PermissionDenied

    if request.method == 'POST':
        user = request.user
        user_profile = request.user.rel_profile

        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.save()

        # format date before store
        # set birth_date to None if date field is empty
        date_string = request.POST['birth_date']
        if date_string:
            date_format = '%m/%d/%Y'
            temp_datetime = datetime.strptime(date_string, date_format)
            timezone_datetime = timezone.datetime(
                temp_datetime.year, temp_datetime.month, temp_datetime.day)
            timezone_date = timezone_datetime.date()
            user_profile.birth_date = timezone_date
        else:
            user_profile.birth_date = None

        # save profile picture
        profile_picture = request.FILES.get('profile_picture')
        if profile_picture is not None:
            # save file and a thumbnail copy
            _, image_ext = os.path.splitext(profile_picture.name)
            image_name = f'{uuid.uuid4()}{image_ext}'
            create_thumbnail(profile_picture, image_name)
            save_image_file(profile_picture, image_name)
            # then save the URI of the file
            user_profile.picture = os.path.join(
                settings.MEDIA_URL, 'thumbnails/', image_name)

        user_profile.bio = request.POST['bio']
        user_profile.location = request.POST['location']
        user_profile.save()

        messages.add_message(request, messages.SUCCESS,
                             'You successfully updated your profile.')

        return HttpResponseRedirect(reverse('user:profile', args=(request.user.username,)))

    user_profile = request.user.rel_profile
    user_info = {
        'username': request.user.username,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        # commented because planning to move this edit email to account view
        # 'email': request.user.email,
        'bio': user_profile.bio,
        'location': user_profile.location,
        'birth_date': user_profile.birth_date,
        'profile_picture': user_profile.picture,
    }

    return render(request, 'user/profile.html', {
        'user_info': user_info,
    })
