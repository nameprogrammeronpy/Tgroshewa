from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard(is_admin: bool = False):
    """Главное меню (inline)"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🏢 Бизнес", callback_data="menu_business"),
        InlineKeyboardButton(text="🍽 Питание", callback_data="menu_food"),
        InlineKeyboardButton(text="💪 Здоровье", callback_data="menu_health")
    )
    builder.row(InlineKeyboardButton(text="🛍 Каталог товаров", callback_data="menu_catalog"))
    builder.row(InlineKeyboardButton(text="🔗 Важные ссылки", callback_data="menu_links"))
    if is_admin:
        builder.row(InlineKeyboardButton(text="⚙️ Админка", callback_data="menu_admin"))
    return builder.as_markup()


def catalog_keyboard():
    """Каталог товаров"""
    builder = InlineKeyboardBuilder()
    catalog_items = [
        ("🆕 Новинки", "https://www.nlstar.com/ref/g4A1jv/"),
        ("🛒 Весь магазин", "https://www.nlstar.com/ref/5n33hu/"),
        ("🧹 Уборка", "https://ng.nlstar.com/ru/api/referrals/ref/XdCCAZ/"),
        ("💊 БАДы и витамины", "https://www.nlstar.com/ref/Fz8gTr/"),
        ("💇 Шампуни и уход для волос", "https://www.nlstar.com/ref/aGfHXy/"),
        ("💆 Уход за лицом", "https://ng.nlstar.com/ru/api/referrals/ref/n17bKv/"),
        ("🧴 Для тела", "https://www.nlstar.com/ref/sUGDmV/"),
        ("🎁 Подарки", "https://www.nlstar.com/ref/BFCoLx/"),
        ("🥤 Коктейли", "https://www.nlstar.com/ref/4vJo4t/"),
        ("🌿 Адаптогены", "https://www.nlstar.com/ref/924P7c/"),
        ("🍬 Лакомства", "https://www.nlstar.com/ref/kg8VpL/"),
        ("🥛 Напитки", "https://www.nlstar.com/ref/cLbDQB/"),
        ("🦷 Зубные пасты", "https://www.nlstar.com/ref/tgiS58/"),
        ("💰 Выгодные наборы", "https://www.nlstar.com/ref/pfkZXF/"),
        ("👶 Для детей", "https://www.nlstar.com/ref/uPZHiC/"),
        ("👨 Для мужчин", "https://www.nlstar.com/ref/LiDFTV/"),
    ]
    for name, url in catalog_items:
        builder.row(InlineKeyboardButton(text=name, url=url))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main"))
    return builder.as_markup()


def important_links_keyboard():
    """Важные ссылки"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➡️ Иду в лс к Грошевой", url="http://t.me/groshevatanka"))
    builder.row(InlineKeyboardButton(text="➡️ Стать клиентом", url="https://nlstar.com/ref/ZeTJmV/"))
    builder.row(InlineKeyboardButton(text="➡️ Стать партнёром", url="https://nlstar.com/ref/HnDPwC/"))
    builder.row(InlineKeyboardButton(text="➡️ День открытых дверей", url="https://t.me/+pMgLQZGx4p5mYjk6"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main"))
    return builder.as_markup()


def admin_menu_keyboard():
    """Админ-панель (inline)"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📝 Посты", callback_data="admin_posts"),
        InlineKeyboardButton(text="🔗 Ссылки", callback_data="admin_marathons")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="admin_settings")
    )
    builder.row(InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_main"))
    return builder.as_markup()


def posts_management_keyboard():
    """Управление постами (inline)"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ Добавить пост", callback_data="add_post"),
        InlineKeyboardButton(text="📋 Список постов", callback_data="list_posts")
    )
    builder.row(
        InlineKeyboardButton(text="📁 Категории", callback_data="manage_categories"),
        InlineKeyboardButton(text="📂 Подкатегории", callback_data="manage_subcategories")
    )
    builder.row(InlineKeyboardButton(text="🔙 В админку", callback_data="menu_admin"))
    return builder.as_markup()


def marathons_management_keyboard():
    """Управление марафонами (inline)"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ Добавить марафон", callback_data="add_marathon"),
        InlineKeyboardButton(text="📋 Список марафонов", callback_data="list_marathons")
    )
    builder.row(InlineKeyboardButton(text="🔙 В админку", callback_data="menu_admin"))
    return builder.as_markup()


def settings_keyboard(notifications_on: bool = True):
    """Настройки (inline)"""
    builder = InlineKeyboardBuilder()
    notif_text = "🔔 Уведомления: ВКЛ" if notifications_on else "🔕 Уведомления: ВЫКЛ"
    builder.row(InlineKeyboardButton(text=notif_text, callback_data="toggle_notifications"))
    builder.row(InlineKeyboardButton(text="🔙 В админку", callback_data="menu_admin"))
    return builder.as_markup()




def yes_no_keyboard():
    """Да/Нет"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Да", callback_data="confirm_yes"),
        InlineKeyboardButton(text="❌ Нет", callback_data="confirm_no")
    )
    return builder.as_markup()


def broadcast_keyboard():
    """Рассылка при добавлении поста"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📢 Разослать всем", callback_data="broadcast_yes"),
        InlineKeyboardButton(text="❌ Не рассылать", callback_data="broadcast_no")
    )
    return builder.as_markup()


# ========== Inline клавиатуры ==========

def categories_inline_keyboard(categories: list, prefix: str = "cat"):
    """Клавиатура с категориями"""
    builder = InlineKeyboardBuilder()
    for cat_id, name, emoji in categories:
        builder.row(InlineKeyboardButton(
            text=f"{emoji} {name}",
            callback_data=f"{prefix}_{cat_id}"
        ))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main"))
    return builder.as_markup()


def subcategories_inline_keyboard(subcategories: list, category_id: int, prefix: str = "subcat"):
    """Клавиатура с подкатегориями"""
    builder = InlineKeyboardBuilder()
    for sub_id, name in subcategories:
        builder.row(InlineKeyboardButton(
            text=name,
            callback_data=f"{prefix}_{sub_id}"
        ))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data=f"back_to_categories"))
    return builder.as_markup()


def posts_inline_keyboard(posts: list, back_callback: str = "back_to_subcategories"):
    """Клавиатура с постами"""
    builder = InlineKeyboardBuilder()
    for post_id, title, *_ in posts:
        builder.row(InlineKeyboardButton(
            text=title[:50],
            callback_data=f"post_{post_id}"
        ))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data=back_callback))
    return builder.as_markup()


def post_actions_keyboard(post_id: int, back_callback: str = "back_to_posts"):
    """Действия с постом (для админа)"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_post_{post_id}"),
        InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_post_{post_id}")
    )
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data=back_callback))
    return builder.as_markup()


def marathons_inline_keyboard(marathons: list, is_admin: bool = False):
    """Клавиатура с марафонами"""
    builder = InlineKeyboardBuilder()
    for m_id, name, url, emoji, clicks in marathons:
        builder.row(InlineKeyboardButton(
            text=f"{emoji} {name}",
            callback_data=f"marathon_{m_id}"
        ))
    builder.row(InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_main"))
    return builder.as_markup()


def marathon_link_keyboard(marathon_id: int, url: str):
    """Кнопка для перехода по ссылке марафона"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔗 Перейти по ссылке", url=url))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_marathons"))
    return builder.as_markup()


def marathon_actions_keyboard(marathon_id: int):
    """Действия с марафоном (для админа)"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_marathon_{marathon_id}"),
        InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_marathon_{marathon_id}")
    )
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_marathons_list"))
    return builder.as_markup()


def admin_categories_keyboard(categories: list):
    """Категории для админа"""
    builder = InlineKeyboardBuilder()
    for cat_id, name, emoji in categories:
        builder.row(
            InlineKeyboardButton(text=f"{emoji} {name}", callback_data=f"admin_cat_{cat_id}"),
            InlineKeyboardButton(text="🗑", callback_data=f"delete_cat_{cat_id}")
        )
    builder.row(InlineKeyboardButton(text="➕ Добавить категорию", callback_data="add_category"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_posts_menu"))
    return builder.as_markup()


def admin_subcategories_keyboard(subcategories: list, category_id: int):
    """Подкатегории для админа"""
    builder = InlineKeyboardBuilder()
    for sub_id, name in subcategories:
        builder.row(
            InlineKeyboardButton(text=name, callback_data=f"admin_subcat_{sub_id}"),
            InlineKeyboardButton(text="🗑", callback_data=f"delete_subcat_{sub_id}")
        )
    builder.row(InlineKeyboardButton(text="➕ Добавить подкатегорию", callback_data=f"add_subcat_{category_id}"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_categories_admin"))
    return builder.as_markup()


def admin_posts_keyboard(posts: list):
    """Посты для админа"""
    builder = InlineKeyboardBuilder()
    for post_id, title, *_ in posts:
        builder.row(
            InlineKeyboardButton(text=title[:40], callback_data=f"admin_post_{post_id}"),
            InlineKeyboardButton(text="🗑", callback_data=f"del_post_{post_id}")
        )
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_posts_menu"))
    return builder.as_markup()


def admin_marathons_keyboard(marathons: list):
    """Марафоны для админа"""
    builder = InlineKeyboardBuilder()
    for m_id, name, url, emoji, clicks in marathons:
        builder.row(
            InlineKeyboardButton(text=f"{emoji} {name}", callback_data=f"admin_marathon_{m_id}"),
            InlineKeyboardButton(text="🗑", callback_data=f"del_marathon_{m_id}")
        )
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_marathons_menu"))
    return builder.as_markup()


def select_category_keyboard(categories: list, prefix: str = "select_cat"):
    """Выбор категории"""
    builder = InlineKeyboardBuilder()
    for cat_id, name, emoji in categories:
        builder.row(InlineKeyboardButton(
            text=f"{emoji} {name}",
            callback_data=f"{prefix}_{cat_id}"
        ))
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_action"))
    return builder.as_markup()


def select_subcategory_keyboard(subcategories: list, prefix: str = "select_subcat"):
    """Выбор подкатегории"""
    builder = InlineKeyboardBuilder()
    for sub_id, name in subcategories:
        builder.row(InlineKeyboardButton(
            text=name,
            callback_data=f"{prefix}_{sub_id}"
        ))
    builder.row(InlineKeyboardButton(text="⏩ Без подкатегории", callback_data=f"{prefix}_none"))
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_action"))
    return builder.as_markup()

