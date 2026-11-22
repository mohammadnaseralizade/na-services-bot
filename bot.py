import os
import sys
import inspect
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
except Exception:
    log("❌ خطا در ایمپورت rubpy:")
    traceback.print_exc()
    sys.exit(1)

try:
    from rubpy.bot.models import ButtonLink
except Exception:
    ButtonLink = None

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    log("❌ خطا: متغیر محیطی BOT_TOKEN تنظیم نشده است.")
    sys.exit(1)

# اطلاعات تشخیصی: امضای واقعی کلاس‌ها در نسخه نصب‌شده
try:
    log("ℹ️ Button:", inspect.signature(Button.__init__))
    if ButtonLink is not None:
        log("ℹ️ ButtonLink:", inspect.signature(ButtonLink.__init__))
    else:
        log("ℹ️ ButtonLink وجود ندارد")
    log("ℹ️ Keypad:", inspect.signature(Keypad.__init__))
except Exception:
    pass

app = BotClient(TOKEN, max_retries=10)


# ---------------------------------------------------------
# ساخت دکمه
# ---------------------------------------------------------
def link_button(btn_id: str, text: str, url: str) -> Button:
    """دکمه لینک؛ چند حالت ممکن را امتحان می‌کند تا یکی بسازد."""
    attempts = []
    if ButtonLink is not None:
        attempts.append(lambda: Button(
            id=btn_id, type="Link", button_text=text,
            button_link=ButtonLink(type="url", link_url=url)))
    attempts.append(lambda: Button(id=btn_id, type="Link", button_text=text, link_url=url))
    attempts.append(lambda: Button(id=btn_id, type="Link", button_text=text, url=url))

    last_err = None
    for make in attempts:
        try:
            return make()
        except Exception as e:
            last_err = e
    log("❌ ساخت دکمه لینک ممکن نشد:", last_err)
    # آخرین راه: دکمه ساده که لینک را در پیام می‌فرستد
    return Button(id=f"url_{btn_id}", button_text=text)


def simple_button(btn_id: str, text: str) -> Button:
    return Button(id=btn_id, button_text=text)


# لینک‌ها: id -> (متن، آدرس)؛ برای حالت جایگزین (ارسال لینک در پیام)
LINKS = {}


def L(btn_id, text, url):
    LINKS[f"url_{btn_id}"] = (text, url)
    return link_button(btn_id, text, url)


# ---------------------------------------------------------
# منوها (بدون resize_keyboard چون برای inline مجاز نیست)
# ---------------------------------------------------------
def main_menu() -> Keypad:
    return Keypad(rows=[
        KeypadRow(buttons=[
            L("online", "اطلاع از جلسات آنلاین NA", "https://nairan1.org/onlinemeeting/")
        ]),
        KeypadRow(buttons=[
            L("iran", "سایت شورای فرامنطقه ایران", "https://nairan.org/"),
            L("apf", "شورای فرامنطقه APF", "https://fa.apfna.org/"),
        ]),
        KeypadRow(buttons=[
            L("edm", "شورای فرامنطقه EDM", "https://www.edmna.org/")
        ]),
        KeypadRow(buttons=[
            simple_button("global_services", "ارتباط با کنفرانس خدمات جهانی NA")
        ]),
    ])


EMAIL_ITEMS = [
    ("fsmail", "اطلاعات عمومی و فلووشیپ", "fsmail@na.org"),
    ("cust", "خدمات مشتری (سفارشات)", "customer_service@na.org"),
    ("wb", "هیئت جهانی (World Board)", "worldboard@na.org"),
    ("hr", "منابع انسانی (HR)", "hrp@na.org"),
    ("pr", "روابط عمومی (PR)", "pr@na.org"),
    ("handi", "بیمارستان‌ها و موسسات (H&I)", "handi@na.org"),
    ("web", "وب‌سایت (Webmaster)", "webmaster@na.org"),
    ("events", "رویدادها و کنوانسیون‌ها", "events@na.org"),
    ("naway", "مجله The NA Way", "naway@na.org"),
    ("contrib", "کمک‌های مالی", "contributions@na.org"),
    ("jobs", "فرصت‌های شغلی", "jobs@na.org"),
]


def email_menu() -> Keypad:
    rows = []
    for i in range(0, len(EMAIL_ITEMS), 2):
        chunk = EMAIL_ITEMS[i:i + 2]
        rows.append(KeypadRow(buttons=[
            simple_button(f"mail_{b_id}", text) for b_id, text, _ in chunk
        ]))
    rows.append(KeypadRow(buttons=[simple_button("shop", "فروشگاه آنلاین (پرداخت)")]))
    rows.append(KeypadRow(buttons=[simple_button("back_to_main", "بازگشت به منوی اصلی")]))
    return Keypad(rows=rows)


WELCOME_TEXT = (
    "به مرکز خدمات و منابع انجمن معتادان گمنام NA خوش آمدید.\n"
    "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"
)


# ---------------------------------------------------------
# هندلرها
# ---------------------------------------------------------
async def safe_reply(update, text, keypad=None):
    """اگر ارسال با دکمه خطا داد، خطا را کامل چاپ می‌کند و متن ساده می‌فرستد."""
    try:
        if keypad is not None:
            await update.reply(text, inline_keypad=keypad)
        else:
            await update.reply(text)
    except Exception as e:
        log("❌ خطا در ارسال پیام با دکمه:", repr(e))
        traceback.print_exc()
        try:
            await update.reply(text)
        except Exception:
            traceback.print_exc()


@app.on_update(filters.commands("start"))
async def start(client, update: Update):
    await safe_reply(update, WELCOME_TEXT, main_menu())


@app.on_update(filters.button("global_services"))
async def global_services(client, update: Update):
    text = (
        "بخش‌های ارتباطی خدمات جهانی NA\n"
        "روی هر دکمه بزنید تا آدرس ایمیل آن بخش برای شما ارسال شود."
    )
    await safe_reply(update, text, email_menu())


def make_email_handler(btn_id, title, email):
    @app.on_update(filters.button(f"mail_{btn_id}"))
    async def handler(client, update: Update):
        await safe_reply(update, f"{title}\n📧 {email}")
    return handler


for _id, _title, _email in EMAIL_ITEMS:
    make_email_handler(_id, _title, _email)


def make_url_handler(btn_id, title, url):
    @app.on_update(filters.button(btn_id))
    async def handler(client, update: Update):
        await safe_reply(update, f"{title}\n{url}")
    return handler


for _bid, (_t, _u) in list(LINKS.items()):
    make_url_handler(_bid, _t, _u)


@app.on_update(filters.button("shop"))
async def shop(client, update: Update):
    await safe_reply(update, "فروشگاه آنلاین (پرداخت):\nhttps://asan.shaparak.ir/")


@app.on_update(filters.button("back_to_main"))
async def back_to_main(client, update: Update):
    await safe_reply(update, WELCOME_TEXT, main_menu())


# ---------------------------------------------------------
# اجرا (polling)
# ---------------------------------------------------------
@app.on_update(filters.commands("test"))
async def test_buttons(client, update: Update):
    results = []
    tests = {
        "simple": lambda: Keypad(rows=[KeypadRow(buttons=[
            Button(id="t1", button_text="تست", type="Simple")])]),
        "simple_notype": lambda: Keypad(rows=[KeypadRow(buttons=[
            Button(id="t2", button_text="تست")])]),
        "link": lambda: Keypad(rows=[KeypadRow(buttons=[
            link_button("t3", "لینک", "https://nairan.org/")])]),
    }
    for name, make in tests.items():
        try:
            await update.reply("تست " + name, inline_keypad=make())
            results.append(name + ": OK")
        except Exception as e:
            results.append(name + ": FAIL " + repr(e))
    await update.reply("\n".join(results))
if __name__ == "__main__":
    log("✅ ربات در حالت polling اجرا شد")
    try:
        app.run()
    except Exception:
        log("❌ خطا هنگام اجرای app.run:")
        traceback.print_exc()
        sys.exit(1)
