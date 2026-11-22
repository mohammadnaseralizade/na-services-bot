import os
import sys
import traceback

# خروجی بدون بافر تا لاگ هاست فوراً نمایش داده شود
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
    log("❌ خطا در ایمپورت rubpy (نصب یا نسخه را بررسی کنید):")
    traceback.print_exc()
    sys.exit(1)

# ButtonLink در بعضی نسخه‌ها وجود دارد (برای دکمه‌های لینک)
try:
    from rubpy.bot.models import ButtonLink
except Exception:
    ButtonLink = None

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not TOKEN or not WEBHOOK_URL:
    log("❌ خطا: متغیرهای محیطی BOT_TOKEN و WEBHOOK_URL تنظیم نشده‌اند.")
    sys.exit(1)

app = BotClient(TOKEN, max_retries=10)


# ---------------------------------------------------------
# توابع کمکی برای ساخت دکمه
# ---------------------------------------------------------
def link_button(btn_id: str, text: str, url: str) -> Button:
    """دکمه لینک (فقط http/https)"""
    if ButtonLink is not None:
        return Button(
            id=btn_id,
            type="Link",
            button_text=text,
            button_link=ButtonLink(type="url", link_url=url),
        )
    # fallback برای نسخه‌هایی که ساختار متفاوتی دارند
    return Button(id=btn_id, type="Link", button_text=text, url=url)


def simple_button(btn_id: str, text: str) -> Button:
    """دکمه معمولی که کلیکش آپدیت به ربات می‌فرستد"""
    return Button(id=btn_id, type="Simple", button_text=text)


# ---------------------------------------------------------
# منوها
# ---------------------------------------------------------
def main_menu() -> Keypad:
    return Keypad(
        rows=[
            KeypadRow(buttons=[
                link_button("online", "اطلاع از جلسات آنلاین NA",
                            "https://nairan1.org/onlinemeeting/")
            ]),
            KeypadRow(buttons=[
                link_button("iran", "سایت شورای فرامنطقه ایران", "https://nairan.org/"),
                link_button("apf", "شورای فرامنطقه APF", "https://fa.apfna.org/"),
            ]),
            KeypadRow(buttons=[
                link_button("edm", "شورای فرامنطقه EDM", "https://www.edmna.org/")
            ]),
            KeypadRow(buttons=[
                simple_button("global_services", "ارتباط با کنفرانس خدمات جهانی NA")
            ]),
        ],
        resize_keyboard=True,
    )


# ایمیل‌ها: (id, متن دکمه, آدرس ایمیل)
# چون روبیکا لینک mailto را معمولاً نمی‌پذیرد، با کلیک، آدرس ایمیل ارسال می‌شود.
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
    # دو دکمه در هر ردیف
    for i in range(0, len(EMAIL_ITEMS), 2):
        chunk = EMAIL_ITEMS[i:i + 2]
        rows.append(KeypadRow(buttons=[
            simple_button(f"mail_{b_id}", text) for b_id, text, _ in chunk
        ]))
    rows.append(KeypadRow(buttons=[simple_button("shop", "فروشگاه آنلاین (پرداخت)")]))
    rows.append(KeypadRow(buttons=[simple_button("back_to_main", "بازگشت به منوی اصلی")]))
    return Keypad(rows=rows, resize_keyboard=True)


WELCOME_TEXT = (
    "به مرکز خدمات و منابع انجمن معتادان گمنام NA خوش آمدید.\n"
    "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"
)


# ---------------------------------------------------------
# هندلرها
# ---------------------------------------------------------
@app.on_update(filters.commands("start"))
async def start(client, update: Update):
    try:
        await update.reply(WELCOME_TEXT, inline_keypad=main_menu())
    except Exception:
        traceback.print_exc()


@app.on_update(filters.button("global_services"))
async def global_services(client, update: Update):
    try:
        text = (
            "بخش‌های ارتباطی خدمات جهانی NA\n"
            "روی هر دکمه بزنید تا آدرس ایمیل آن بخش برای شما ارسال شود."
        )
        await update.reply(text, inline_keypad=email_menu())
    except Exception:
        traceback.print_exc()


def make_email_handler(btn_id: str, title: str, email: str):
    @app.on_update(filters.button(f"mail_{btn_id}"))
    async def handler(client, update: Update):
        try:
            await update.reply(f"{title}\n📧 {email}")
        except Exception:
            traceback.print_exc()
    return handler


for _id, _title, _email in EMAIL_ITEMS:
    make_email_handler(_id, _title, _email)


@app.on_update(filters.button("shop"))
async def shop(client, update: Update):
    try:
        await update.reply("فروشگاه آنلاین (پرداخت):\nhttps://asan.shaparak.ir/")
    except Exception:
        traceback.print_exc()


@app.on_update(filters.button("back_to_main"))
async def back_to_main(client, update: Update):
    try:
        await update.reply(WELCOME_TEXT, inline_keypad=main_menu())
    except Exception:
        traceback.print_exc()


# ---------------------------------------------------------
# اجرا (وبهوک)
# ---------------------------------------------------------
if __name__ == "__main__":
    log("✅ ربات در حالت polling اجرا شد")
    try:
        app.run()
    except Exception:
        log("❌ خطا هنگام اجرای app.run:")
        traceback.print_exc()
        sys.exit(1)
