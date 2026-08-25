from backend.hukom_bot.schema.mixin import PaginatableMixin, SearchableMixin


class QueryParams(SearchableMixin, PaginatableMixin):
    ...