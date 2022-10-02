import datetime
import logging
import time
import uuid
from typing import Optional

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from podcast.config.template import Templates
from podcast.pkg.errors.biz_error import EmailNotSet, InvalidLoginUrl, InvalidEmail, ExpireToken, InvalidToken, EmailNotExist
from podcast.pkg.cipher.jwt import Jwt
from podcast.pkg.email import EmailClient
from podcast.internal.user.user import User as UserInternal
from podcast.dao.user import User as UserDao
from podcast.pkg.response import success
from podcast.pkg.type import check_email
from podcast.pkg.client.redis import get_login_token, set_confirm_login_token, set_login_token, get_confirm_login_token, del_confirm_login_token
from starlette_context import context

from podcast.pkg.client.redis import delete_login_token


router = APIRouter(
    prefix="/api/web",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)


class LoginForm(BaseModel):
    email: str
    is_remember: Optional[bool] = Field(alias='isRemember', default=False)


@router.post("/user/login")
async def login(login_form: LoginForm, request: Request):
    if login_form.email == "":
        raise EmailNotSet()

    if not check_email(login_form.email):
        raise InvalidEmail()

    user = UserInternal(email=login_form.email, name="admin")
    total = user.get_user_total()
    if total <= 0:
        user_dao = user.save()
    else:
        user_dao: UserDao = user.get_user_by_email()
        if user_dao is None:
            raise EmailNotExist()

    token: str = uuid.uuid4()
    set_confirm_login_token(token, user_dao.gid)

    # send email
    login_url: str = "{0}/user/confirmLogin?token={1}&user_id={2}&is_remember={3}".format(context.data.get("base_url"),
                                                                                          token,
                                                                                          user_dao.gid,
                                                                                          login_form.is_remember)
    logging.warning("login confirm url: %s", login_url)
    set_confirm_login_token(token, user_dao.gid)
    login_email_content = Templates.get_login_tpl(user_dao.name, login_url)
    # with EmailClient() as client:
    #     client.send([login_form.email], "Login canary", login_email_content)
    return success()


@router.get("/user/confirm_login")
async def confirm_login(token: str, user_id: str, is_remember: bool):
    user_id_from_redis = get_confirm_login_token(token)
    if user_id_from_redis is None:
        raise InvalidLoginUrl()

    if str(user_id_from_redis, 'UTF-8') != user_id:
        raise InvalidLoginUrl()

    del_confirm_login_token(token)

    user: UserDao = UserInternal(gid=user_id).get_user_by_gid()
    if user is None:
        raise InvalidLoginUrl()

    days: int = 1
    if is_remember:
        days = 7

    exp: int = days * 24 * 60 * 60
    token: str = Jwt(payload={
        "user_id": user_id,
        "exp_time": (datetime.datetime.now() + datetime.timedelta(days=days)).timestamp()
    }).encrypt_auth_token()


    set_login_token(user_id, token, is_remember)
    logging.warning("login confirm url: %s", context.data.get("base_url"))

    return success({
        'token': token,
    })


class CheckLoginForm(BaseModel):
    token: str


def token_is_valid(request: Request):
    token: str = request.headers.get("Authorization", "")[6:]
    if token is None or token == "":
            raise InvalidToken()
    data = Jwt(token=token).decrypt_auth_token()
    if data is None:
        raise InvalidLoginUrl()

    if time.time() > data["exp_time"]:
        raise ExpireToken()

    user_id = get_login_token(token)
    if user_id != data.get("user_id", ""):
        raise InvalidToken()

    return token, data["user_id"]


@router.post("/user/check_login")
async def check_login(request: Request):
    token_is_valid(request)
    return success()


@router.post("/user/logout")
async def logout(request: Request):
    token, _ = token_is_valid(request)
    delete_login_token(token)
    return success()


@router.get("/user")
async def get_user(request: Request):
    token, user_id = token_is_valid(request)
    user_dao: UserDao = UserInternal(gid=user_id).get_user_by_gid()
    return success(user_dao)