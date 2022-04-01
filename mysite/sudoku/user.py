import datetime

from .models import SudokuBlogUser, SudokuBlogUserSession
from django.contrib.auth.hashers import PBKDF2PasswordHasher, check_password, get_random_string
from django.utils import timezone

MY_AUTH_COOKIE = 'my_sessionid'

def create_sudoku_user(loginname, password, firstname, lastname):
    res = {}
    if len(SudokuBlogUser.objects.filter(loginname=loginname)) > 0:
        res['success'] = False
        res['error'] = 'User with login name %s already exists' % loginname
    else:
        hasher = PBKDF2PasswordHasher()
        salt = hasher.salt()
        password_hash = hasher.encode(password, salt)
        user = SudokuBlogUser(
            loginname=loginname,
            firstname = firstname,
            lastname = lastname,
            is_registered_user = True,
            password_hash = password_hash
        )
        user.save()
        res['success'] = True

    return res

def check_user_password(loginname, password):
    res = {}
    users_with_loginname = SudokuBlogUser.objects.filter(loginname=loginname)
    if len(users_with_loginname) == 0:
        res['success'] = False
        res['error'] = 'User with login name %s does not exist' % loginname
    else:
        user = users_with_loginname[0]
        if user.is_registered_user:
            if check_password(password, user.password_hash):
                res['success'] = True
            else:
                res['success'] = False
                res['error'] = 'Password for user %s does not match' % loginname
        else:
            res['success'] = False
            res['error'] = '%s is an anonymous user' % loginname

    return res

def get_anonymous_user():
    return SudokuBlogUser.objects.get(loginname="anonymous")

def get_user_by_loginname(loginname):
    user = SudokuBlogUser.objects.get(loginname=loginname)
    return user


def get_logged_in_session(request):
    session_id = request.COOKIES.get(MY_AUTH_COOKIE)
    if session_id is None:
        return None

    sessions = SudokuBlogUserSession.objects.filter(session_id=session_id)
    if len(sessions) != 1:
        return None

    session = sessions[0]

    if session.expires_at <= timezone.now():
        session.delete()
        return None

    return session


def get_logged_in_user(request):
    session = get_logged_in_session(request)
    if session is None:
        return None

    return session.sudoku_user

def new_session(user):
    session_id = get_random_string(80)
    expires_at = timezone.now() + datetime.timedelta(days=1)
    session = SudokuBlogUserSession(
                sudoku_user=user,
                session_id = session_id,
                expires_at = expires_at
                )
    session.save()
    return session