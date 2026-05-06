from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from config import CHANNEL_URL

def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🛍️ មើលកញ្ចប់ (Products)")
    builder.button(text="❓ របៀបទិញ (How to buy)")
    builder.button(text="ℹ️ អំពីយើង (About)")
    builder.button(text="📢 ឆានែលរបស់យើង (Our Channel)")
    builder.button(text="📞 ទំនាក់ទំនង Admin")
    builder.adjust(2, 2, 1)
    return builder.as_markup(resize_keyboard=True)

def get_back_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 ត្រឡប់ក្រោយ", callback_data="start_menu")
    return builder.as_markup()

def get_products_keyboard(products):
    builder = InlineKeyboardBuilder()
    for prod in products:
        # prod is (id, name, description, price, image_url, stock)
        stock_text = f" (ស្តុក: {prod[5]})" if prod[5] >= 0 else ""
        if prod[5] == 0:
            builder.button(text=f"❌ អស់ស្តុក - {prod[1]}", callback_data=f"buy_{prod[0]}")
        else:
            builder.button(text=f"{prod[1]} - {prod[3]}{stock_text}", callback_data=f"buy_{prod[0]}")
    builder.button(text="🔙 ត្រឡប់ក្រោយ", callback_data="start_menu")
    builder.adjust(1)
    return builder.as_markup()

def get_payment_keyboard(order_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ ខ្ញុំបានបង់ប្រាក់រួច (Upload Receipt)", callback_data=f"paid_{order_id}")
    builder.button(text="❌ បោះបង់ (Cancel)", callback_data="start_menu")
    builder.adjust(1)
    return builder.as_markup()

def get_admin_approval_keyboard(order_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ ទទួលយក (Approve)", callback_data=f"admin_approve_{order_id}")
    builder.button(text="❌ បដិសេធ (Reject)", callback_data=f"admin_reject_{order_id}")
    builder.adjust(2)
    return builder.as_markup()

def get_admin_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="➕ បន្ថែមផលិតផលថ្មី (Add Product)")
    builder.button(text="✏️ កែប្រែតម្លៃ (Edit Price)")
    builder.button(text="🏷️ កែប្រែឈ្មោះ (Rename Product)")
    builder.button(text="🖼️ ដាក់រូបភាព (Set Picture)")
    builder.button(text="📦 បន្ថែមស្តុក (Add Stock)")
    builder.button(text="Delete Product")
    builder.button(text="Notify Customers")
    builder.button(text="👥 ស្ថិតិអ្នកប្រើ (Bot Stats)")
    builder.button(text="👑 គ្រប់គ្រង Admin")
    builder.adjust(2, 2, 2, 2, 1)
    return builder.as_markup(resize_keyboard=True)

def get_admin_products_keyboard(products, action_prefix):
    builder = InlineKeyboardBuilder()
    for prod in products:
        builder.button(text=f"{prod[1]}", callback_data=f"{action_prefix}_{prod[0]}")
    builder.button(text="🔙 ត្រឡប់ក្រោយ", callback_data="admin_main_menu")
    builder.adjust(1)
    return builder.as_markup()

def get_delete_product_confirm_keyboard(product_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="Confirm Delete", callback_data=f"admin_confirm_delete_{product_id}")
    builder.button(text="Cancel", callback_data="admin_main_menu")
    builder.adjust(1)
    return builder.as_markup()

def get_admin_list_keyboard(admins, main_admin_id):
    """Keyboard showing all admins with remove buttons."""
    builder = InlineKeyboardBuilder()
    for admin in admins:
        uid, uname, added_at = admin
        label = f"@{uname}" if uname else f"ID: {uid}"
        builder.button(text=f"❌ លុប {label}", callback_data=f"admin_remove_{uid}")
    builder.button(text="➕ បន្ថែម Admin ថ្មី", callback_data="admin_add_new")
    builder.button(text="🔙 ត្រឡប់", callback_data="admin_main_menu")
    builder.adjust(1)
    return builder.as_markup()

def get_cancel_admin_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ បោះបង់", callback_data="admin_main_menu")
    return builder.as_markup()

