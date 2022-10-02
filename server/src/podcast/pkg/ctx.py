from rq import get_current_job
from starlette_context import context


class Context:
    @classmethod
    def get_context(cls):
        if context.exists():
            return context.data

        job = get_current_job()
        if job is not None:
            return job.meta.get('context') or {}
        return {}

    @classmethod
    def get_user_id(cls):
        return cls.get_context().get("user_id", "")

    @classmethod
    def get_request_id(cls):
        return cls.get_context().get("request_id", "")

    @classmethod
    def get_session(cls):
        return cls.get_context().get("session")
