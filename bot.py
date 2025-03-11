from pyrogram import Client, filters
from info import ADMINS

@Client.on_inline_query()
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
        text = f"🎬 **{result['file_name']}**\n"
        text += f"📅 **سال انتشار:** {result['year']}\n"
        text += f"⭐ **امتیاز IMDb:** {result['rating']}\n"
        text += f"🎭 **ژانر:** {result['genre']}\n"
        text += f"🎬 **کارگردان:** {result['director']}\n"
        text += f"👥 **بازیگران:** {result['actors']}\n\n"
        text += f"📝 **خلاصه:** {result['summary']}\n\n"
        text += f"📂 **حجم فایل:** {result['file_size']}\n"
        if result['imdb_link']:
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
            thumb_url=result['poster'] if result['poster'] else None
        )

        inline_results.append(inline_result)
    
    await query.answer(inline_results, cache_time=0)


# کد مربوط به پنل مدیریت حرفه‌ای ربات
@Client.on_message(filters.command("admin") & filters.user(ADMINS))
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


# کد مربوط به استریم آنلاین فیلم در ربات
@Client.on_message(filters.regex(r"^🎥 تماشای آنلاین") & filters.private)
async def stream_movie(client, message):
    movie_id = message.text.split("#")[1]
    movie_info = await get_movie_details(movie_id)

    if not movie_info.get("stream_link"):
        await message.reply("❌ این فیلم قابلیت پخش آنلاین ندارد.")
        return

    text = f"🎬 **{movie_info['title']}**\n\n"
    text += f"🎥 **پخش آنلاین:** [تماشا کنید]({movie_info['stream_link']})"

    await message.reply(text, disable_web_page_preview=False)


# کد مربوط به مدیریت کاربران VIP
@Client.on_message(filters.command("vip") & filters.user(ADMINS))
async def manage_vip(client, message):
    text = "⭐ **مدیریت کاربران VIP**\n\n"
    text += "🔹 افزودن یا حذف کاربران VIP\n"
    
    buttons = [
        [InlineKeyboardButton("➕ افزودن کاربر VIP", callback_data="add_vip")],
        [InlineKeyboardButton("🛑 حذف کاربر VIP", callback_data="remove_vip")],
        [InlineKeyboardButton("🔍 بررسی وضعیت VIP", callback_data="check_vip")],
    ]

    await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))
