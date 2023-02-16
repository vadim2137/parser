from filters.filter import IsBannedFilter


def register_filters(dp):
    dp.filters_factory.bind(IsBannedFilter)