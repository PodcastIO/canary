import datetime
import io

from fastapi import APIRouter, UploadFile, File
from starlette.responses import StreamingResponse

from podcast.internal.resource.resource import Resource as InternalResource
from podcast.pkg.response import success

router = APIRouter(
    prefix="/api/web",
    tags=["resource"],
    responses={404: {"description": "Resources not found"}},
)


@router.post("/resource/{resource_type}")
async def add_resource(resource_type: str, file: UploadFile = File(...)):
    internal_resource = InternalResource(name=file.filename, file=file.file, type=resource_type)
    resource_dao = internal_resource.save()
    return success({
        "id": resource_dao.gid
    })
 

@router.get("/resource/${resource_id}")
async def get_resource(resource_id: str):
    resources = InternalResource.get_resources_by_gid_array([resource_id])
    resource = resources.get(resource_id)
    return StreamingResponse(io.BytesIO(resource.get("content")), media_type=resource.get("media_type"))

@router.get("/resource/${resource_id}/detail")
async def get_resource_detail(resource_id: str):
    resource = InternalResource.get_resource_detail(resource_id)
    return success(resource)