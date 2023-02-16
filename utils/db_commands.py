import datetime as date_time
import time
from datetime import datetime

from sqlalchemy import func, select, update, delete
from sqlalchemy.exc import IntegrityError

from utils.database import get_session
from utils.schemas import User, LogFilter, VTPresets, UserLastSearch, VTLastSearches, ViewedPosts, JGLastSearches, \
    JGPresets, Payments, Subs, WLLastSearches, WLPresets, RefTeams


# User
async def register_user(user_id: int, full_name: str, ref_id: int, team_id: int):
    user = User(
        user_id=user_id,
        full_name=full_name,
        ref_id=ref_id,
        team_id=team_id
    )
    async with get_session() as session:
        session.add(user)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()


async def delete_user(user_id: int):
    async with get_session() as session:
        await session.execute(delete(User).where(User.user_id == user_id))
        await session.commit()


async def select_user(user_id: int):
    async with get_session() as session:
        user = await session.execute(select(User).where(User.user_id == user_id))
        return user.scalar()


async def update_user_is_agreed(user_id: int):
    user = update(User).where(User.user_id == user_id).values(is_agreed=True)
    async with get_session() as session:
        await session.execute(user)
        await session.commit()


async def change_user_banned(user_id: int, banned: bool):
    user = update(User).where(User.user_id == user_id).values(is_banned=banned)
    async with get_session() as session:
        await session.execute(user)
        await session.commit()


async def select_count_users():
    async with get_session() as session:
        users = await session.execute(select(func.count(User.id)))
        return users.scalar()


async def select_count_users_per_date(days: int):
    async with get_session() as session:
        users = await session.execute(
            select(func.count(User.id)).where(
                User.date > datetime.now() - date_time.timedelta(days=days)
            )
        )
        return users.scalar()


async def select_count_ref_users(ref_id: int):
    async with get_session() as session:
        count_refs = await session.execute(
            select(func.count(User.id)).where(
                User.ref_id == ref_id
            )
        )
        return count_refs.scalar()


async def check_args(args: str, user_id: int):
    user = await select_user(user_id)
    if args.startswith('team'):
        team_id = args.split('team')[1]
        if team_id != '' and await select_team(int(team_id)) and not user:
            return {'ref': 0, 'team': int(args.split('team')[1])}
        else:
            return {'ref': 0, 'team': 0}

    elif args == '':
        return {'ref': 0, 'team': 0}

    elif not args.isnumeric():
        return {'ref': 0, 'team': 0}

    elif not await select_user(int(args)):
        return {'ref': 0, 'team': 0}

    elif user:
        return {'ref': 0, 'team': 0}

    else:
        return {'ref': int(args), 'team': 0}


# Teams
async def add_new_team(team_name: str):
    team = RefTeams(
        team_name=team_name
    )
    async with get_session() as session:
        session.add(team)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()


async def select_team(team_id: int):
    async with get_session() as session:
        team = await session.execute(
            select(RefTeams).where(RefTeams.id == team_id)
        )
        return team.scalar()


async def delete_team(team_id: int):
    async with get_session() as session:
        await session.execute(
            delete(RefTeams).where(
                RefTeams.id == team_id
            )
        )
        await session.commit()


async def select_count_ref_team_users(team_id: int):
    async with get_session() as session:
        users = await session.execute(
            select(func.count(User.id)).where(User.team_id == team_id)
        )
        return users.scalar()


async def select_count_ref_team_users_per_date(team_id: int, days: int):
    async with get_session() as session:
        users = await session.execute(
            select(func.count(User.id)).where(
                User.team_id == team_id
            ).where(
                User.date > datetime.now() - date_time.timedelta(days=days)
            )
        )
        return users.scalar()


async def select_all_teams():
    async with get_session() as session:
        teams = await session.execute(select(RefTeams))
        return teams.scalars().all()


# Log Filter
async def add_log_filter(user_id: int):
    filter = LogFilter(
        user_id=user_id
    )
    async with get_session() as session:
        session.add(filter)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()


async def select_log_filter(user_id: int):
    async with get_session() as session:
        filter = await session.execute(select(LogFilter).where(LogFilter.user_id == user_id))
        return filter.scalar()


async def update_log_filter(user_id: int, status: bool, param):
    async with get_session() as session:
        filter = update(LogFilter).where(LogFilter.user_id == user_id).values({param: status})
        await session.execute(filter)
        await session.commit()


async def update_posts_filter(user_id: int, count_posts: int):
    async with get_session() as session:
        filter = update(LogFilter).where(LogFilter.user_id == user_id).values({LogFilter.posts_filter: count_posts})
        await session.execute(filter)
        await session.commit()


# Viewed Post
async def add_viewed_post(user_id: int, post_id: str):
    post = ViewedPosts(
        user_id=user_id,
        post_id=post_id
    )
    async with get_session() as session:
        session.add(post)

        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()


async def select_viewed_post(user_id: int, post_id: str):
    async with get_session() as session:
        post = await session.execute(select(ViewedPosts).where(ViewedPosts.user_id == user_id).where(
            ViewedPosts.post_id == post_id)
        )
        return post.scalar()


async def select_count_views(post_id: str):
    async with get_session() as session:
        post = await session.execute(select(func.count(ViewedPosts.post_id)).where(ViewedPosts.post_id == post_id))
        return post.scalar()


# User Access
async def update_user_access(user_id: int, status: bool):
    async with get_session() as session:
        user = update(User).where(User.user_id == user_id).values({User.sub: status})
        await session.execute(user)
        await session.commit()


async def select_users():
    async with get_session() as session:
        users = await session.execute(select(User))
        return users.scalars().all()


# Vinted Last Search
async def add_vt_last_search(
        user_id: int,
        domain: str,
        url: str,
        search_text: str,
        parse_date: float,
        parse_date_str: str,
        count_posts: int,
        count_reviews: int,
        from_price: int,
        to_price: int,
        parse_registration: datetime,
        parse_registration_str: str,
        from_page: int,
        to_page: int,
        auto_change_domain: str
):
    vt_presets = VTLastSearches(
        user_id=user_id,
        domain=domain,
        url=url,
        search_text=search_text,
        parse_date=parse_date,
        parse_date_str=parse_date_str,
        count_posts=count_posts,
        count_reviews=count_reviews,
        from_price=from_price,
        parse_registration=parse_registration,
        parse_registration_str=parse_registration_str,
        to_price=to_price,
        from_page=from_page,
        to_page=to_page,
        auto_change_domain=auto_change_domain
    )
    async with get_session() as session:
        session.add(vt_presets)

        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()


async def select_vt_last_search(user_id: int) -> VTLastSearches:
    async with get_session() as session:
        vt_preset = await session.execute(select(VTLastSearches).where(
            VTLastSearches.user_id == user_id).order_by(
            VTLastSearches.id.desc())
        )
        return vt_preset.scalar()


async def add_last_search(user_id: int, search_class: str):
    search = UserLastSearch(
        user_id=user_id,
        search_class=search_class
    )
    async with get_session() as session:
        session.add(search)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()


async def select_last_search(user_id: int):
    async with get_session() as session:
        search = await session.execute(select(UserLastSearch).where(
            UserLastSearch.user_id == user_id).order_by(
            UserLastSearch.id.desc())
        )
        return search.scalar()


async def auto_update_vt_last_search_date(user_id: int):
    date_today = datetime.today().date()
    date = update(VTLastSearches).where(VTLastSearches.user_id == user_id).values(
        {
            VTLastSearches.parse_date: time.mktime(date_today.timetuple()),
            VTLastSearches.parse_date_str: date_today.strftime('%Y-%m-%d')
        }
    )
    async with get_session() as session:
        await session.execute(date)
        await session.commit()


# Wallapop Last Search
async def add_wl_last_search(
        user_id: int,
        url: str,
        search_text: str,
        parse_date: float,
        parse_date_str: str,
        count_posts: int,
        count_reviews: int,
        count_sells: int,
        post_views: int,
        from_price: int,
        to_price: int,
        wl_category_id: int,
        wl_category_all: bool,
        wl_domain: str
):
    wl_presets = WLLastSearches(
        user_id=user_id,
        url=url,
        search_text=search_text,
        parse_date=parse_date,
        parse_date_str=parse_date_str,
        count_posts=count_posts,
        count_reviews=count_reviews,
        count_sells=count_sells,
        post_views=post_views,
        from_price=from_price,
        to_price=to_price,
        wl_category_id=wl_category_id,
        wl_category_all=wl_category_all,
        wl_domain=wl_domain
    )
    async with get_session() as session:
        session.add(wl_presets)

        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()


async def select_wl_last_search(user_id: int):
    async with get_session() as session:
        wl_preset = await session.execute(select(WLLastSearches).where(WLLastSearches.user_id == user_id).order_by(
            WLLastSearches.id.desc())
        )
        return wl_preset.scalar()


async def auto_update_wl_last_search_date(user_id: int):
    date_today = datetime.today().date()
    date = update(WLLastSearches).where(WLLastSearches.user_id == user_id).values(
        {
            WLLastSearches.parse_date: time.mktime(date_today.timetuple()),
            WLPresets.parse_date_str: date_today.strftime('%Y-%m-%d')
        }
    )
    async with get_session() as session:
        await session.execute(date)
        await session.commit()


# Jofogas Last Search
async def add_jg_last_search(
        user_id: int,
        url: str,
        category: str,
        search_text: str,
        parse_date: float,
        parse_date_str: str,
        count_reviews: int,
        from_price: int,
        to_price: int,
        from_page: int,
        to_page: int
):
    jg_presets = JGLastSearches(
        user_id=user_id,
        category=category,
        url=url,
        search_text=search_text,
        parse_date=parse_date,
        parse_date_str=parse_date_str,
        count_reviews=count_reviews,
        from_price=from_price,
        to_price=to_price,
        from_page=from_page,
        to_page=to_page
    )
    async with get_session() as session:
        session.add(jg_presets)

        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()


async def select_jg_last_search(user_id: int):
    async with get_session() as session:
        jg_preset = await session.execute(select(JGLastSearches).where(JGLastSearches.user_id == user_id).order_by(
            JGLastSearches.id.desc())
        )
        return jg_preset.scalar()


async def auto_update_jg_last_search_date(user_id: int):
    date_today = datetime.today().date()
    date = update(JGLastSearches).where(JGLastSearches.user_id == user_id).values(
        {
            JGLastSearches.parse_date: time.mktime(date_today.timetuple()),
            JGLastSearches.parse_date_str: date_today.strftime('%Y-%m-%d')
        }
    )
    async with get_session() as session:
        await session.execute(date)
        await session.commit()


# VT Presets
async def add_vt_preset(
        user_id: int,
        preset_name: str,
        domain: str,
        url: str,
        search_text: str,
        parse_date: float,
        parse_date_str: str,
        count_posts: int,
        count_reviews: int,
        from_price: int,
        to_price: int,
        parse_registration: datetime,
        parse_registration_str: str,
        from_page: int,
        to_page: int,
        auto_change_domain: str
):
    vt_presets = VTPresets(
        user_id=user_id,
        preset_name=preset_name,
        domain=domain,
        url=url,
        search_text=search_text,
        parse_date=parse_date,
        parse_date_str=parse_date_str,
        count_posts=count_posts,
        count_reviews=count_reviews,
        from_price=from_price,
        to_price=to_price,
        parse_registration=parse_registration,
        parse_registration_str=parse_registration_str,
        from_page=from_page,
        to_page=to_page,
        auto_change_domain=auto_change_domain
    )
    async with get_session() as session:
        session.add(vt_presets)

        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()


async def update_vt_preset_registration(
        user_id: int,
        preset_id: int,
        registration_date: datetime,
        registration_date_str: str
):
    date = update(VTPresets).where(
        VTPresets.user_id == user_id).where(
        VTPresets.id == preset_id).values(
        {
            VTPresets.parse_registration: registration_date,
            VTPresets.parse_registration_str: registration_date_str
        }
    )
    async with get_session() as session:
        await session.execute(date)
        await session.commit()


async def update_vt_preset_date(user_id: int, preset_id: int, parse_date: float, parse_date_str: str):
    date = update(VTPresets).where(
        VTPresets.user_id == user_id).where(
        VTPresets.id == preset_id).values(
        {
            VTPresets.parse_date: parse_date,
            VTPresets.parse_date_str: parse_date_str
        }
    )
    async with get_session() as session:
        await session.execute(date)
        await session.commit()


async def select_vt_preset_by_id(preset_id: int) -> VTPresets:
    async with get_session() as session:
        vt_preset = await session.execute(select(VTPresets).where(VTPresets.id == preset_id))
        return vt_preset.scalar()


async def delete_vt_preset(preset_id: int):
    vt_preset = delete(VTPresets).where(VTPresets.id == preset_id)
    async with get_session() as session:
        await session.execute(vt_preset)
        await session.commit()
        await session.commit()


async def select_vt_presets(user_id: int):
    async with get_session() as session:
        vt_presets = await session.execute(select(VTPresets).where(VTPresets.user_id == user_id))
        return vt_presets.scalars().all()


async def select_count_vt_presets(user_id: int):
    async with get_session() as session:
        vt_presets = await session.execute(select(func.count(VTPresets.user_id)).where(VTPresets.user_id == user_id))
        return vt_presets.scalar()


# Wallapop Presets
async def add_wl_preset(
        user_id: int,
        preset_name: str,
        url: str,
        search_text: str,
        parse_date: float,
        parse_date_str: str,
        count_posts: int,
        count_reviews: int,
        count_sells: int,
        post_views: int,
        from_price: int,
        to_price: int,
        wl_category_id: int,
        wl_category_all: bool,
        wl_domain: str
):
    wl_presets = WLPresets(
        user_id=user_id,
        preset_name=preset_name,
        url=url,
        search_text=search_text,
        parse_date=parse_date,
        parse_date_str=parse_date_str,
        count_posts=count_posts,
        count_reviews=count_reviews,
        count_sells=count_sells,
        post_views=post_views,
        from_price=from_price,
        to_price=to_price,
        wl_category_id=wl_category_id,
        wl_category_all=wl_category_all,
        wl_domain=wl_domain
    )
    async with get_session() as session:
        session.add(wl_presets)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()


async def update_wl_preset_date(user_id: int, preset_id: int, parse_date: float, parse_date_str: str):
    date = update(WLPresets).where(
        WLPresets.user_id == user_id).where(
        WLPresets.id == preset_id).values(
        {
            WLPresets.parse_date: parse_date,
            WLPresets.parse_date_str: parse_date_str
        }
    )
    async with get_session() as session:
        await session.execute(date)
        await session.commit()


async def select_wl_preset_by_id(preset_id: int):
    async with get_session() as session:
        wl_preset = await session.execute(select(WLPresets).where(WLPresets.id == preset_id))
        return wl_preset.scalar()


async def delete_wl_preset(preset_id: int):
    wl_preset = delete(WLPresets).where(WLPresets.id == preset_id)
    async with get_session() as session:
        await session.execute(wl_preset)
        await session.commit()


async def select_wl_presets(user_id: int):
    async with get_session() as session:
        wl_presets = await session.execute(select(WLPresets).where(WLPresets.user_id == user_id))
        return wl_presets.scalars().all()


async def select_count_wl_presets(user_id: int):
    async with get_session() as session:
        wl_presets = await session.execute(select(func.count(WLPresets.user_id)).where(
            WLPresets.user_id == user_id)
        )
        return wl_presets.scalar()


# JG Presets
async def add_jg_preset(
        user_id: int,
        preset_name: str,
        category: str,
        url: str,
        search_text: str,
        parse_date: float,
        parse_date_str: str,
        count_reviews: int,
        from_price: int,
        to_price: int,
        from_page: int,
        to_page: int
):
    vt_presets = JGPresets(
        user_id=user_id,
        preset_name=preset_name,
        category=category,
        url=url,
        search_text=search_text,
        parse_date=parse_date,
        parse_date_str=parse_date_str,
        count_reviews=count_reviews,
        from_price=from_price,
        to_price=to_price,
        from_page=from_page,
        to_page=to_page
    )
    async with get_session() as session:
        session.add(vt_presets)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()


async def select_jg_preset_by_id(preset_id: int):
    async with get_session() as session:
        jg_preset = await session.execute(select(JGPresets).where(JGPresets.id == preset_id))
        return jg_preset.scalar()


async def delete_jg_preset(preset_id: int):
    jg_preset = delete(JGPresets).where(JGPresets.id == preset_id)
    async with get_session() as session:
        await session.execute(jg_preset)
        await session.commit()


async def select_jg_presets(user_id: int):
    async with get_session() as session:
        jg_presets = await session.execute(select(JGPresets).where(JGPresets.user_id == user_id))
        return jg_presets.scalars().all()


async def select_count_jg_presets(user_id: int):
    async with get_session() as session:
        jg_presets = await session.execute(select(func.count(JGPresets.user_id)).where(JGPresets.user_id == user_id))
        return jg_presets.scalar()


async def auto_update_jg_preset_date(user_id: int, preset_id: int):
    date_today = datetime.today().date()
    date = update(JGPresets).where(
        JGPresets.user_id == user_id).where(
        JGPresets.id == preset_id).values(
        {
            JGPresets.parse_date: time.mktime(date_today.timetuple()),
            JGPresets.parse_date_str: date_today.strftime('%Y-%m-%d')
        }
    )
    async with get_session() as session:
        await session.execute(date)
        await session.commit()


# Balance
async def update_balance(user_id: int, balance: float):
    async with get_session() as session:
        user = update(User).where(User.user_id == user_id).values({User.balance: User.balance + balance})
        await session.execute(user)
        await session.commit()


# Subs
async def add_sub(user_id: int, time_sub: int, service: str, sub_hours: int, is_gift: bool = False):
    subs = Subs(
        user_id=user_id,
        sub_seconds=time_sub,
        service=service,
        sub_hours=sub_hours,
        is_gift=is_gift
    )
    async with get_session() as session:
        session.add(subs)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()


async def select_all_subs(user_id: int):
    sql = select(Subs).where(
        Subs.user_id == user_id
    ).where(
        Subs.sub_seconds - int(time.time()) > 0
    )
    async with get_session() as session:
        subs = await session.execute(sql)
        return subs.scalars().all()


async def select_sub_per_service(user_id: int, service: str):
    sql = select(Subs).where(
        Subs.user_id == user_id
    ).where(
        Subs.sub_seconds - int(time.time()) > 0
    ).where(
        Subs.service == service
    )
    async with get_session() as session:
        subs = await session.execute(sql)
        return subs.scalar()


async def select_count_subs_per_service_and_sub_hours(service: str, sub_hours: int):
    sql = select(func.count(Subs.id)).where(
        Subs.service == service
    ).where(
        Subs.sub_hours == sub_hours
    ).where(
        Subs.is_gift == False
    )
    async with get_session() as session:
        subs = await session.execute(sql)
        return subs.scalar()


async def select_count_users_with_subs():
    sql = select(Subs).where(Subs.sub_seconds - int(time.time()) > 0).where(
        Subs.is_gift == False
    )
    async with get_session() as session:
        subs = await session.execute(sql)
        return subs.scalars().all()


async def update_sub_hours(sub_id: int, sub_seconds: int, sub_hours: int):
    sql = update(Subs).where(Subs.id == sub_id).values(
        sub_seconds=Subs.sub_seconds + sub_seconds,
        sub_hours=Subs.sub_hours + sub_hours
    )
    async with get_session() as session:
        await session.execute(sql)
        await session.commit()


# Payments
async def add_new_payment(user_id: int, payment_id: str, summa: float, service: str):
    payment = Payments(
        user_id=user_id,
        payment_id=payment_id,
        summa=summa,
        service=service,
        status=False
    )
    async with get_session() as session:
        session.add(payment)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()


async def select_payment(payment_id: str):
    async with get_session() as session:
        payment = await session.execute(select(Payments).where(Payments.payment_id == payment_id))
        return payment.scalar()


async def select_sum_payments_per_service(service: str):
    async with get_session() as session:
        payments = await session.execute(
            select(Payments).where(
                Payments.service == service
            ).where(
                Payments.status == True
            ).where(
                Payments.date > datetime.now() - date_time.timedelta(days=31)
            )
        )
        return payments.scalars().all()


async def select_all_payments(user_id: int):
    async with get_session() as session:
        payment = await session.execute(select(Payments).where(Payments.user_id == user_id))
        return payment.scalars().all()


async def update_payment_status(payment_id: str):
    async with get_session() as session:
        payment = update(Payments).where(Payments.payment_id == payment_id).values(
            status=True
        )
        await session.execute(payment)
        await session.commit()
