
async def auto_filter(client, name, msg, reply_msg, ai_search, spoll=False):
    results, _, total = await get_search_results(msg.chat.id, name)

    if not results:
        await msg.reply("❌ فیلم یا سریالی با این نام یافت نشد.")
        return

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

        if result['poster']:
            await msg.reply_photo(result['poster'], caption=text, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await msg.reply(text, reply_markup=InlineKeyboardMarkup(buttons))
