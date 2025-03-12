import re, os, json, base64, logging
from utils import temp
from pyrogram import filters, Client, enums
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, UsernameInvalid, UsernameNotModified
from info import ADMINS, LOG_CHANNEL, FILE_STORE_CHANNEL, PUBLIC_FILE_STORE
from database.ia_filterdb import unpack_new_file_id

# تنظیم سیستم لاگ‌گیری برای نمایش پیام‌های هنگام اجرا
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# بررسی اینکه آیا کاربر مجاز به استفاده از دستورات است یا خیر
async def allowed(_, __, message):
    if PUBLIC_FILE_STORE:
        return True
    if message.from_user and message.from_user.id in ADMINS:
        return True
    return False

# تابع تولید لینک برای یک فایل
@Client.on_message(filters.command(['link', 'plink']) & filters.create(allowed))
async def gen_link_s(bot, message):
    # دریافت فایل از کاربر
    vj = await bot.ask(chat_id=message.from_user.id, text="الان فایلی که می‌خوای ذخیره کنی رو بفرست.")
    file_type = vj.media

    # بررسی نوع فایل (فقط ویدیو، صدا، و فایل‌های مستند مجاز هستند)
    if file_type not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
        return await vj.reply("فقط ویدیو، فایل صوتی، یا مستند بفرست.")

    # بررسی اینکه آیا محتوای ارسال‌شده محافظت‌شده است یا خیر
    if message.has_protected_content and message.chat.id not in ADMINS:
        return await message.reply("❌ خطا: شما اجازه‌ی ارسال محتوای محافظت‌شده را ندارید.")

    # دریافت `file_id` از فایل
    try:
        file_id = unpack_new_file_id((getattr(vj, file_type.value)).file_id)
        print("🔍 خروجی بازگشایی شده:", file_id)  # نمایش مقدار در لاگ
    except Exception as e:
        return await message.reply(f"❌ خطا در `unpack_new_file_id`: {e}")

    # بررسی اینکه مقدار استخراج‌شده معتبر است یا خیر
    if not isinstance(file_id, str):
        return await message.reply("⚠️ خطا: مقدار باز شده نامعتبر است. لطفاً بررسی کنید.")

    # تولید لینک اختصاصی
    string = 'filep_' if message.text.lower().strip() == "/plink" else 'file_'
    string += file_id
    outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")

    await message.reply(f"✅ اینم لینکت:\nhttps://t.me/{temp.U_NAME}?start={outstr}")

# تابع تولید لینک برای چندین فایل (به‌صورت دسته‌ای)
@Client.on_message(filters.command(['batch', 'pbatch']) & filters.create(allowed))
async def gen_link_batch(bot, message):
    if " " not in message.text:
        return await message.reply("⚠️ فرمت صحیح را استفاده کن.\nمثال:\n`/batch https://t.me/VJ_Botz/10 https://t.me/VJ_Botz/20`")

    links = message.text.strip().split(" ")
    if len(links) != 3:
        return await message.reply("⚠️ فرمت صحیح را استفاده کن.\nمثال:\n`/batch https://t.me/VJ_Botz/10 https://t.me/VJ_Botz/20`")

    cmd, first, last = links
    regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")

    match = regex.match(first)
    if not match:
        return await message.reply('❌ لینک نامعتبره')
    f_chat_id = match.group(4)
    f_msg_id = int(match.group(5))
    if f_chat_id.isnumeric():
        f_chat_id  = int(("-100" + f_chat_id))

    match = regex.match(last)
    if not match:
        return await message.reply('❌ لینک نامعتبره')
    l_chat_id = match.group(4)
    l_msg_id = int(match.group(5))
    if l_chat_id.isnumeric():
        l_chat_id  = int(("-100" + l_chat_id))

    if f_chat_id != l_chat_id:
        return await message.reply("❌ خطا: چت آیدی‌ها یکی نیستند.")

    try:
        chat_id = (await bot.get_chat(f_chat_id)).id
    except ChannelInvalid:
        return await message.reply('❌ این چنل/گروه خصوصی به نظر میاد. باید ادمینم کنی.')
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('❌ لینک نامعتبره.')
    except Exception as e:
        return await message.reply(f'❌ خطا: {e}')

    sts = await message.reply("⏳ در حال تولید لینک... ممکنه کمی طول بکشه.")

    if chat_id in FILE_STORE_CHANNEL:
        string = f"{f_msg_id}_{l_msg_id}_{chat_id}_{cmd.lower().strip()}"
        b_64 = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
        return await sts.edit(f"✅ اینم لینکت: https://t.me/{temp.U_NAME}?start=DSTORE-{b_64}")

    outlist = []
    og_msg = 0
    tot = 0

    async for msg in bot.iter_messages(f_chat_id, l_msg_id, f_msg_id):
        tot += 1
        if msg.empty or msg.service:
            continue
        if not msg.media:
            continue

        try:
            file_type = msg.media
            file = getattr(msg, file_type.value)
            caption = getattr(msg, 'caption', '')
            if caption:
                caption = caption.html
            if file:
                file = {
                    "file_id": file.file_id,
                    "caption": caption,
                    "title": getattr(file, "file_name", ""),
                    "size": file.file_size,
                    "protect": cmd.lower().strip() == "/pbatch",
                }
                og_msg += 1
                outlist.append(file)
        except Exception as e:
            print(f"⚠️ خطا در پردازش پیام: {e}")

    with open(f"batchmode_{message.from_user.id}.json", "w+") as out:
        json.dump(outlist, out)

    post = await bot.send_document(LOG_CHANNEL, f"batchmode_{message.from_user.id}.json", file_name="Batch.json", caption="⚠️ این فایل برای ذخیره‌سازی تولید شد.")
    os.remove(f"batchmode_{message.from_user.id}.json")

    try:
        file_id = unpack_new_file_id(post.document.file_id)
    except Exception as e:
        return await sts.edit(f"❌ خطا در `unpack_new_file_id`: {e}")

    await sts.edit(f"✅ اینم لینکت\nشامل `{og_msg}` فایل:\nhttps://t.me/{temp.U_NAME}?start=BATCH-{file_id}")
