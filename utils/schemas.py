from datetime import datetime

from sqlalchemy import Column, Integer, Boolean, String, Float, BIGINT, DateTime

from utils.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(BIGINT, unique=True)
    full_name = Column(String)
    balance = Column(Float, default=0.0)
    is_banned = Column(Boolean, default=False)
    is_agreed = Column(Boolean, default=False)
    ref_id = Column(BIGINT)
    team_id = Column(BIGINT)
    date = Column(DateTime, default=datetime.now())


class Subs(Base):
    __tablename__ = 'subs'

    id = Column(Integer, primary_key=True)
    user_id = Column(BIGINT)
    service = Column(String)
    sub_seconds = Column(BIGINT)
    sub_hours = Column(BIGINT)
    is_gift = Column(Boolean)


class RefTeams(Base):
    __tablename__ = 'ref_teams'

    id = Column(Integer, primary_key=True)
    team_name = Column(String)


class LogFilter(Base):
    __tablename__ = 'log_filter'

    id = Column(Integer, primary_key=True)
    user_id = Column(BIGINT, unique=True)
    photo = Column(Boolean, default=True)
    name = Column(Boolean, default=True)
    price = Column(Boolean, default=True)
    location = Column(Boolean, default=True)
    title = Column(Boolean, default=True)
    post_date = Column(Boolean, default=True)
    count_posts = Column(Boolean, default=True)
    viewed_posts = Column(Boolean, default=False)
    posts_filter = Column(BIGINT, default=50)


class ViewedPosts(Base):
    __tablename__ = 'viewed_posts'

    id = Column(Integer, primary_key=True)
    user_id = Column(BIGINT)
    post_id = Column(String)


class UserLastSearch(Base):
    __tablename__ = 'last_searches'

    id = Column(Integer, primary_key=True)
    user_id = Column(BIGINT)
    search_class = Column(String)


class VTLastSearches(Base):
    __tablename__ = 'vt_last_searches'

    id = Column(Integer, primary_key=True)
    user_id = Column(BIGINT)
    domain = Column(String)
    url = Column(String)
    search_text = Column(String)
    parse_date = Column(Float)
    parse_date_str = Column(String)
    count_posts = Column(BIGINT)
    count_reviews = Column(BIGINT)
    from_price = Column(BIGINT)
    to_price = Column(BIGINT)
    parse_registration = Column(DateTime)
    parse_registration_str = Column(String)
    from_page = Column(BIGINT)
    to_page = Column(BIGINT)
    auto_change_domain = Column(String)


class VTPresets(Base):
    __tablename__ = 'vt_presets'

    id = Column(Integer, primary_key=True)
    user_id = Column(BIGINT)
    preset_name = Column(String)
    domain = Column(String)
    url = Column(String)
    search_text = Column(String)
    parse_date = Column(Float)
    parse_date_str = Column(String)
    count_posts = Column(BIGINT)
    count_reviews = Column(BIGINT)
    from_price = Column(BIGINT)
    to_price = Column(BIGINT)
    parse_registration = Column(DateTime)
    parse_registration_str = Column(String)
    from_page = Column(BIGINT)
    to_page = Column(BIGINT)
    auto_change_domain = Column(String)


class WLLastSearches(Base):
    __tablename__ = 'wl_last_searches'

    id = Column(Integer, primary_key=True)
    user_id = Column(BIGINT)
    url = Column(String)
    search_text = Column(String)
    parse_date = Column(Float)
    parse_date_str = Column(String)
    count_posts = Column(BIGINT)
    count_reviews = Column(BIGINT)
    count_sells = Column(BIGINT)
    post_views = Column(BIGINT)
    from_price = Column(BIGINT)
    to_price = Column(BIGINT)
    wl_category_id = Column(String)
    wl_category_all = Column(Boolean)
    wl_domain = Column(String)


class WLPresets(Base):
    __tablename__ = 'wl_presets'

    id = Column(Integer, primary_key=True)
    user_id = Column(BIGINT)
    preset_name = Column(String)
    url = Column(String)
    search_text = Column(String)
    parse_date = Column(Float)
    parse_date_str = Column(String)
    count_posts = Column(BIGINT)
    count_reviews = Column(BIGINT)
    count_sells = Column(BIGINT)
    post_views = Column(BIGINT)
    from_price = Column(BIGINT)
    to_price = Column(BIGINT)
    wl_category_id = Column(String)
    wl_category_all = Column(Boolean)
    wl_domain = Column(String)


class JGLastSearches(Base):
    __tablename__ = 'jg_last_searches'

    id = Column(Integer, primary_key=True)
    user_id = Column(BIGINT)
    url = Column(String)
    category = Column(String)
    search_text = Column(String)
    parse_date = Column(Float)
    parse_date_str = Column(String)
    count_reviews = Column(BIGINT)
    from_price = Column(BIGINT)
    to_price = Column(BIGINT)
    from_page = Column(BIGINT)
    to_page = Column(BIGINT)


class JGPresets(Base):
    __tablename__ = 'jg_presets'

    id = Column(Integer, primary_key=True)
    user_id = Column(BIGINT)
    preset_name = Column(String)
    category = Column(String)
    url = Column(String)
    search_text = Column(String)
    parse_date = Column(Float)
    parse_date_str = Column(String)
    count_reviews = Column(BIGINT)
    from_price = Column(BIGINT)
    to_price = Column(BIGINT)
    from_page = Column(BIGINT)
    to_page = Column(BIGINT)


class Payments(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    user_id = Column(BIGINT)
    payment_id = Column(String)
    summa = Column(Float)
    service = Column(String)
    date = Column(DateTime, default=datetime.now())
    status = Column(Boolean)
