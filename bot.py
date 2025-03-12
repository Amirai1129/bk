from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
import os
from info import API_ID, API_HASH, BOT_TOKEN, ADMINS

# مقداردهی `Client`
bot = Client(
    "my_bot",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# اطمینان از اینکه ADMINS لیست عددی است
if isinstance(ADMINS, str):
    ADMINS = list(map(int, ADMINS.split()))
elif isinstance(ADMINS, (list, tuple)):
    ADMINS = list(map(int, ADMINS))
else:
    ADMINS = []

@bot.on_inline_query()
async def inline_query_handler(client, query):
    search = query.query.strip()
    if not search:
        await query.answer([], cache_time=0)
        return

    results, _, total = await get_search_results(query.from_user.id, search)
    if not results:
        await query.answer([], cache_time=0)
        return

    inline_results = []
    for result in results:
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
            [InlineKeyboardButton("📺 مشاهده فصل‌ها", callback_data=f"seasons#{result['file_id']}")],
            [InlineKeyboardButton("📁 مشاهده کیفیت‌ها", callback_data=f"qualities#{result['file_id']}")],
            [InlineKeyboardButton("🌍 انتخاب زبان", callback_data=f"languages#{result['file_id']}")],
            [InlineKeyboardButton("📆 انتخاب سال انتشار", callback_data=f"year#{result['file_id']}")],
            [InlineKeyboardButton("🎭 انتخاب ژانر", callback_data=f"genre#{result['file_id']}")],
            [InlineKeyboardButton("📜 دریافت زیرنویس", callback_data=f"subtitles#{result['file_id']}")],
            [InlineKeyboardButton("🎤 دریافت نسخه دوبله", callback_data=f"dubbing#{result['file_id']}")],
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

    await query.answer(inline_results, cache_time=0)

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

if __name__ == "__main__":
    bot.run()
