import fire

from podcast.internal.user.user import User as UserInternal
from podcast.pkg.errors.biz_error import EmailNotSet, InvalidLoginUrl, InvalidEmail, ExpireToken, InvalidToken, EmailNotExist, NameNotSet
from podcast.pkg.type import check_email


def add(name: str, email: str):
    if email == "":
        raise EmailNotSet()

    if name == "":
        raise NameNotSet()

    
    if not check_email(email):
        raise InvalidEmail()

    user_internal = UserInternal(name=name, email=email)

    user = user_internal.get_user_by_email()
    if user is not None:
        print(f"user has existed, {user}")
        return user

    return user_internal.save()


if __name__ == "__main__":
    fire.Fire(add)