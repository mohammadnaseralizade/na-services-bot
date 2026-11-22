import os
from rubpy.bot import BotClient, filters
from rubpy.bot.models import Keypad, KeypadRow, Button, Update

# ⚠️ توکن ربات و آدرس وبهوک را از متغیرهای محیطی می‌خوانیم
# هرگز توکن را داخل کد ننویسید!
TOKEN = os.getenv("CJGHBB0DTAERTQQLKDBNELIGTYHNGIOWHPSPZUCLOVQKPQLIGKSIBSQBUUQOABZR")
WEBHOOK_URL = os.getenv("https://na-bot-478038e06ee7.sam.apps.haiocloud.com/webhook")

if not TOKEN or not WEBHOOK_URL:
    print("❌ خطا: متغیرهای محیطی BOT_TOKEN و WEBHOOK_URL تنظیم نشده‌اند.")
    exit(1)

app = BotClient(TOKEN, max_retries=10)

# ---------------------------------------------------------
# ۱. منوی اصلی (شروع ربات)
# ---------------------------------------------------------
@app.on_update(filters.commands("start"))
async def start(client, update: Update):
    keypad = Keypad(
        rows=[
            KeypadRow(buttons=[Button(id="online", button_text="اطلاع از جلسات آنلاین NA", type="link", url="https://nairan1.org/onlinemeeting/")]),
            KeypadRow(buttons=[
                Button(id="iran", button_text="سایت شورای فرامنطقه ایران", type="link", url="https://nairan.org/"),
                Button(id="apf", button_text="شورای فرامنطقه APF", type="link", url="https://fa.apfna.org/")
            ]),
            KeypadRow(buttons=[Button(id="edm", button_text="شورای فرامنطقه EDM", type="link", url="https://www.edmna.org/")]),
            KeypadRow(buttons=[Button(id="global_services", button_text="ارتباط با کنفرانس خدمات جهانی NA")])
        ],
        resize_keyboard=True
    )

    welcome_text = "به مرکز خدمات و منابع انجمن معتادان گمنام NA خوش آمدید.\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:"
    await update.reply(welcome_text, inline_keypad=keypad)

# ---------------------------------------------------------
# ۲. مدیریت کلیک روی دکمه‌ها
# ---------------------------------------------------------
@app.on_update(filters.button("global_services"))
async def global_services(client, update: Update):
    email_keypad = Keypad(
        rows=[
            KeypadRow(buttons=[Button(id="fsmail", button_text="اطلاعات عمومی و فلووشیپ", type="link", url="mailto:fsmail@na.org")]),
            KeypadRow(buttons=[
                Button(id="cust", button_text="خدمات مشتری (سفارشات)", type="link", url="mailto:customer_service@na.org"),
                Button(id="shop", button_text="فروشگاه آنلاین (پرداخت)", type="link", url="https://asan.shaparak.ir/")
            ]),
            KeypadRow(buttons=[Button(id="wb", button_text="هیئت جهانی (World Board)", type="link", url="mailto:worldboard@na.org")]),
            KeypadRow(buttons=[
                Button(id="hr", button_text="منابع انسانی (HR)", type="link", url="mailto:hrp@na.org"),
                Button(id="pr", button_text="روابط عمومی (PR)", type="link", url="mailto:pr@na.org")
            ]),
            KeypadRow(buttons=[
                Button(id="handi", button_text="بیمارستان‌ها و موسسات (H&I)", type="link", url="mailto:handi@na.org"),
                Button(id="web", button_text="وب‌سایت (Webmaster)", type="link", url="mailto:webmaster@na.org")
            ]),
            KeypadRow(buttons=[
                Button(id="events", button_text="رویدادها و کنوانسیون‌ها", type="link", url="mailto:events@na.org"),
                Button(id="naway", button_text="مجله The NA Way", type="link", url="mailto:naway@na.org")
            ]),
            KeypadRow(buttons=[
                Button(id="contrib", button_text="کمک‌های مالی", type="link", url="mailto:contributions@na.org"),
                Button(id="jobs", button_text="فرصت‌های شغلی", type="link", url="mailto:jobs@na.org")
            ]),
            KeypadRow(buttons=[Button(id="back_to_main", button_text="بازگشت به منوی اصلی")])
        ],
        resize_keyboard=True
    )
    
    email_text = "بخش‌های ارتباطی خدمات جهانی NA\nبا کلیک روی هر دکمه، اپلیکیشن ایمیل گوشی شما باز خواهد شد."
    await update.reply(email_text, inline_keypad=email_keypad)

@app.on_update(filters.button("back_to_main"))
async def back_to_main(client, update: Update):
    # به جای صدا زدن تابع start، یک پیام ساده برای راهنمایی می‌فرستیم که کاربر دوباره /start بزند
    # یا می‌توانید دقیقاً همان کیپد اصلی را دوباره اینجا بسازید.
    await update.reply("برای مشاهده مجدد منوی اصلی، لطفاً دستور /start را ارسال کنید.")

# ---------------------------------------------------------
# ۳. اجرای ربات (فقط یک بار و در حالت وبهوک)
# ---------------------------------------------------------
if __name__ == "__main__":
    print("✅ ربات با موفقیت در حالت وبهوک اجرا شد.")
    
    # خواندن پورت از متغیرهای محیطی (هاست‌های ابری معمولاً پورت را خودشان تعیین می‌کنند)
    PORT = int(os.getenv("PORT", 8080))
    
    # اجرای ربات فقط با یک دستور
    app.run(webhook_url=WEBHOOK_URL, path="/webhook", host="0.0.0.0", port=PORT)