from podcast.dao.category import Category as CategoryDao
from thefuzz import fuzz


class Category:
    def __init__(self, **kwargs):
        self.gid = kwargs.get("gid")
        self.name = kwargs.get("name")

    def get_category(self):
        category = CategoryDao(gid=self.gid).get_by_gid()
        if category is None:
            return None

        return category

    @classmethod
    def fetch_all(cls):
        categories = CategoryDao().get_all()
        if categories is None:
            return None

        return categories

    def add(self):
        return CategoryDao(name=self.name).save()

    def fuzz_search(self, ratio: float):
        if ratio > 100 or self.name == "":
            return []

        categories = self.fetch_all()
        categories_result = []
        for category in categories:
            result_radio = fuzz.ratio(self.name, category.name)
            if result_radio > ratio:
                categories_result.append({
                    "id": category.gid,
                    "name": category.name,
                    "ratio": result_radio,
                })

        categories_result.sort(key=lambda x: x["ratio"], reverse=True)

        return categories_result
