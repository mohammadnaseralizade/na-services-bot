from robka import Robot
from robka.button import InlineBuilder

# ⚠️ توکن خود را اینجا قرار دهید
TOKEN = "CJGHBB0DTAERTQQLKDBNELIGTYHNGIOWHPSPZUCLOVQKPQLIGKSIBSQBUUQOABZR"
# آدرس وبهوک بعدا اینجا قرار می‌گیرد
WEBHOOK_URL ="https://na-bot-478038e06ee7.sam.apps.haiocloud.com/webhook"

bot = Robot(TOKEN)

# ---------------------------------------------------------
# ۱. منوی اصلی (شروع ربات)
# ---------------------------------------------------------
@bot.on_message(commands=["start"])
def start(bot, message):
    builder = InlineBuilder().row(
        InlineBuilder().button_link(id="online", title="اطلاع از جلسات آنلاین NA", url="https://nairan1.org/onlinemeeting/")
    ).row(
        InlineBuilder().button_link(id="iran", title="سایت شورای فرامنطقه ایران", url="https://nairan.org/"),
        InlineBuilder().button_link(id="apf", title="شورای فرامنطقه APF", url="https://fa.apfna.org/")
    ).row(
        InlineBuilder().button_link(id="edm", title="شورای فرامنطقه EDM", url="https://www.edmna.org/")
    ).row(
        InlineBuilder().button_simple(id="global_services", text="ارتباط با کنفرانس خدمات جهانی NA")
    ).build()
    
    welcome_text = "به مرکز خدمات و منابع انجمن معتادان گمنام NA خوش آمدید.\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:"
    message.reply(welcome_text, inline_keypad=builder)

# ---------------------------------------------------------
# ۲. مدیریت کلیک روی دکمه‌ها
# ---------------------------------------------------------
@bot.on_callback("global_services")
def global_services(bot, message):
    email_builder = InlineBuilder().row(
        InlineBuilder().button_link(id="fsmail", title="اطلاعات عمومی و فلووشیپ", url="mailto:fsmail@na.org")
    ).row(
        InlineBuilder().button_link(id="cust", title="خدمات مشتری (سفارشات)", url="mailto:customer_service@na.org"),
        InlineBuilder().button_link(id="shop", title="فروشگاه آنلاین (پرداخت)", url="https://asan.shaparak.ir/")
    ).row(
        InlineBuilder().button_link(id="wb", title="هیئت جهانی (World Board)", url="mailto:worldboard@na.org")
    ).row(
        InlineBuilder().button_link(id="hr", title="منابع انسانی (HR)", url="mailto:hrp@na.org"),
        InlineBuilder().button_link(id="pr", title="روابط عمومی (PR)", url="mailto:pr@na.org")
    ).row(
        InlineBuilder().button_link(id="handi", title="بیمارستان‌ها و موسسات (H&I)", url="mailto:handi@na.org"),
        InlineBuilder().button_link(id="web", title="وب‌سایت (Webmaster)", url="mailto:webmaster@na.org")
    ).row(
        InlineBuilder().button_link(id="events", title="رویدادها و کنوانسیون‌ها", url="mailto:events@na.org"),
        InlineBuilder().button_link(id="naway", title="مجله The NA Way", url="mailto:naway@na.org")
    ).row(
        InlineBuilder().button_link(id="contrib", title="کمک‌های مالی", url="mailto:contributions@na.org"),
        InlineBuilder().button_link(id="jobs", title="فرصت‌های شغلی", url="mailto:jobs@na.org")
    ).row(
        InlineBuilder().button_simple(id="back_to_main", text="بازگشت به منوی اصلی")
    ).build()
    
    email_text = "بخش‌های ارتباطی خدمات جهانی NA\nبا کلیک روی هر دکمه، اپلیکیشن ایمیل گوشی شما باز خواهد شد."
    message.reply(email_text, inline_keypad=email_builder)

@bot.on_callback("back_to_main")
def back_to_main(bot, message):
    start(bot, message)

# ---------------------------------------------------------
# ۳. تنظیم وبهوک و اجرای نهایی
# ---------------------------------------------------------
# ثبت آدرس وبهوک
bot.update_bot_endpoint(WEBHOOK_URL, "webhook")

print("✅ ربات با موفقیت در حالت وبهوک اجرا شد.")
bot.run()