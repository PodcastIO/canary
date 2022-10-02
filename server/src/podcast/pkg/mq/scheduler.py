from rq_scheduler import Scheduler as RQScheduler
from rq_scheduler.utils import from_unix, to_unix, get_next_scheduled_time, rationalize_until


class Scheduler(RQScheduler):
    def __init__(self, queue_name='default', queue=None, interval=60, connection=None, job_class=None, queue_class=None, name=None):
        RQScheduler.__init__(self, queue_name, queue, interval, connection, job_class, queue_class, name)

    def custom_cron(self, scheduled_time, cron_string, func, args=None, kwargs=None, repeat=None,
             queue_name=None, id=None, timeout=None, description=None, meta=None, use_local_timezone=False, depends_on=None):
        # Set result_ttl to -1, as jobs scheduled via cron are periodic ones.
        # Otherwise the job would expire after 500 sec.
        job = self._create_job(func, args=args, kwargs=kwargs, commit=False,
                               result_ttl=-1, id=id, queue_name=queue_name,
                               description=description, timeout=timeout, meta=meta, depends_on=depends_on)

        job.meta['cron_string'] = cron_string
        job.meta['use_local_timezone'] = use_local_timezone

        if repeat is not None:
            job.meta['repeat'] = int(repeat)

        job.save()

        self.connection.zadd(self.scheduled_jobs_key,
                              {job.id: to_unix(scheduled_time)})
        return job

