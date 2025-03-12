import asyncio
import logging
from pyrogram import Client, filters, idle
from pyrogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup, 
    InlineQueryResultArticle, InputTextMessageContent
)
from info import API_ID, API_HASH, BOT_TOKEN, ADMINS

# تنظیم لاگ برای مشاهده‌ی خطاها و دیباگینگ
logging.basicConfig(level=logging.INFO)

# بررسی مقدار `ADMINS` و تبدیل به لیست اعداد
if isinstance(ADMINS, str):
    ADMINS = [int(admin.strip()) for admin in ADMINS.split()]
elif isinstance(ADMINS, (list, tuple)):
    ADMINS = list(map(int, ADMINS))
else:
    ADMINS = []

# مقداردهی `Client`
bot = Client(
    "my_bot",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# تابع جستجو (باید در جایی تعریف شود)
async def get_search_results(user_id, query):
    # این تابع را با سیستم پایگاه داده یا API واقعی جایگزین کنید
    return [
        {
            "file_name": "فیلم نمونه",
            "year": "2024",
            "rating": "8.5",
            "genre": "اکشن، ماجراجویی",
            "director": "کارگردان نمونه",
            "actors": "بازیگر 1، بازیگر 2",
            "summary": "این یک خلاصه‌ی نمونه است.",
            "file_size": "1.5GB",
            "imdb_link": "https://www.imdb.com/title/tt1234567/",
            "file_id": "file_123456",
            "poster": "https://example.com/poster.jpg"
        }
    ], None, 1

@bot.on_inline_query()
async def inline_query_handler(client, query):
    search = query.query.strip()
    if not search:
        await query.answer([], cache_time=5)
        return

    try:
        results, _, total = await get_search_results(query.from_user.id, search)
    except Exception as e:
        logging.error(f"خطا در دریافت نتایج جستجو: {e}")
        await query.answer([], cache_time=5)
        return

    if not results:
        await query.answer([], cache_time=5)
        return

    inline_results = []
    for result in results:
        file_id = result.get('file_id', 'unknown_id')
        text = (
            f"🎬 **{result['file_name']}**\n"
            f"📅 **سال انتشار:** {result['year']}\n"
            f"⭐ **امتیاز IMDb:** {result['rating']}\n"
            f"🎭 **ژانر:** {result['genre']}\n"
            f"🎬 **کارگردان:** {result['director']}\n"
            f"👥 **بازیگران:** {result['actors']}\n\n"
            f"📝 **خلاصه:** {result['summary']}\n\n"
            f"📂 **حجم فایل:** {result['file_size']}\n"
        )
        if result.get('imdb_link'):
            text += f"🔗 [مشاهده در IMDb]({result['imdb_link']})\n"

        buttons = [
            [InlineKeyboardButton("📺 مشاهده فصل‌ها", callback_data=f"seasons#{file_id}")],
            [InlineKeyboardButton("📁 مشاهده کیفیت‌ها", callback_data=f"qualities#{file_id}")],
            [InlineKeyboardButton("🌍 انتخاب زبان", callback_data=f"languages#{file_id}")],
            [InlineKeyboardButton("📆 انتخاب سال انتشار", callback_data=f"year#{file_id}")],
            [InlineKeyboardButton("🎭 انتخاب ژانر", callback_data=f"genre#{file_id}")],
            [InlineKeyboardButton("📜 دریافت زیرنویس", callback_data=f"subtitles#{file_id}")],
            [InlineKeyboardButton("🎤 دریافت نسخه دوبله", callback_data=f"dubbing#{file_id}")],
            [InlineKeyboardButton("🔗 اشتراک‌گذاری لیست", switch_inline_query=f"{result['file_name']}")],
        ]

        inline_result = InlineQueryResultArticle(
            title=result['file_name'],
            description=f"{result['genre']} | {result['year']} | امتیاز: {result['rating']}⭐",
            input_message_content=InputTextMessageContent(text),
            reply_markup=InlineKeyboardMarkup(buttons),
            thumb_url=result.get('poster')
        )
        inline_results.append(inline_result)

    await query.answer(inline_results, cache_time=5)

@bot.on_message(filters.command("admin") & filters.user(ADMINS))
async def admin_panel(client, message):
    text = "📊 **پنل مدیریت ربات**\n\n"
    text += "👥 **تعداد کاربران:** 12345\n"
    text += "🎬 **تعداد فیلم‌های موجود:** 6789\n"
    text += "📥 **تعداد دانلودها:** 23456\n"
    text += "⭐ **کاربران VIP:** 100\n\n"
    text += "🔧 **مدیریت ربات:**\n"

    buttons = [
        [InlineKeyboardButton("➕ افزودن فیلم جدید", callback_data="add_movie")],
        [InlineKeyboardButton("🛑 حذف فیلم", callback_data="delete_movie")],
        [InlineKeyboardButton("👤 مدیریت کاربران", callback_data="manage_users")],
        [InlineKeyboardButton("📊 مشاهده آمار", callback_data="stats")],
    ]
    await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))

async def main():
    await bot.start()
    logging.info("✅ ربات با موفقیت اجرا شد!")
    await idle()
    await bot.stop()
    logging.info("❌ ربات متوقف شد.")

if __name__ == "__main__":
    asyncio.run(main())
