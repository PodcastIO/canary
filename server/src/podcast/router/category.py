from fastapi import APIRouter
from pydantic import BaseModel

from podcast.internal.category.category import Category as CategoryInternal
from podcast.pkg.response import success

router = APIRouter(
    prefix="/api/web",
    tags=["category"],
    responses={404: {"description": "Not found"}},
)


@router.get("/categories")
async def get_categories():
    categories = CategoryInternal().fetch_all()
    return success({
        "items": [{
            "id": category.gid,
            "name": category.name,
        } for category in categories]
    })


class Category(BaseModel):
    name: str


@router.post("/category")
async def add_category(category: Category):
    if category == "":
        raise Exception("category is empty")

    new_category = CategoryInternal(name=category.name).add()
    return success({
        "id": new_category.gid,
        "name": new_category.name,
    })


@router.get("/category/search")
async def search_categories(name: str = "", ratio: float = 50):
    return success({
        "items": CategoryInternal(name=name).fuzz_search(ratio)
    })
