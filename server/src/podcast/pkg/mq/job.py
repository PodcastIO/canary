from datetime import datetime
from functools import wraps
from typing import List, Set

from rq.compat import string_types
from rq.decorators import job as rq_job
from rq import Worker, Queue, Retry

from podcast.dao.podcast import Frequency
from podcast.pkg.client.redis import redis_connection
from podcast.pkg.mq.scheduler import Scheduler
from podcast.pkg.ctx import Context
from podcast.pkg.errors.biz_error import RegisteredQueue, SchedulerFrequencyTypeInvalid


class QueuesManager:
    queues = {}

    @classmethod
    def add_queue(cls, queue_type: str, queue_name: str):
        queue_set = cls.queues.get(queue_type, set())
        if queue_name in queue_set:
            raise RegisteredQueue()

        queue_set.add(queue_name)
        cls.queues[queue_type] = queue_set

    @classmethod
    def get_other_queues(cls):
        return cls.queues.get("other", set())

    @classmethod
    def language_queue_exists(cls, language):
        return language in cls.queues.get("language", set())

    @classmethod
    def get_languages_can_tts(cls) -> Set:
        workers: List[Worker] = Worker.all(connection=redis_connection)
        languages = set()
        for worker in workers:
            if worker.name.startswith("lang_"):
                languages.add(worker.name.split("_")[1])
        return languages


class SchedulerJob:
    def __init__(self, queue_name, func, frequency: str, frequency_value: int, first_execute_time: int, **kwargs):
        self.queue_name = queue_name
        self.func = func
        self.frequency = frequency
        self.frequency_value = frequency_value
        self.first_execute_time = datetime.fromtimestamp(first_execute_time)
        self.kwargs = kwargs

        self.scheduler = Scheduler(connection=redis_connection)

    def _get_cron(self) -> str:
        day = self.first_execute_time.weekday
        hour = self.first_execute_time.hour
        minute = self.first_execute_time.minute
        weekday = self.first_execute_time.weekday()
        if self.frequency == Frequency.day:
            return f"{minute} {hour} */{self.frequency_value} * *"
        elif self.frequency == Frequency.week:
            return f"{minute} {hour} * * {weekday}/{self.frequency_value}"
        elif self.frequency == Frequency.month:
            return f"{minute} {hour} {day} */{self.frequency_value} *"
        raise SchedulerFrequencyTypeInvalid()

    def cancel(self, timer_id):
        if timer_id is not None:
            self.scheduler.cancel(timer_id)

    def set(self, timer_id=None) -> str:
        if timer_id is not None:
            self.scheduler.cancel(timer_id)

        cron_str = self._get_cron()
        job = self.scheduler.custom_cron(
            self.first_execute_time,
            cron_str,
            func=self.func,
            use_local_timezone=False,
            kwargs=self.kwargs,
            queue_name=self.func.__name__,
            meta={"context": Context.get_context()},
        )
        return job.id


class custom_rq_job(rq_job):
    def __init__(self, queue_name, timeout=10 * 600, depends_on=None):
        rq_job.__init__(self,
                        queue_name,
                        connection=redis_connection,
                        timeout=timeout,
                        depends_on=depends_on,
                        retry=Retry(max=3, interval=[10, 30, 60]),
                        )

    def __call__(self, f):
        @wraps(f)
        def wrap_f(*args, **kwargs):
            return f(*args, **kwargs)

        @wraps(f)
        def delay(*args, **kwargs):
            if isinstance(self.queue, string_types):
                queue = self.queue_class(name=self.queue,
                                         connection=self.connection)
            else:
                queue = self.queue

            depends_on = kwargs.pop('depends_on', None)
            job_id = kwargs.pop('job_id', None)
            at_front = kwargs.pop('at_front', False)

            if not depends_on:
                depends_on = self.depends_on

            if not at_front:
                at_front = self.at_front

            self.meta = {
                "context": Context.get_context()
            }

            return queue.enqueue_call(wrap_f, args=args, kwargs=kwargs,
                                      timeout=self.timeout, result_ttl=self.result_ttl,
                                      ttl=self.ttl, depends_on=depends_on, job_id=job_id, at_front=at_front,
                                      meta=self.meta, description=self.description, failure_ttl=self.failure_ttl,
                                      retry=self.retry)

        wrap_f.delay = delay
        return wrap_f


class other(custom_rq_job):
    def __init__(self, queue_name, timeout=10 * 600, depends_on=None):
        QueuesManager.add_queue("other", queue_name)

        custom_rq_job.__init__(self, queue_name, timeout=timeout, depends_on=depends_on)


class lang_rq_job(custom_rq_job):
    def __init__(self, language, timeout=10 * 600, depends_on=None):
        QueuesManager.add_queue("language", language)

        queue_name = f"lang_{language}"
        custom_rq_job.__init__(self, queue_name, timeout=timeout, depends_on=depends_on)


class zh(lang_rq_job):
    def __init__(self, timeout=10 * 600, depends_on=None):
        custom_rq_job.__init__(self, "zh", timeout=timeout, depends_on=depends_on)


class en(lang_rq_job):
    def __init__(self, timeout=10 * 600, depends_on=None):
        custom_rq_job.__init__(self, "en", timeout=timeout, depends_on=depends_on)


class ja(lang_rq_job):
    def __init__(self, timeout=10 * 600, depends_on=None):
        custom_rq_job.__init__(self, "ja", timeout=timeout, depends_on=depends_on)


class de(lang_rq_job):
    def __init__(self, timeout=10 * 600, depends_on=None):
        custom_rq_job.__init__(self, "de", timeout=timeout, depends_on=depends_on)


class nl(lang_rq_job):
    def __init__(self, timeout=10 * 600, depends_on=None):
        custom_rq_job.__init__(self, "nl", timeout=timeout, depends_on=depends_on)


class fr(lang_rq_job):
    def __init__(self, timeout=10 * 600, depends_on=None):
        custom_rq_job.__init__(self, "fr", timeout=timeout, depends_on=depends_on)


class es(lang_rq_job):
    def __init__(self, timeout=10 * 600, depends_on=None):
        custom_rq_job.__init__(self, "es", timeout=timeout, depends_on=depends_on)


class uk(lang_rq_job):
    def __init__(self, timeout=10 * 600, depends_on=None):
        custom_rq_job.__init__(self, "uk", timeout=timeout, depends_on=depends_on)
