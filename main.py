import asyncio
import logging
import os
import random
from dotenv import load_dotenv
from aiohttp import web

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

import database as db
import keyboards as kb

# Загрузка переменных окружения
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMINS = [int(x) for x in os.getenv("ADMINS", "").split(",") if x.strip()]

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Сообщения для рассылки по категориям
BROADCAST_MESSAGES = {
    "Бизнес": [
        "🔥 Новый пост о бизнесе! Узнай секреты успеха 💼",
        "💡 Свежие идеи для твоего бизнеса уже ждут тебя!",
        "🚀 Хочешь расти? Смотри новый материал!",
        "📈 Полезная информация для предпринимателей!",
        "💪 Время действовать! Новый пост специально для тебя!",
    ],
    "Питание": [
        "🍽 Новый рецепт здорового питания! Попробуй!",
        "🥗 Узнай, как питаться правильно и вкусно!",
        "🌿 Секреты здорового питания в новом посте!",
        "😋 Вкусно и полезно — смотри новый материал!",
        "🍎 Заботься о себе! Новая полезная информация!",
    ],
    "Здоровье": [
        "💪 Новый пост о здоровье! Береги себя!",
        "🏃 Узнай, как быть в форме каждый день!",
        "❤️ Здоровье — это главное! Смотри новый материал!",
        "🌟 Полезные советы для твоего здоровья!",
        "✨ Время позаботиться о себе! Новый пост для тебя!",
    ],
}


# ========== FSM States ==========
class AddPostStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_media = State()
    waiting_for_category = State()
    waiting_for_subcategory = State()
    waiting_for_broadcast = State()


class EditPostStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_media = State()


class AddMarathonStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_url = State()
    waiting_for_emoji = State()


class EditMarathonStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_url = State()
    waiting_for_emoji = State()


class AddCategoryStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_emoji = State()


class AddSubcategoryStates(StatesGroup):
    waiting_for_name = State()


# ========== Helpers ==========
def is_admin(user_id: int) -> bool:
    return user_id in ADMINS


async def send_post_to_user(chat_id: int, post: tuple, category_name: str = None):
    """Отправить пост пользователю с зазывающим сообщением"""
    post_id, title, description, media_type, media_file_id, *_ = post

    # Выбираем случайное зазывающее сообщение по категории
    if category_name and category_name in BROADCAST_MESSAGES:
        intro_message = random.choice(BROADCAST_MESSAGES[category_name])
    else:
        intro_message = "🔥 Новый пост для тебя! Смотри скорее!"

    text = f"{intro_message}\n\n<b>{title}</b>\n\n{description or ''}"

    try:
        if media_type == "photo" and media_file_id:
            await bot.send_photo(chat_id, media_file_id, caption=text, parse_mode="HTML")
        elif media_type == "video" and media_file_id:
            await bot.send_video(chat_id, media_file_id, caption=text, parse_mode="HTML")
        else:
            await bot.send_message(chat_id, text, parse_mode="HTML")
        return True
    except Exception as e:
        logger.error(f"Error sending post to {chat_id}: {e}")
        return False


# ========== Основные команды ==========
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await db.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)

    text = f"✨ <b>Привет, {message.from_user.first_name}!</b> ✨\n\n"
    text += "Рада видеть тебя здесь! 🤗\n\n"
    text += "Здесь ты найдёшь:\n"
    text += "🏢 Полезные материалы о бизнесе\n"
    text += "🍽 Секреты правильного питания\n"
    text += "💪 Советы для здоровья\n"
    text += "🛍 Каталог товаров со скидками\n\n"
    text += "Выбирай раздел и начинай! 👇"

    await message.answer(text, parse_mode="HTML", reply_markup=kb.main_menu_keyboard(is_admin(message.from_user.id)))


@router.message(Command("help"))
async def cmd_help(message: Message):
    text = "📚 <b>Помощь по боту</b>\n\n"
    text += "🏢 <b>Бизнес</b> — посты о бизнесе\n"
    text += "🍽 <b>Питание</b> — посты о питании\n"
    text += "💪 <b>Здоровье</b> — посты о здоровье\n"
    text += "🔥 <b>Марафоны</b> — полезные ссылки\n\n"
    text += "📌 <b>Команды:</b>\n"
    text += "/start — главное меню\n"
    text += "/help — помощь\n"
    text += "/menu — открыть меню"

    await message.answer(text, parse_mode="HTML")


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("📋 Главное меню:", reply_markup=kb.main_menu_keyboard(is_admin(message.from_user.id)))


# ========== Категории для пользователей ==========
@router.callback_query(F.data.in_(["menu_business", "menu_food", "menu_health"]))
async def show_category(callback: CallbackQuery, state: FSMContext):
    category_map = {
        "menu_business": "Бизнес",
        "menu_food": "Питание",
        "menu_health": "Здоровье"
    }
    category_name = category_map.get(callback.data)

    categories = await db.get_categories()
    category = next((c for c in categories if c[1] == category_name), None)

    if not category:
        await callback.answer("Категория не найдена")
        return

    category_id = category[0]
    await state.update_data(current_category_id=category_id)

    # Проверяем есть ли подкатегории
    subcategories = await db.get_subcategories(category_id)

    if subcategories:
        await callback.message.edit_text(
            f"📂 {category[2]} {category[1]}\n\nВыберите подкатегорию:",
            reply_markup=kb.subcategories_inline_keyboard(subcategories, category_id)
        )
    else:
        # Показываем посты напрямую
        posts = await db.get_posts(category_id=category_id)
        if posts:
            await callback.message.edit_text(
                f"📂 {category[2]} {category[1]}\n\nВыберите пост:",
                reply_markup=kb.posts_inline_keyboard(posts, "back_to_main")
            )
        else:
            builder = kb.InlineKeyboardBuilder()
            builder.row(kb.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main"))
            await callback.message.edit_text(
                f"📂 {category[2]} {category[1]}\n\nВ этой категории пока нет постов.",
                reply_markup=builder.as_markup()
            )

    await callback.answer()


@router.callback_query(F.data.startswith("subcat_"))
async def show_subcategory_posts(callback: CallbackQuery, state: FSMContext):
    subcategory_id = int(callback.data.split("_")[1])
    subcategory = await db.get_subcategory(subcategory_id)

    if not subcategory:
        await callback.answer("Подкатегория не найдена")
        return

    await state.update_data(current_subcategory_id=subcategory_id, current_category_id=subcategory[2])

    posts = await db.get_posts(subcategory_id=subcategory_id)

    if posts:
        await callback.message.edit_text(
            f"📁 {subcategory[1]}\n\nВыберите пост:",
            reply_markup=kb.posts_inline_keyboard(posts, f"back_subcat_{subcategory[2]}")
        )
    else:
        await callback.message.edit_text(
            f"📁 {subcategory[1]}\n\nВ этой подкатегории пока нет постов.",
            reply_markup=kb.subcategories_inline_keyboard([], subcategory[2])
        )

    await callback.answer()


@router.callback_query(F.data.startswith("back_subcat_"))
async def back_to_subcategories(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[2])
    subcategories = await db.get_subcategories(category_id)
    category = await db.get_category(category_id)

    await callback.message.edit_text(
        f"📂 {category[2]} {category[1]}\n\nВыберите подкатегорию:",
        reply_markup=kb.subcategories_inline_keyboard(subcategories, category_id)
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery, state: FSMContext):
    categories = await db.get_categories()
    await callback.message.edit_text(
        "Выберите категорию:",
        reply_markup=kb.categories_inline_keyboard(categories)
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_main")
async def callback_back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "📋 Главное меню:",
        reply_markup=kb.main_menu_keyboard(is_admin(callback.from_user.id))
    )
    await callback.answer()


# ========== Каталог товаров ==========
@router.callback_query(F.data == "menu_catalog")
async def show_catalog(callback: CallbackQuery):
    text = "🛍 <b>Каталог товаров</b>\n\n"
    text += "📌 Цены на сайте без скидок, за скидками ко мне!\n\n"
    text += "Выбирай категорию и переходи в магазин 👇"

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=kb.catalog_keyboard()
    )
    await callback.answer()


# ========== Важные ссылки ==========
@router.callback_query(F.data == "menu_links")
async def show_important_links(callback: CallbackQuery):
    text = "🔗 <b>Важные ссылки</b>\n\n"
    text += "Переходи по нужной ссылке 👇"

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=kb.important_links_keyboard()
    )
    await callback.answer()


# ========== Просмотр постов ==========
@router.callback_query(F.data.startswith("post_"))
async def show_post(callback: CallbackQuery, state: FSMContext):
    post_id = int(callback.data.split("_")[1])
    post = await db.get_post(post_id)

    if not post:
        await callback.answer("Пост не найден")
        return

    # Увеличиваем счётчик просмотров
    await db.increment_post_views(post_id, callback.from_user.id)

    post_id, title, description, media_type, media_file_id, category_id, subcategory_id, views = post
    text = f"<b>{title}</b>\n\n{description or ''}\n\n👁 Просмотров: {views + 1}"

    # Определяем куда возвращаться
    if subcategory_id:
        back_callback = f"back_subcat_{category_id}"
    else:
        back_callback = "back_to_main"

    back_kb = kb.InlineKeyboardBuilder()
    back_kb.row(kb.InlineKeyboardButton(text="🔙 Назад", callback_data=back_callback))

    await callback.message.delete()

    if media_type == "photo" and media_file_id:
        await callback.message.answer_photo(media_file_id, caption=text, parse_mode="HTML", reply_markup=back_kb.as_markup())
    elif media_type == "video" and media_file_id:
        await callback.message.answer_video(media_file_id, caption=text, parse_mode="HTML", reply_markup=back_kb.as_markup())
    else:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=back_kb.as_markup())

    await callback.answer()


# ========== Марафоны ==========
@router.callback_query(F.data == "menu_marathons")
async def show_marathons(callback: CallbackQuery):
    marathons = await db.get_marathons()

    if marathons:
        await callback.message.edit_text(
            "🔥 <b>Марафоны и ссылки</b>\n\nВыберите интересующий марафон:",
            parse_mode="HTML",
            reply_markup=kb.marathons_inline_keyboard(marathons)
        )
    else:
        builder = kb.InlineKeyboardBuilder()
        builder.row(kb.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main"))
        await callback.message.edit_text("Пока нет доступных марафонов.", reply_markup=builder.as_markup())

    await callback.answer()


@router.callback_query(F.data.startswith("marathon_"))
async def show_marathon(callback: CallbackQuery):
    marathon_id = int(callback.data.split("_")[1])
    marathon = await db.get_marathon(marathon_id)

    if not marathon:
        await callback.answer("Марафон не найден")
        return

    m_id, name, url, emoji, clicks = marathon

    # Увеличиваем счётчик кликов
    await db.increment_marathon_clicks(marathon_id, callback.from_user.id)

    text = f"{emoji} <b>{name}</b>\n\n🔗 Нажмите кнопку ниже, чтобы перейти:"

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=kb.marathon_link_keyboard(marathon_id, url)
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_marathons")
async def back_to_marathons(callback: CallbackQuery):
    marathons = await db.get_marathons()
    await callback.message.edit_text(
        "🔥 <b>Марафоны и ссылки</b>\n\nВыберите интересующий марафон:",
        parse_mode="HTML",
        reply_markup=kb.marathons_inline_keyboard(marathons)
    )
    await callback.answer()


# ========== АДМИНКА ==========
@router.callback_query(F.data == "menu_admin")
async def admin_panel(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет доступа к админ-панели.", show_alert=True)
        return

    await callback.message.edit_text(
        "⚙️ <b>Админ-панель</b>\n\nВыберите раздел:",
        parse_mode="HTML",
        reply_markup=kb.admin_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_posts")
async def posts_management(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    await callback.message.edit_text(
        "📝 <b>Управление постами</b>",
        parse_mode="HTML",
        reply_markup=kb.posts_management_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "add_post")
async def add_post_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return

    await state.set_state(AddPostStates.waiting_for_title)
    await callback.message.edit_text("📝 Введите название поста:\n\n(или /cancel для отмены)")
    await callback.answer()


@router.message(Command("cancel"))
async def cancel_command(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()
        await message.answer("❌ Действие отменено.\n\n📋 Главное меню:",
                            reply_markup=kb.main_menu_keyboard(is_admin(message.from_user.id)))


@router.message(AddPostStates.waiting_for_title)
async def add_post_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AddPostStates.waiting_for_description)
    await message.answer("📝 Введите описание поста:\n\n(или отправьте '-' чтобы пропустить)")


@router.message(AddPostStates.waiting_for_description)
async def add_post_description(message: Message, state: FSMContext):
    if message.text == "-":
        await state.update_data(description="")
    else:
        await state.update_data(description=message.text)

    await state.set_state(AddPostStates.waiting_for_media)
    await message.answer("📷 Отправьте фото или видео для поста:\n\n(или отправьте '-' чтобы пропустить)")


@router.message(AddPostStates.waiting_for_media)
async def add_post_media(message: Message, state: FSMContext):
    if message.text == "-":
        await state.update_data(media_type=None, media_file_id=None)
    elif message.photo:
        await state.update_data(media_type="photo", media_file_id=message.photo[-1].file_id)
    elif message.video:
        await state.update_data(media_type="video", media_file_id=message.video.file_id)
    else:
        await message.answer("Пожалуйста, отправьте фото, видео или '-' чтобы пропустить")
        return

    categories = await db.get_categories()
    await state.set_state(AddPostStates.waiting_for_category)
    await message.answer("📁 Выберите категорию:", reply_markup=kb.select_category_keyboard(categories, "new_post_cat"))


@router.callback_query(F.data.startswith("new_post_cat_"))
async def add_post_category(callback: CallbackQuery, state: FSMContext):
    # new_post_cat_1 -> извлекаем ID после последнего _
    parts = callback.data.split("_")
    category_id = int(parts[-1])  # берём последний элемент
    await state.update_data(category_id=category_id)

    subcategories = await db.get_subcategories(category_id)

    if subcategories:
        await state.set_state(AddPostStates.waiting_for_subcategory)
        await callback.message.edit_text(
            "📂 Выберите подкатегорию:",
            reply_markup=kb.select_subcategory_keyboard(subcategories, "new_post_subcat")
        )
    else:
        # Нет подкатегорий - спрашиваем создать ли
        builder = kb.InlineKeyboardBuilder()
        builder.row(kb.InlineKeyboardButton(text="⏩ Без подкатегории", callback_data="new_post_subcat_none"))
        builder.row(kb.InlineKeyboardButton(text="➕ Создать подкатегорию", callback_data=f"create_subcat_for_post_{category_id}"))
        builder.row(kb.InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_action"))
        await callback.message.edit_text(
            "📂 В этой категории нет подкатегорий.\n\nВыберите действие:",
            reply_markup=builder.as_markup()
        )

    await callback.answer()


@router.callback_query(F.data.startswith("new_post_subcat_"))
async def add_post_subcategory(callback: CallbackQuery, state: FSMContext):
    # new_post_subcat_1 или new_post_subcat_none
    parts = callback.data.split("_")
    subcat_data = parts[-1]  # берём последний элемент

    if subcat_data == "none":
        await state.update_data(subcategory_id=None)
    else:
        await state.update_data(subcategory_id=int(subcat_data))

    await save_new_post(callback, state)
    await callback.answer()


class CreateSubcatForPostStates(StatesGroup):
    waiting_for_name = State()


@router.callback_query(F.data.startswith("create_subcat_for_post_"))
async def create_subcat_for_post_start(callback: CallbackQuery, state: FSMContext):
    """Создание подкатегории прямо при создании поста"""
    category_id = int(callback.data.split("_")[-1])
    await state.update_data(category_id=category_id)
    await state.set_state(CreateSubcatForPostStates.waiting_for_name)

    await callback.message.edit_text("📂 Введите название новой подкатегории:")
    await callback.answer()


@router.message(CreateSubcatForPostStates.waiting_for_name)
async def create_subcat_for_post_name(message: Message, state: FSMContext):
    """Сохраняем подкатегорию и продолжаем создание поста"""
    data = await state.get_data()
    category_id = data["category_id"]

    # Создаём подкатегорию
    await db.add_subcategory(message.text, category_id)

    # Получаем ID только что созданной подкатегории
    subcategories = await db.get_subcategories(category_id)
    new_subcat = next((s for s in subcategories if s[1] == message.text), None)

    if new_subcat:
        await state.update_data(subcategory_id=new_subcat[0])
    else:
        await state.update_data(subcategory_id=None)

    # Очищаем состояние FSM и сохраняем пост
    await state.set_state(None)

    # Сохраняем пост
    post_data = await state.get_data()

    post_id = await db.add_post(
        title=post_data["title"],
        description=post_data.get("description", ""),
        media_type=post_data.get("media_type"),
        media_file_id=post_data.get("media_file_id"),
        category_id=post_data["category_id"],
        subcategory_id=post_data.get("subcategory_id")
    )

    await state.update_data(new_post_id=post_id)

    await message.answer(
        f"✅ Подкатегория создана и пост сохранён!\n\nХотите разослать его всем пользователям?",
        reply_markup=kb.broadcast_keyboard()
    )


async def save_new_post(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    post_id = await db.add_post(
        title=data["title"],
        description=data.get("description", ""),
        media_type=data.get("media_type"),
        media_file_id=data.get("media_file_id"),
        category_id=data["category_id"],
        subcategory_id=data.get("subcategory_id")
    )

    await state.update_data(new_post_id=post_id)

    await callback.message.edit_text(
        f"✅ Пост успешно создан!\n\nХотите разослать его всем пользователям?",
        reply_markup=kb.broadcast_keyboard()
    )


@router.callback_query(F.data == "broadcast_yes")
async def broadcast_post(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    post_id = data.get("new_post_id")

    if not post_id:
        await callback.answer("Ошибка: пост не найден")
        return

    post = await db.get_post(post_id)
    users = await db.get_all_users()

    # Получаем название категории для зазывающих сообщений
    category_name = None
    if post and post[5]:  # category_id
        category = await db.get_category(post[5])
        if category:
            category_name = category[1]

    sent_count = 0
    for user_id, notifications_enabled in users:
        if notifications_enabled:
            if await send_post_to_user(user_id, post, category_name):
                sent_count += 1

    await state.clear()
    await callback.message.edit_text(f"📢 Пост разослан {sent_count} пользователям!")
    await callback.message.answer("📝 Управление постами", reply_markup=kb.posts_management_keyboard())
    await callback.answer()


@router.callback_query(F.data == "broadcast_no")
async def skip_broadcast(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("✅ Пост сохранён без рассылки.")
    await callback.message.answer("📝 Управление постами", reply_markup=kb.posts_management_keyboard())
    await callback.answer()


@router.callback_query(F.data == "cancel_action")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("Действие отменено", reply_markup=kb.posts_management_keyboard())
    await callback.answer()


# ========== Список постов ==========
@router.callback_query(F.data == "list_posts")
async def list_posts(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    posts = await db.get_posts()

    if posts:
        await callback.message.edit_text(
            "📋 <b>Список постов</b>\n\nВыберите пост для редактирования:",
            parse_mode="HTML",
            reply_markup=kb.admin_posts_keyboard(posts)
        )
    else:
        builder = kb.InlineKeyboardBuilder()
        builder.row(kb.InlineKeyboardButton(text="🔙 Назад", callback_data="admin_posts"))
        await callback.message.edit_text("Постов пока нет.", reply_markup=builder.as_markup())

    await callback.answer()


@router.callback_query(F.data.startswith("admin_post_"))
async def admin_view_post(callback: CallbackQuery, state: FSMContext):
    post_id = int(callback.data.split("_")[2])
    post = await db.get_post(post_id)

    if not post:
        await callback.answer("Пост не найден")
        return

    post_id, title, description, media_type, media_file_id, category_id, subcategory_id, views = post

    category = await db.get_category(category_id)
    cat_name = category[1] if category else "Нет"

    subcat_name = "Нет"
    if subcategory_id:
        subcat = await db.get_subcategory(subcategory_id)
        if subcat:
            subcat_name = subcat[1]

    text = f"<b>📝 {title}</b>\n\n"
    text += f"📄 Описание: {description[:100]}{'...' if description and len(description) > 100 else ''}\n\n"
    text += f"📁 Категория: {cat_name}\n"
    text += f"📂 Подкатегория: {subcat_name}\n"
    text += f"📷 Медиа: {media_type or 'Нет'}\n"
    text += f"👁 Просмотров: {views}"

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb.post_actions_keyboard(post_id, "back_to_posts_list"))
    await callback.answer()


@router.callback_query(F.data.startswith("del_post_"))
async def delete_post_confirm(callback: CallbackQuery):
    post_id = int(callback.data.split("_")[2])
    await db.delete_post(post_id)

    posts = await db.get_posts()
    await callback.message.edit_text(
        "✅ Пост удалён!\n\n📋 <b>Список постов</b>:",
        parse_mode="HTML",
        reply_markup=kb.admin_posts_keyboard(posts)
    )
    await callback.answer("Пост удалён")


@router.callback_query(F.data.startswith("edit_post_"))
async def edit_post_start(callback: CallbackQuery, state: FSMContext):
    post_id = int(callback.data.split("_")[2])
    await state.update_data(edit_post_id=post_id)
    await state.set_state(EditPostStates.waiting_for_title)

    await callback.message.edit_text("✏️ Введите новое название поста (или отправьте '-' чтобы оставить прежнее):")
    await callback.answer()


@router.message(EditPostStates.waiting_for_title)
async def edit_post_title(message: Message, state: FSMContext):
    data = await state.get_data()
    post = await db.get_post(data["edit_post_id"])

    if message.text != "-":
        await state.update_data(new_title=message.text)
    else:
        await state.update_data(new_title=post[1])

    await state.set_state(EditPostStates.waiting_for_description)
    await message.answer("✏️ Введите новое описание (или '-' чтобы оставить прежнее):")


@router.message(EditPostStates.waiting_for_description)
async def edit_post_description(message: Message, state: FSMContext):
    data = await state.get_data()
    post = await db.get_post(data["edit_post_id"])

    if message.text != "-":
        await state.update_data(new_description=message.text)
    else:
        await state.update_data(new_description=post[2])

    # Обновляем пост
    new_data = await state.get_data()
    await db.update_post(
        post_id=data["edit_post_id"],
        title=new_data["new_title"],
        description=new_data["new_description"],
        category_id=post[5],
        subcategory_id=post[6]
    )

    await state.clear()
    await message.answer("✅ Пост обновлён!", reply_markup=kb.posts_management_keyboard())


@router.callback_query(F.data == "back_to_posts_list")
async def back_to_posts_list(callback: CallbackQuery):
    posts = await db.get_posts()
    await callback.message.edit_text(
        "📋 <b>Список постов</b>:",
        parse_mode="HTML",
        reply_markup=kb.admin_posts_keyboard(posts)
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_posts_menu")
async def back_to_posts_menu(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("📝 Управление постами", reply_markup=kb.posts_management_keyboard())
    await callback.answer()


# ========== Управление категориями ==========
@router.callback_query(F.data == "manage_categories")
async def manage_categories(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    categories = await db.get_categories()
    await callback.message.edit_text(
        "📁 <b>Управление категориями</b>",
        parse_mode="HTML",
        reply_markup=kb.admin_categories_keyboard(categories)
    )
    await callback.answer()


@router.callback_query(F.data == "add_category")
async def add_category_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddCategoryStates.waiting_for_name)
    await callback.message.edit_text("📁 Введите название новой категории:")
    await callback.answer()


@router.message(AddCategoryStates.waiting_for_name)
async def add_category_name(message: Message, state: FSMContext):
    await state.update_data(cat_name=message.text)
    await state.set_state(AddCategoryStates.waiting_for_emoji)
    await message.answer("🎨 Введите эмодзи для категории (например: 🏢):")


@router.message(AddCategoryStates.waiting_for_emoji)
async def add_category_emoji(message: Message, state: FSMContext):
    data = await state.get_data()
    await db.add_category(data["cat_name"], message.text)
    await state.clear()

    categories = await db.get_categories()
    await message.answer(
        "✅ Категория добавлена!\n\n📁 <b>Управление категориями</b>",
        parse_mode="HTML",
        reply_markup=kb.admin_categories_keyboard(categories)
    )


@router.callback_query(F.data.startswith("delete_cat_"))
async def delete_category(callback: CallbackQuery):
    category_id = int(callback.data.split("_")[2])
    await db.delete_category(category_id)

    categories = await db.get_categories()
    await callback.message.edit_text(
        "✅ Категория удалена!\n\n📁 <b>Управление категориями</b>",
        parse_mode="HTML",
        reply_markup=kb.admin_categories_keyboard(categories)
    )
    await callback.answer("Категория удалена")


@router.callback_query(F.data == "back_to_categories_admin")
async def back_to_categories_admin(callback: CallbackQuery):
    categories = await db.get_categories()
    await callback.message.edit_text(
        "📁 <b>Управление категориями</b>",
        parse_mode="HTML",
        reply_markup=kb.admin_categories_keyboard(categories)
    )
    await callback.answer()


# ========== Управление подкатегориями ==========
@router.callback_query(F.data == "manage_subcategories")
async def manage_subcategories(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    categories = await db.get_categories()
    await callback.message.edit_text(
        "📂 Выберите категорию для управления подкатегориями:",
        reply_markup=kb.select_category_keyboard(categories, "manage_subcat")
    )
    await callback.answer()


@router.callback_query(F.data.startswith("manage_subcat_"))
async def show_subcategories_admin(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[2])
    await state.update_data(admin_category_id=category_id)

    subcategories = await db.get_subcategories(category_id)
    category = await db.get_category(category_id)

    await callback.message.edit_text(
        f"📂 Подкатегории для <b>{category[1]}</b>:",
        parse_mode="HTML",
        reply_markup=kb.admin_subcategories_keyboard(subcategories, category_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("add_subcat_"))
async def add_subcategory_start(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[2])
    await state.update_data(admin_category_id=category_id)
    await state.set_state(AddSubcategoryStates.waiting_for_name)

    await callback.message.edit_text("📂 Введите название новой подкатегории:")
    await callback.answer()


@router.message(AddSubcategoryStates.waiting_for_name)
async def add_subcategory_name(message: Message, state: FSMContext):
    data = await state.get_data()
    await db.add_subcategory(message.text, data["admin_category_id"])
    await state.clear()

    subcategories = await db.get_subcategories(data["admin_category_id"])
    await message.answer(
        f"✅ Подкатегория добавлена!",
        reply_markup=kb.admin_subcategories_keyboard(subcategories, data["admin_category_id"])
    )


@router.callback_query(F.data.startswith("delete_subcat_"))
async def delete_subcategory(callback: CallbackQuery, state: FSMContext):
    subcategory_id = int(callback.data.split("_")[2])
    subcat = await db.get_subcategory(subcategory_id)
    category_id = subcat[2] if subcat else None

    await db.delete_subcategory(subcategory_id)

    if category_id:
        subcategories = await db.get_subcategories(category_id)
        await callback.message.edit_text(
            "✅ Подкатегория удалена!",
            reply_markup=kb.admin_subcategories_keyboard(subcategories, category_id)
        )
    await callback.answer("Подкатегория удалена")


# ========== Управление марафонами ==========
@router.callback_query(F.data == "admin_marathons")
async def marathons_management(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    await callback.message.edit_text(
        "🔗 <b>Управление марафонами</b>",
        parse_mode="HTML",
        reply_markup=kb.marathons_management_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "add_marathon")
async def add_marathon_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return

    await state.set_state(AddMarathonStates.waiting_for_name)
    await callback.message.edit_text("🔗 Введите название марафона:\n\n(или /cancel для отмены)")
    await callback.answer()


@router.message(AddMarathonStates.waiting_for_name)
async def add_marathon_name(message: Message, state: FSMContext):
    await state.update_data(marathon_name=message.text)
    await state.set_state(AddMarathonStates.waiting_for_url)
    await message.answer("🔗 Введите URL ссылки:")


@router.message(AddMarathonStates.waiting_for_url)
async def add_marathon_url(message: Message, state: FSMContext):
    await state.update_data(marathon_url=message.text)
    await state.set_state(AddMarathonStates.waiting_for_emoji)
    await message.answer("🎨 Введите эмодзи (или '-' для ➡️ по умолчанию):")


@router.message(AddMarathonStates.waiting_for_emoji)
async def add_marathon_emoji(message: Message, state: FSMContext):
    data = await state.get_data()
    emoji = "➡️" if message.text == "-" else message.text

    await db.add_marathon(data["marathon_name"], data["marathon_url"], emoji)
    await state.clear()

    await message.answer("✅ Марафон добавлен!", reply_markup=kb.marathons_management_keyboard())


@router.callback_query(F.data == "list_marathons")
async def list_marathons(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    marathons = await db.get_marathons()

    if marathons:
        await callback.message.edit_text(
            "📋 <b>Список марафонов</b>",
            parse_mode="HTML",
            reply_markup=kb.admin_marathons_keyboard(marathons)
        )
    else:
        builder = kb.InlineKeyboardBuilder()
        builder.row(kb.InlineKeyboardButton(text="🔙 Назад", callback_data="admin_marathons"))
        await callback.message.edit_text("Марафонов пока нет.", reply_markup=builder.as_markup())

    await callback.answer()


@router.callback_query(F.data.startswith("admin_marathon_"))
async def admin_view_marathon(callback: CallbackQuery, state: FSMContext):
    marathon_id = int(callback.data.split("_")[2])
    marathon = await db.get_marathon(marathon_id)

    if not marathon:
        await callback.answer("Марафон не найден")
        return

    m_id, name, url, emoji, clicks = marathon

    text = f"{emoji} <b>{name}</b>\n\n"
    text += f"🔗 URL: {url}\n"
    text += f"👆 Кликов: {clicks}"

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb.marathon_actions_keyboard(marathon_id))
    await callback.answer()


@router.callback_query(F.data.startswith("del_marathon_"))
async def delete_marathon(callback: CallbackQuery):
    marathon_id = int(callback.data.split("_")[2])
    await db.delete_marathon(marathon_id)

    marathons = await db.get_marathons()
    await callback.message.edit_text(
        "✅ Марафон удалён!\n\n📋 <b>Список марафонов</b>:",
        parse_mode="HTML",
        reply_markup=kb.admin_marathons_keyboard(marathons)
    )
    await callback.answer("Марафон удалён")


@router.callback_query(F.data.startswith("edit_marathon_"))
async def edit_marathon_start(callback: CallbackQuery, state: FSMContext):
    marathon_id = int(callback.data.split("_")[2])
    await state.update_data(edit_marathon_id=marathon_id)
    await state.set_state(EditMarathonStates.waiting_for_name)

    await callback.message.edit_text("✏️ Введите новое название (или '-' чтобы оставить прежнее):")
    await callback.answer()


@router.message(EditMarathonStates.waiting_for_name)
async def edit_marathon_name(message: Message, state: FSMContext):
    data = await state.get_data()
    marathon = await db.get_marathon(data["edit_marathon_id"])

    if message.text != "-":
        await state.update_data(new_name=message.text)
    else:
        await state.update_data(new_name=marathon[1])

    await state.set_state(EditMarathonStates.waiting_for_url)
    await message.answer("✏️ Введите новый URL (или '-'):")


@router.message(EditMarathonStates.waiting_for_url)
async def edit_marathon_url(message: Message, state: FSMContext):
    data = await state.get_data()
    marathon = await db.get_marathon(data["edit_marathon_id"])

    if message.text != "-":
        await state.update_data(new_url=message.text)
    else:
        await state.update_data(new_url=marathon[2])

    await state.set_state(EditMarathonStates.waiting_for_emoji)
    await message.answer("✏️ Введите новый эмодзи (или '-'):")


@router.message(EditMarathonStates.waiting_for_emoji)
async def edit_marathon_emoji(message: Message, state: FSMContext):
    data = await state.get_data()
    marathon = await db.get_marathon(data["edit_marathon_id"])

    if message.text != "-":
        new_emoji = message.text
    else:
        new_emoji = marathon[3]

    await db.update_marathon(
        data["edit_marathon_id"],
        data["new_name"],
        data["new_url"],
        new_emoji
    )

    await state.clear()
    await message.answer("✅ Марафон обновлён!", reply_markup=kb.marathons_management_keyboard())


@router.callback_query(F.data == "back_to_marathons_list")
async def back_to_marathons_list(callback: CallbackQuery):
    marathons = await db.get_marathons()
    await callback.message.edit_text(
        "📋 <b>Список марафонов</b>:",
        parse_mode="HTML",
        reply_markup=kb.admin_marathons_keyboard(marathons)
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_marathons_menu")
async def back_to_marathons_menu(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("🔗 Управление марафонами", reply_markup=kb.marathons_management_keyboard())
    await callback.answer()


# ========== Статистика ==========
@router.callback_query(F.data == "admin_stats")
async def show_statistics(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    users_count = await db.get_users_count()
    posts_count = await db.get_posts_count()
    total_views = await db.get_total_views()
    total_clicks = await db.get_total_clicks()

    text = "📊 <b>Статистика бота</b>\n\n"
    text += f"👥 Пользователей: {users_count}\n"
    text += f"📝 Постов: {posts_count}\n"
    text += f"👁 Всего просмотров: {total_views}\n"
    text += f"👆 Всего кликов по ссылкам: {total_clicks}"

    builder = kb.InlineKeyboardBuilder()
    builder.row(kb.InlineKeyboardButton(text="🔙 Назад", callback_data="menu_admin"))

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=builder.as_markup())
    await callback.answer()


# ========== Настройки ==========
@router.callback_query(F.data == "admin_settings")
async def show_settings(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    # Получаем текущий статус уведомлений
    users = await db.get_all_users()
    user = next((u for u in users if u[0] == callback.from_user.id), None)
    notifications_on = user[1] == 1 if user else True

    await callback.message.edit_text(
        "⚙️ <b>Настройки</b>",
        parse_mode="HTML",
        reply_markup=kb.settings_keyboard(notifications_on)
    )
    await callback.answer()


@router.callback_query(F.data == "toggle_notifications")
async def toggle_notifications(callback: CallbackQuery):
    new_value = await db.toggle_notifications(callback.from_user.id)
    status = "включены ✅" if new_value else "выключены ❌"

    await callback.message.edit_text(
        f"⚙️ <b>Настройки</b>\n\n🔔 Уведомления {status}",
        parse_mode="HTML",
        reply_markup=kb.settings_keyboard(new_value == 1)
    )
    await callback.answer(f"Уведомления {status}")


# ========== HTTP сервер для health checks ==========
async def health_check(request):
    """Endpoint для health check Koyeb"""
    return web.Response(text="OK", status=200)


async def run_web_server():
    """Запуск веб-сервера на порту 8000 для health checks"""
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", 8000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    logger.info(f"Web server started on port {port}")


# ========== Запуск бота ==========
async def main():
    # Инициализация базы данных
    await db.init_db()

    # Восстановление марафонов если удалены
    await db.restore_marathons()

    logger.info("Bot started!")

    # Запуск веб-сервера для health checks
    asyncio.create_task(run_web_server())

    # Запуск polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

