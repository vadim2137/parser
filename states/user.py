from aiogram.dispatcher.filters.state import StatesGroup, State


class Parser(StatesGroup):
    use_presets = State()
    preset_publication = State()
    preset_registration = State()
    domain = State()
    category = State()
    date = State()
    count_posts = State()
    count_reviews = State()
    price = State()
    use_registration = State()
    registration = State()
    from_page = State()
    to_page = State()
    auto_change_domain = State()
    preset = State()
    name = State()
    start_vt = State()


class WLParser(StatesGroup):
    domain = State()
    use_presets = State()
    preset_publication = State()
    category = State()
    date = State()
    count_posts = State()
    count_reviews = State()
    count_sells = State()
    post_views = State()
    price = State()
    preset = State()
    name = State()
    start_wl = State()


class JGParser(StatesGroup):
    use_presets = State()
    category = State()
    date = State()
    count_posts = State()
    count_reviews = State()
    price = State()
    from_page = State()
    to_page = State()
    preset = State()
    name = State()
    start_jg = State()


class PostsFilter(StatesGroup):
    filter = State()


class Mail(StatesGroup):
    mail = State()


class Banker(StatesGroup):
    cheque = State()


class CryproBot(StatesGroup):
    sum = State()
    currency = State()


class CreateTeam(StatesGroup):
    name = State()
