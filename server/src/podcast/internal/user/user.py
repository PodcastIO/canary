from podcast.dao.user import User as UserDao


class User:
    def __init__(self, **kwargs):
        self.gid = kwargs.get("gid")
        self.name = kwargs.get("name")
        self.email = kwargs.get("email")

    def get_user_by_email(self):
        return UserDao(email=self.email).get_user_by_email()

    def get_user_by_gid(self) -> UserDao:
        return UserDao(gid=self.gid).get_user_by_gid()

    def save(self) -> UserDao:
        return UserDao(email=self.email, name=self.name).save()

    def get_user_total(self) -> int:
        return UserDao().get_user_total()