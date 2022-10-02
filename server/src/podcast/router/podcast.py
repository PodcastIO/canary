import datetime
import io
import json
import time
from typing import Optional
from podcast.pkg.utils.dict import model_to_dict

from starlette.responses import StreamingResponse, Response

from podcast.dao.podcast import PodcastSource, Frequency
from podcast.internal.podcast.podcast import Podcast as PodcastInternal
from podcast.internal.episode.episode import Episode as EpisodeInternal
from podcast.internal.resource.resource import Resource as ResourceInternal
from fastapi import APIRouter
from pydantic import BaseModel, Field

from podcast.job.podcast import parse_and_gen_podcast_job
from podcast.pkg.errors.biz_error import SourceNotRecognize, NotUploadPodcast, PodcastUrlNotSet, CategoryNotSet, \
    LanguageNotInvalid, SchedulerFrequencyTypeNotSet, SchedulerFirstExecuteTimeNotSet, SchedulerFrequencyTypeInvalid, \
    ShareDisabled, ShareExpired
from podcast.pkg.mq.job import SchedulerJob
from podcast.pkg.type import str_is_empty
from podcast.pkg.response import success
from podcast.job.gen_episode import gen_one_episode_job, gen_podcast_job
from podcast.job.parse_podcast import parse_podcast_job
from podcast.pkg.utils.dict import obj_to_dict
from podcast.internal.resource.resource import Resource as InternalResource


router = APIRouter(
    prefix="/api/web",
    tags=["podcast"],
    responses={404: {"description": "Not found"}},
)


class Podcast(BaseModel):
    source: str
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = Field(alias='url')
    cover_resource_id: Optional[str] = Field(alias='coverResourceId')
    book_resource_id: Optional[str] = Field(alias='bookResourceId')
    language: str
    frequency: Optional[str] = Field(alias='frequency')
    frequency_value: Optional[int] = Field(alias='frequencyValue')
    first_execute_time: Optional[int] = Field(alias='firstExecuteTime')
    share_enable: Optional[bool] = Field(alias="shareEnable")
    share_time: Optional[int] = Field(alias="shareTime")


@router.post("/podcast")
async def add_podcast(item: Podcast):
    if item.source not in [PodcastSource.local, PodcastSource.rss, PodcastSource.video]:
        raise SourceNotRecognize()

    if item.language not in ["zh", "en"]:
        raise LanguageNotInvalid()

    if item.source == PodcastSource.local:
        if str_is_empty(item.book_resource_id):
            raise NotUploadPodcast()

        gids = [item.book_resource_id]
        if not str_is_empty(item.cover_resource_id):
            gids.append(item.cover_resource_id)

        resources = ResourceInternal.get_resources_by_gid_array(gids)
        podcast = PodcastInternal(**item.__dict__).add_podcast(resources.get(item.book_resource_id).get("name"))

    elif item.source in [PodcastSource.rss, PodcastSource.video]:
        if str_is_empty(item.url):
            raise PodcastUrlNotSet()

        if str_is_empty(item.frequency):
            raise SchedulerFrequencyTypeNotSet()

        if str_is_empty(item.first_execute_time):
            raise SchedulerFirstExecuteTimeNotSet()

        if item.frequency not in [Frequency.day, Frequency.week, Frequency.month]:
            raise SchedulerFrequencyTypeInvalid()

        gids = []
        if not str_is_empty(item.cover_resource_id):
            gids.append(item.cover_resource_id)

        ResourceInternal.get_resources_by_gid_array(gids)
        podcast_internal = PodcastInternal(**item.__dict__)
        podcast = podcast_internal.add_podcast("")
        scheduler_job = SchedulerJob("other",
                                     parse_and_gen_podcast_job,
                                     podcast.frequency,
                                     podcast.frequency_value,
                                     podcast.first_execute_time,
                                     podcast_gid=podcast.gid)
        timer_id = scheduler_job.set(podcast.timer_id)
        podcast.update({"timer_id": timer_id})

    parse_podcast_task = parse_podcast_job.delay(podcast.gid)
    gen_podcast_job.delay(podcast.gid, depends_on=[parse_podcast_task])

    return success({
        "id": podcast.gid
    })

@router.delete("/podcast/${podcast_id}")
async def delete_podcast(podcast_id: str):
    podcast_internal = PodcastInternal(gid=podcast_id)
    podcast = podcast_internal.get_podcast()
    if podcast.source in [PodcastSource.rss, PodcastSource.video]:
        scheduler_job = SchedulerJob("other",
                                parse_and_gen_podcast_job,
                                podcast.frequency,
                                podcast.frequency_value,
                                podcast.first_execute_time,
                                podcast_gid=podcast.gid)
        scheduler_job.cancel(podcast.timer_id)
    podcast_internal.delete_podcast()
    return success()

@router.get("/podcast/{podcast_id}")
async def get_podcast(podcast_id: str):
    podcast_internal = PodcastInternal(gid=podcast_id)
    podcast = podcast_internal.get_podcast()
    return success(podcast)

@router.get("/podcast/${podcast_id}/episodes")
async def get_podcast_episodes(podcast_id: str, offset: int = 0, limit: int = 10):
    episode_internal = EpisodeInternal(podcast_gid=podcast_id)
    episodes = episode_internal.get_episodes_by_podcast_gid(offset, limit)
    episodes_total = episode_internal.get_episodes_total_by_podcast_gid()
    result = {
        "items": episodes,
        "total": episodes_total,
    }
    return success(result)

class UpdatePodcastItem(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    cover_resource_id: Optional[str] = Field(alias='coverResourceId')
    book_resource_id: Optional[str] = Field(alias='bookResourceId')
    frequency: Optional[str] = Field(alias='frequency')
    frequency_value: Optional[int] = Field(alias='frequencyValue')
    first_execute_time: Optional[int] = Field(alias='firstExecuteTime')
    share_enable: Optional[int] = Field(alias="shareEnable")
    share_time: Optional[int] = Field(alias="shareTime")


@router.put("/podcast/{podcast_id}")
async def update_podcast(podcast_id: str, item: UpdatePodcastItem):
    podcast_internal = PodcastInternal(gid=podcast_id)
    podcast = podcast_internal.get_podcast()

    params = obj_to_dict(item)
    if item.frequency is not None and item.first_execute_time is not None:
        if item.frequency not in [Frequency.day, Frequency.week, Frequency.month]:
            raise SchedulerFrequencyTypeInvalid()

        scheduler_job = SchedulerJob("other",
                                     parse_and_gen_podcast_job,
                                     item.frequency,
                                     item.frequency_value,
                                     item.first_execute_time,
                                     podcast_gid=podcast_id)
        timer_id = scheduler_job.set(podcast.timer_id)
        params.update({"timer_id": timer_id})
    podcast_internal.update_podcast_info(**params)
    return success()


@router.get("/episodes")
async def get_episodes(offset=0, limit=10):
    episodes, total = EpisodeInternal().get_episodes(offset, limit)
    podcasts = PodcastInternal().get_podcasts_by_gids([episode.podcast_gid for episode in episodes])
    return success({
        "episodes": episodes,
        "podcasts": podcasts,
        "total": total,
    })


class ShareSetting(BaseModel):
    enable_share: bool = Field(alias='enableShare')


@router.post("/podcast/share/{podcast_id}")
async def share_podcast(podcast_id: str, share_setting: ShareSetting):
    podcast_internal = PodcastInternal(gid=podcast_id)
    share_token = podcast_internal.share_podcast(share_setting.enable_share)
    return success({
        "id": podcast_id,
        "share_token": share_token,
    })


@router.get("/podcast/rss/{token}")
async def get_rss(token: str):
    data = PodcastInternal.check_rss_token(token)
    rss_content: io.BytesIO = PodcastInternal(gid=data.get("podcast_id")).gen_rss(token)
    return Response(rss_content.getvalue(), headers={
        "content-type": "application/xml"
    })


@router.get("/podcasts")
async def get_podcasts(offset: int = 0, limit: int = 10):
    podcasts = PodcastInternal.get_podcasts(offset, limit)
    total = PodcastInternal.get_podcasts_total()

    return success({
        "items": podcasts,
        "total": total,
    })


@router.post("/episode/{episode_id}/gen")
async def gen_podcast_episode(episode_id: str):
    episode = EpisodeInternal(gid=episode_id).get_episode()
    gen_one_episode_job.delay(episode.gid)
    return success(None)


@router.post("/podcast/{podcast_id}/gen")
async def gen_podcast(podcast_id: str):
    podcast = PodcastInternal(gid=podcast_id).get_podcast()
    parse_podcast_task = parse_podcast_job.delay(podcast.gid)
    gen_podcast_job.delay(podcast.gid, depends_on=[parse_podcast_task])
    return success(None)


@router.get("/podcast_resource/${token}")
async def get_rss_resource(token: str):
    data = PodcastInternal.check_rss_token(token)
    resource_id = data.get("resource_id")
    resources = InternalResource.get_resources_by_gid_array([resource_id])
    resource = resources.get(resource_id)
    return StreamingResponse(io.BytesIO(resource.get("content")), media_type=resource.get("media_type"))

