import psutil
import pyautogui
import os
import time
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- الإعدادات (تأكد من صحة البيانات) ---
TOKEN = 'YOUR_TOKEN_HERE'
ADMIN_ID = 'YOUR_ID_FROM_YOUR_BOT'  # الـ ID الخاص بك الذي ظهر في شاشتك

# ذاكرة مؤقتة لتخزين الأجهزة المتصلة
users_sessions = {}

# --- دالة الحماية ---
def is_admin(update: Update):
    return update.effective_user.id == ADMIN_ID

# --- الدوال الأساسية ---

# 1. الترحيب والتعرف على المستخدم
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users_sessions[user.id] = {
        "name": user.full_name,
        "username": user.username,
        "join_time": datetime.datetime.now().strftime("%H:%M:%S")
    }
    
    welcome = (f"🚀 أهلاً بك في 'Engineer Control Panel' يا {user.first_name}!\n"
               f"معرف جهازك هو: `{user.id}`\n\n")
    
    if is_admin(update):
        welcome += "✅ **وضع المطور (Admin):** كامل الصلاحيات متاحة لك الآن."
    else:
        welcome += "⚠️ **وضع الضيف:** تم تسجيلك، لكن الأوامر الحساسة للمطور فقط."
        
    await update.message.reply_text(welcome, parse_mode='Markdown')
    print(f"👤 مستخدم جديد: {user.full_name} | ID: {user.id}")

# 2. فحص أداء النظام
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔️ عذراً، الوصول لبيانات النظام متاح للمطور فقط.")
        return

    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('C:\\')
    
    report = (
        f"🖥 **تقرير أداء الكمبيوتر:**\n\n"
        f"⚙️ المعالج: {cpu}%\n"
        f"🧠 الرام: {ram.percent}% (المتوفر: {ram.available // (1024**2)} MB)\n"
        f"💾 القرص (C): {disk.percent}% مستخدم\n"
        f"🌡 الحالة: {'ضغط عالي 🔥' if cpu > 85 else 'مستقر ✅'}"
    )
    await update.message.reply_text(report, parse_mode='Markdown')

# 3. تصوير الشاشة (Screenshot)
async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return

    await update.message.reply_text("📸 جاري التقاط الصورة...")
    try:
        path = "current_screen.png"
        pyautogui.screenshot(path)
        with open(path, 'rb') as photo:
            await update.message.reply_photo(photo=photo, caption="🖼 لقطة حية لسطح المكتب")
        os.remove(path)
    except Exception as e:
        await update.message.reply_text(f"❌ فشل التصوير: {e}")

# 4. جلب ملف من الكمبيوتر
async def get_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return
    
    file_path = " ".join(context.args).replace('"', '') # تنظيف المسار من علامات التنصيص
    if not file_path:
        await update.message.reply_text("❓ يرجى إرسال مسار الملف.\nمثال: `/file C:\\Users\\Desktop\\test.txt`", parse_mode='Markdown')
        return

    if os.path.exists(file_path):
        await update.message.reply_text("📂 جاري جلب الملف...")
        try:
            with open(file_path, 'rb') as doc:
                await update.message.reply_document(doc)
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ أثناء الرفع: {e}")
    else:
        await update.message.reply_text("⚠️ الملف غير موجود، تأكد من صحة المسار.")

# --- تشغيل التطبيق ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('status', status))
    app.add_handler(CommandHandler('screen', screenshot))
    app.add_handler(CommandHandler('file', get_file))
    
    print("🤖 البوت يعمل الآن باسم 'Engineer Control Panel'..")
    app.run_polling()