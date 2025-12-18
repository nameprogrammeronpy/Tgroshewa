import aiosqlite

DATABASE_PATH = "bot_database.db"


async def init_db():
    """Инициализация базы данных"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Таблица пользователей
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notifications_enabled INTEGER DEFAULT 1
            )
        ''')

        # Таблица категорий
        await db.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                emoji TEXT DEFAULT ''
            )
        ''')

        # Таблица подкатегорий
        await db.execute('''
            CREATE TABLE IF NOT EXISTS subcategories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category_id INTEGER,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
            )
        ''')

        # Таблица постов
        await db.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                media_type TEXT,
                media_file_id TEXT,
                category_id INTEGER,
                subcategory_id INTEGER,
                views INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
                FOREIGN KEY (subcategory_id) REFERENCES subcategories(id) ON DELETE SET NULL
            )
        ''')

        # Таблица марафонов (ссылок)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS marathons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                emoji TEXT DEFAULT '➡️',
                clicks INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Таблица просмотров постов (для статистики)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS post_views (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                user_id INTEGER,
                viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
            )
        ''')

        # Таблица кликов по ссылкам
        await db.execute('''
            CREATE TABLE IF NOT EXISTS marathon_clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                marathon_id INTEGER,
                user_id INTEGER,
                clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (marathon_id) REFERENCES marathons(id) ON DELETE CASCADE
            )
        ''')

        await db.commit()

        # Добавляем начальные категории если их нет
        await add_initial_data(db)


async def add_initial_data(db):
    """Добавление начальных данных"""
    # Категории
    categories = [
        ("Бизнес", "🏢"),
        ("Питание", "🍽"),
        ("Здоровье", "💪")
    ]

    for name, emoji in categories:
        try:
            await db.execute(
                "INSERT OR IGNORE INTO categories (name, emoji) VALUES (?, ?)",
                (name, emoji)
            )
        except:
            pass

    # Марафоны (важные ссылки)
    marathons = [
        ("Иду в лс к Грошевой", "http://t.me/groshevatanka", "➡️"),
        ("Стать клиентом", "https://nlstar.com/ref/ZeTJmV/", "➡️"),
        ("Стать партнёром", "https://nlstar.com/ref/HnDPwC/", "➡️"),
        ("День открытых дверей", "https://t.me/+pMgLQZGx4p5mYjk6", "➡️")
    ]

    for name, url, emoji in marathons:
        cursor = await db.execute("SELECT id FROM marathons WHERE name = ?", (name,))
        if not await cursor.fetchone():
            await db.execute(
                "INSERT INTO marathons (name, url, emoji) VALUES (?, ?, ?)",
                (name, url, emoji)
            )

    await db.commit()


async def restore_marathons():
    """Восстановление марафонов если удалены"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        marathons = [
            ("Иду в лс к Грошевой", "http://t.me/groshevatanka", "➡️"),
            ("Стать клиентом", "https://nlstar.com/ref/ZeTJmV/", "➡️"),
            ("Стать партнёром", "https://nlstar.com/ref/HnDPwC/", "➡️"),
            ("День открытых дверей", "https://t.me/+pMgLQZGx4p5mYjk6", "➡️")
        ]

        for name, url, emoji in marathons:
            cursor = await db.execute("SELECT id FROM marathons WHERE name = ?", (name,))
            if not await cursor.fetchone():
                await db.execute(
                    "INSERT INTO marathons (name, url, emoji) VALUES (?, ?, ?)",
                    (name, url, emoji)
                )

        await db.commit()


# ========== Пользователи ==========
async def add_user(user_id: int, username: str = None, first_name: str = None):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name) 
            VALUES (?, ?, ?)
        ''', (user_id, username, first_name))
        await db.commit()


async def get_all_users():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT user_id, notifications_enabled FROM users")
        return await cursor.fetchall()


async def get_users_count():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        result = await cursor.fetchone()
        return result[0] if result else 0


async def toggle_notifications(user_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT notifications_enabled FROM users WHERE user_id = ?", (user_id,)
        )
        result = await cursor.fetchone()
        new_value = 0 if result and result[0] == 1 else 1
        await db.execute(
            "UPDATE users SET notifications_enabled = ? WHERE user_id = ?",
            (new_value, user_id)
        )
        await db.commit()
        return new_value


# ========== Категории ==========
async def get_categories():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT id, name, emoji FROM categories")
        return await cursor.fetchall()


async def get_category(category_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT id, name, emoji FROM categories WHERE id = ?", (category_id,)
        )
        return await cursor.fetchone()


async def add_category(name: str, emoji: str = ""):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO categories (name, emoji) VALUES (?, ?)", (name, emoji)
        )
        await db.commit()


async def delete_category(category_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        await db.commit()


# ========== Подкатегории ==========
async def get_subcategories(category_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT id, name FROM subcategories WHERE category_id = ?", (category_id,)
        )
        return await cursor.fetchall()


async def get_subcategory(subcategory_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT id, name, category_id FROM subcategories WHERE id = ?", (subcategory_id,)
        )
        return await cursor.fetchone()


async def add_subcategory(name: str, category_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO subcategories (name, category_id) VALUES (?, ?)",
            (name, category_id)
        )
        await db.commit()


async def delete_subcategory(subcategory_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM subcategories WHERE id = ?", (subcategory_id,))
        await db.commit()


# ========== Посты ==========
async def get_posts(category_id: int = None, subcategory_id: int = None):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        if subcategory_id:
            cursor = await db.execute(
                "SELECT id, title, description, media_type, media_file_id, views FROM posts WHERE subcategory_id = ?",
                (subcategory_id,)
            )
        elif category_id:
            cursor = await db.execute(
                "SELECT id, title, description, media_type, media_file_id, views FROM posts WHERE category_id = ?",
                (category_id,)
            )
        else:
            cursor = await db.execute(
                "SELECT id, title, description, media_type, media_file_id, views FROM posts"
            )
        return await cursor.fetchall()


async def get_post(post_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT id, title, description, media_type, media_file_id, category_id, subcategory_id, views FROM posts WHERE id = ?",
            (post_id,)
        )
        return await cursor.fetchone()


async def add_post(title: str, description: str, media_type: str, media_file_id: str,
                   category_id: int, subcategory_id: int = None):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute('''
            INSERT INTO posts (title, description, media_type, media_file_id, category_id, subcategory_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, description, media_type, media_file_id, category_id, subcategory_id))
        await db.commit()
        return cursor.lastrowid


async def update_post(post_id: int, title: str, description: str, media_type: str = None,
                      media_file_id: str = None, category_id: int = None, subcategory_id: int = None):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        if media_type and media_file_id:
            await db.execute('''
                UPDATE posts SET title = ?, description = ?, media_type = ?, media_file_id = ?,
                category_id = ?, subcategory_id = ? WHERE id = ?
            ''', (title, description, media_type, media_file_id, category_id, subcategory_id, post_id))
        else:
            await db.execute('''
                UPDATE posts SET title = ?, description = ?, category_id = ?, subcategory_id = ? WHERE id = ?
            ''', (title, description, category_id, subcategory_id, post_id))
        await db.commit()


async def delete_post(post_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        await db.commit()


async def increment_post_views(post_id: int, user_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE posts SET views = views + 1 WHERE id = ?", (post_id,))
        await db.execute(
            "INSERT INTO post_views (post_id, user_id) VALUES (?, ?)",
            (post_id, user_id)
        )
        await db.commit()


async def get_posts_count():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM posts")
        result = await cursor.fetchone()
        return result[0] if result else 0


async def get_total_views():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT SUM(views) FROM posts")
        result = await cursor.fetchone()
        return result[0] if result and result[0] else 0


# ========== Марафоны ==========
async def get_marathons():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT id, name, url, emoji, clicks FROM marathons")
        return await cursor.fetchall()


async def get_marathon(marathon_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT id, name, url, emoji, clicks FROM marathons WHERE id = ?", (marathon_id,)
        )
        return await cursor.fetchone()


async def add_marathon(name: str, url: str, emoji: str = "➡️"):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO marathons (name, url, emoji) VALUES (?, ?, ?)",
            (name, url, emoji)
        )
        await db.commit()


async def update_marathon(marathon_id: int, name: str, url: str, emoji: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE marathons SET name = ?, url = ?, emoji = ? WHERE id = ?",
            (name, url, emoji, marathon_id)
        )
        await db.commit()


async def delete_marathon(marathon_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM marathons WHERE id = ?", (marathon_id,))
        await db.commit()


async def increment_marathon_clicks(marathon_id: int, user_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE marathons SET clicks = clicks + 1 WHERE id = ?", (marathon_id,))
        await db.execute(
            "INSERT INTO marathon_clicks (marathon_id, user_id) VALUES (?, ?)",
            (marathon_id, user_id)
        )
        await db.commit()


async def get_total_clicks():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT SUM(clicks) FROM marathons")
        result = await cursor.fetchone()
        return result[0] if result and result[0] else 0

