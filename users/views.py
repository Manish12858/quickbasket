from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode, url_has_allowed_host_and_scheme

from .forms import CreateUserForm, LoginForm, UserUpdateForm
from .token import account_activation_token


def register(request):
    if request.user.is_authenticated:
        return redirect('index')
    form = CreateUserForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.is_active = False  # activated after the email link is clicked
        user.save()

        # Email verification
        message = render_to_string('users/email-verification.html', {
            'user': user,
            'protocol': request.scheme,
            'domain': get_current_site(request).domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        user.email_user(subject='Verify your email to activate your QuickBasket account', message=message)
        return redirect('email-verification-sent')
    return render(request, 'users/register.html', {'form': form})


def email_verification(request, uidb64, token):
    try:
        unique_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=unique_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('email-verification-success')
    return redirect('email-verification-failed')


def email_verification_sent(request):
    return render(request, 'users/email-verification-sent.html')


def email_verification_success(request):
    return render(request, 'users/email-verification-success.html')


def email_verification_failed(request):
    return render(request, 'users/email-verification-failed.html')


def user_login(request):
    if request.user.is_authenticated:
        return redirect('index')
    next_url = request.POST.get('next') or request.GET.get('next', '')
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
        ):
            return redirect(next_url)
        return redirect('index')
    return render(request, 'users/login.html', {'form': form, 'next': next_url})


def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('index')


@login_required
def profile(request):
    user_form = UserUpdateForm(request.POST or None, instance=request.user)
    if request.method == "POST" and user_form.is_valid():
        user_form.save()
        messages.success(request, 'Profile updated.')
        return redirect('profile')
    return render(request, 'users/profile.html', {'user_form': user_form})
