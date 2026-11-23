import os
import sys
import traceback

try:
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
except Exception:
    pass


def log(*args):
    print(*args, flush=True)


log("🚀 شروع برنامه...")

try:
    from rubpy.bot import BotClient, filters
    from rubpy.bot.models import Keypad, KeypadRow, Button, Update
    from rubpy.bot.enums import ButtonTypeEnum, ChatKeypadTypeEnum
except Exception:
    log("❌ خطا در ایمپورت rubpy:")
    traceback.print_exc()
    sys.exit(1)

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    log("❌ خطا: متغیر محیطی BOT_TOKEN تنظیم نشده است.")
    sys.exit(1)

app = BotClient(TOKEN, max_retries=10)


# ---------------------------------------------------------
# متن دکمه‌ها
# ---------------------------------------------------------
B_ONLINE = "اطلاع از جلسات آنلاین NA"
B_IRAN = "شورای فرامنطقه ایران"
B_APF = "شورای فرامنطقه APF"
B_EDM = "شورای فرامنطقه EDM"
B_GLOBAL = "ارتباط با کنفرانس خدمات جهانی NA"
B_BACK = "بازگشت به منوی اصلی"

# متن دکمه -> (عنوان، لینک)
SITES = {
    B_ONLINE: ("جلسات آنلاین NA", "https://nairan1.org/onlinemeeting/"),
    B_IRAN: ("سایت شورای فرامنطقه ایران", "https://nairan.org/"),
    B_APF: ("شورای فرامنطقه APF", "https://fa.apfna.org/"),
    B_EDM: ("شورای فرامنطقه EDM", "https://www.edmna.org/"),
}

# متن دکمه -> (عنوان، ایمیل)
EMAILS = {
    "اطلاعات عمومی و فلووشیپ": "fsmail@na.org",
    "خدمات مشتری (سفارشات)": "customer_service@na.org",
    "هیئت جهانی (World Board)": "worldboard@na.org",
    "منابع انسانی (HR)": "hrp@na.org",
    "روابط عمومی (PR)": "pr@na.org",
    "بیمارستان‌ها و موسسات (H&I)": "handi@na.org",
    "وب‌سایت (Webmaster)": "webmaster@na.org",
    "رویدادها و کنوانسیون‌ها": "events@na.org",
    "مجله The NA Way": "naway@na.org",
    "کمک‌های مالی": "contributions@na.org",
    "فرصت‌های شغلی": "jobs@na.org",
}

WELCOME_TEXT = (
    "به مرکز خدمات و منابع انجمن معتادان گمنام NA خوش آمدید.\n"
    "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"
)

EMAIL_TEXT = (
    "بخش‌های ارتباطی خدمات جهانی NA\n"
    "روی هر دکمه بزنید تا آدرس ایمیل آن بخش برای شما ارسال شود."
)


# ---------------------------------------------------------
# ساخت کیبورد چت
# ---------------------------------------------------------
_counter = [0]


def btn(text: str) -> Button:
    _counter[0] += 1
    return Button(id=f"b{_counter[0]}", type=ButtonTypeEnum.SIMPLE, button_text=text)


def main_keypad() -> Keypad:
    return Keypad(
        rows=[
            KeypadRow(buttons=[btn(B_ONLINE)]),
            KeypadRow(buttons=[btn(B_IRAN), btn(B_APF)]),
            KeypadRow(buttons=[btn(B_EDM)]),
            KeypadRow(buttons=[btn(B_GLOBAL)]),
        ],
        resize_keyboard=True,
    )


def email_keypad() -> Keypad:
    names = list(EMAILS.keys())
    rows = []
    for i in range(0, len(names), 2):
        rows.append(KeypadRow(buttons=[btn(n) for n in names[i:i + 2]]))
    rows.append(KeypadRow(buttons=[btn(B_BACK)]))
    return Keypad(rows=rows, resize_keyboard=True)


async def send(update: Update, text: str, keypad: Keypad = None):
    try:
        if keypad is not None:
            await update.reply(text, chat_keypad=keypad,
                               chat_keypad_type=ChatKeypadTypeEnum.NEW)
        else:
            await update.reply(text)
    except Exception as e:
        log("❌ خطا در ارسال پیام:", repr(e))
        traceback.print_exc()
        try:
            await update.reply(text)
        except Exception:
            traceback.print_exc()


# ---------------------------------------------------------
# هندلرها
# ---------------------------------------------------------
@app.on_update(filters.commands("start"))
async def start(client, update: Update):
    await send(update, WELCOME_TEXT, main_keypad())


# مسیریاب پیام‌های متنی (کلیک دکمه‌های کیبورد چت به‌صورت پیام متنی می‌رسد)
# باید آخرین هندلر باشد.
@app.on_update()
async def router(client, update: Update):
    try:
        msg = update.new_message
        text = (msg.text or "").strip() if msg else ""
    except Exception:
        return

    if not text or text.startswith("/"):
        return

    if text == B_GLOBAL:
        await send(update, EMAIL_TEXT, email_keypad())
    elif text == B_BACK:
        await send(update, WELCOME_TEXT, main_keypad())
    elif text in SITES:
        title, url = SITES[text]
        await send(update, f"{title}\n{url}")
    elif text in EMAILS:
        email = EMAILS[text]
        await send(
            update,
            f"{text}\n📧 {email}\n\n"
            f"نوشتن ایمیل (با جیمیل):\n"
            f"https://mail.google.com/mail/?view=cm&to={email}",
        )
    else:
        await send(update, WELCOME_TEXT, main_keypad())


# ---------------------------------------------------------
# اجرا (polling)
# ---------------------------------------------------------
if __name__ == "__main__":
    log("✅ ربات در حالت polling اجرا شد")
    try:
        app.run()
    except Exception:
        log("❌ خطا هنگام اجرای app.run:")
        traceback.print_exc()
        sys.exit(1)
