from django.shortcuts import render
from django.shortcuts import render
from django.views import View
from .models import CustomUser, Profile, Code
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login

from .forms import SignUpForm, SignInForm, ProfileFillForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from pytz import timezone
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from utils.other import expires


@cache_page(expires(minutes=15))
def sign_up(request, invited_with=''):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    else:
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                user = form.save()
                if user is not None:
                    login(request, user)
                    return HttpResponseRedirect(f'/user_{user.pk}/edit/')
                else:
                    return HttpResponseRedirect(f'/login/')
        else:
            form = SignUpForm()

        return render(request, 'auth/register.html', {'form': form, 'code': invited_with})

@cache_page(expires(minutes=15))
def sign_in(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    else:
        if request.method == 'POST':
            form = SignInForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                user = authenticate(email=cd['email'], password=cd['password'])
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return HttpResponseRedirect('/')
                    else:
                        return HttpResponseRedirect('/login/')
                else:
                    return HttpResponseRedirect('/login/')
        else:
            form = SignInForm()

            return render(request, 'auth/login.html', {'form': form})


@login_required()
def log_out(request):
    logout(request)
    return HttpResponseRedirect('/login/')


@login_required()
def profile_edit(request, pk):
    if request.user.pk != pk:
        raise PermissionDenied
    else:
        if request.method == 'POST':
            instance = get_object_or_404(Profile, owner=request.user)
            form = ProfileFillForm(request.POST, request.FILES, instance=instance)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.finished = True
                profile.save()
                return HttpResponseRedirect('/')
        else:
            profile = request.user.profile
            if not profile.finished:
                images = True
            else:
                images = False
            form = ProfileFillForm(images=images)
        return render(request, 'main/edit.html', {'form': form, 'profile': profile})

@cache_page(expires(minutes=15))
@login_required()
def main(request):
    user = request.user
    if not user.profile.finished:
        HttpResponseRedirect(f'/user_{user.pk}/edit/')
    else:
        last_ten = Profile.objects.all().order_by('-id')[:10]
        first_five = []
        second_five = []
        for i in range(10):
            try:
                profile = last_ten[i]
            except IndexError:
                break
            if i < 5:
                first_five.append({'pk': profile.owner_id,
                                   'name': f'{profile.first_name} {profile.last_name}',
                                   'avatar': profile.avatar.url})
            else:
                second_five.append({'pk': profile.owner_id,
                                    'name': f'{profile.first_name} {profile.last_name}',
                                    'avatar': profile.avatar.url})

        number_of_users = cache.get('number_of_users')
        if number_of_users is None:
            number_of_users = CustomUser.objects.count()
            cache.set('number_of_users', number_of_users, expires(hours=1))

        return render(request, 'main/main.html', {'first': first_five,
                                                  'second': second_five,
                                                  'num_of_us': number_of_users,
                                                  'pk': user.pk})

@login_required()
def user_profile(request, pk):
    user = request.user
    if not user.profile.finished:
        HttpResponseRedirect(f'/user_{user.pk}/edit/')
    else:
        if pk == user.pk:
            is_owner = True
        else:
            is_owner = False

        profile = Profile.objects.get(owner_id=pk)
        code = Code.objects.get(owner_id=pk)
        number_of_users = cache.get('number_of_users')
        if number_of_users is None:
            number_of_users = CustomUser.objects.count()
            cache.set('number_of_users', number_of_users, expires(hours=1))
        context = dict(profile=profile,code=code,is_owner=is_owner,num_of_us=number_of_users,pk=user.pk)
        return render(request, f'main/plates/{profile.template}.html', context)


# Create your views here.
