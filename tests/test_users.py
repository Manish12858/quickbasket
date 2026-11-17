import re

from django.contrib.auth.models import User
from django.urls import reverse

from tests.conftest import PASSWORD

REGISTRATION = {"username": "neha", "email": "neha@example.com", "password1": PASSWORD, "password2": PASSWORD}


def verification_path(email):
    return re.search(r"http://testserver(/users/email-verification/\S+)", email.body).group(1)


def test_register_creates_inactive_user_and_sends_verification_email(client, db, mailoutbox):
    response = client.post(reverse("register"), REGISTRATION)

    assert response.url == reverse("email-verification-sent")
    user = User.objects.get(username="neha")
    assert user.is_active is False
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == ["neha@example.com"]


def test_verification_link_activates_account_only_once(client, db, mailoutbox):
    client.post(reverse("register"), REGISTRATION)
    link = verification_path(mailoutbox[0])

    assert client.get(link).url == reverse("email-verification-success")
    assert User.objects.get(username="neha").is_active is True
    assert client.get(link).url == reverse("email-verification-failed")


def test_invalid_verification_link_fails_gracefully(client, db):
    response = client.get(reverse("email-verification", args=["bm90LWEtdXNlcg", "bad-token"]))
    assert response.url == reverse("email-verification-failed")


def test_register_requires_unique_email(client, user):
    response = client.post(reverse("register"), {**REGISTRATION, "email": "ASHA@example.com"})
    assert response.status_code == 200
    assert "already exists" in response.text


def test_register_requires_email(client, db):
    response = client.post(reverse("register"), {**REGISTRATION, "email": ""})
    assert response.status_code == 200
    assert not User.objects.filter(username="neha").exists()


def test_login_redirects_to_next_page(client, user):
    response = client.post(reverse("login") + "?next=/orders/my-orders", {"username": "asha", "password": PASSWORD})
    assert response.url == "/orders/my-orders"


def test_login_ignores_external_next_url(client, user):
    response = client.post(reverse("login"), {"username": "asha", "password": PASSWORD, "next": "https://evil.example.com/"})
    assert response.url == reverse("index")


def test_unverified_user_cannot_log_in(client, user):
    user.is_active = False
    user.save()
    response = client.post(reverse("login"), {"username": "asha", "password": PASSWORD})
    assert response.status_code == 200
    assert "_auth_user_id" not in client.session


def test_logout(logged_in_client):
    response = logged_in_client.get(reverse("logout"))
    assert response.url == reverse("index")
    assert "_auth_user_id" not in logged_in_client.session


def test_profile_requires_login(client, db):
    response = client.get(reverse("profile"))
    assert response.url == f"{reverse('login')}?next={reverse('profile')}"


def test_profile_update(logged_in_client, user):
    logged_in_client.post(reverse("profile"), {"username": "asha", "email": "asha.new@example.com"})
    user.refresh_from_db()
    assert user.email == "asha.new@example.com"


def test_password_reset_sends_email(client, user, mailoutbox):
    response = client.post(reverse("password_reset"), {"email": "asha@example.com"})
    assert response.url == reverse("password_reset_done")
    assert len(mailoutbox) == 1


def test_account_pages_render(client, db):
    for name in ["register", "login", "password_reset", "email-verification-sent",
                 "email-verification-success", "email-verification-failed", "password_reset_done",
                 "password_reset_complete"]:
        assert client.get(reverse(name)).status_code == 200, name
