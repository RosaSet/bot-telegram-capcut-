from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
import keyboards as kb
from config import ADMIN_ID

router = Router()

class AdminState(StatesGroup):
    add_name = State()
    add_desc = State()
    add_price = State()
    add_image = State()
    add_stock = State()
    
    edit_price = State()
    edit_image = State()
    edit_stock = State()
    notify_customers = State()
    
    send_account = State()

@router.message(F.text == "/admin")
async def cmd_admin(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.clear()
    await message.answer("🛠 **Admin Dashboard**", reply_markup=kb.get_admin_main_menu())

@router.callback_query(F.data == "admin_main_menu")
async def admin_main_menu(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.clear()
    await callback.message.delete()
    await callback.answer()

# --- Add Product ---
@router.message(F.text == "➕ បន្ថែមផលិតផលថ្មី (Add Product)")
async def admin_add_product(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    await message.answer("សូមវាយឈ្មោះផលិតផលថ្មី៖")
    await state.set_state(AdminState.add_name)

@router.message(AdminState.add_name)
async def process_add_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("សូមវាយការពិពណ៌នា (Description) របស់ផលិតផល៖")
    await state.set_state(AdminState.add_desc)

@router.message(AdminState.add_desc)
async def process_add_desc(message: Message, state: FSMContext):
    await state.update_data(desc=message.text)
    await message.answer("សូមវាយតម្លៃផលិតផល (ឧទាហរណ៍៖ $5.00)៖")
    await state.set_state(AdminState.add_price)

@router.message(AdminState.add_price)
async def process_add_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer("សូមផ្ញើ Link រូបភាព (ឬវាយ 'skip' ដើម្បីរំលង)៖")
    await state.set_state(AdminState.add_image)

@router.message(AdminState.add_image)
async def process_add_image(message: Message, state: FSMContext):
    img = message.text if message.text.lower() != 'skip' else ''
    await state.update_data(image=img)
    await message.answer("តើមានស្តុកប៉ុន្មាន? (វាយ -1 សម្រាប់ស្តុកគ្មានកំណត់)៖")
    await state.set_state(AdminState.add_stock)

@router.message(AdminState.add_stock)
async def process_add_stock(message: Message, state: FSMContext):
    try:
        stock = int(message.text)
        data = await state.get_data()
        db.add_product(data['name'], data['desc'], data['price'], data['image'], stock)
        await message.answer("✅ ផលិតផលត្រូវបានបន្ថែមជោគជ័យ!", reply_markup=kb.get_admin_main_menu())
        await state.clear()
    except ValueError:
        await message.answer("សូមវាយជាលេខ។ ឧទាហរណ៍៖ 10 ឬ -1")

# --- Edit Price ---
@router.message(F.text == "✏️ កែប្រែតម្លៃ (Edit Price)")
async def admin_edit_price_menu(message: Message):
    if message.from_user.id != ADMIN_ID: return
    products = db.get_products()
    await message.answer("សូមជ្រើសរើសផលិតផលដែលចង់ប្តូរតម្លៃ៖", reply_markup=kb.get_admin_products_keyboard(products, "admin_set_price"))

@router.callback_query(F.data.startswith("admin_set_price_"))
async def admin_set_price(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID: return
    pid = int(callback.data.split("_")[3])
    await state.update_data(pid=pid)
    await callback.message.edit_text("សូមវាយតម្លៃថ្មី៖")
    await state.set_state(AdminState.edit_price)

@router.message(AdminState.edit_price)
async def process_edit_price(message: Message, state: FSMContext):
    data = await state.get_data()
    db.update_product_price(data['pid'], message.text)
    await message.answer("✅ កែប្រែតម្លៃជោគជ័យ!", reply_markup=kb.get_admin_main_menu())
    await state.clear()

# --- Edit Image ---
@router.message(F.text == "🖼️ ដាក់រូបភាព (Set Picture)")
async def admin_edit_img_menu(message: Message):
    if message.from_user.id != ADMIN_ID: return
    products = db.get_products()
    await message.answer("សូមជ្រើសរើសផលិតផលដែលចង់ប្តូររូបភាព៖", reply_markup=kb.get_admin_products_keyboard(products, "admin_set_img"))

@router.callback_query(F.data.startswith("admin_set_img_"))
async def admin_set_img(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID: return
    pid = int(callback.data.split("_")[3])
    await state.update_data(pid=pid)
    await callback.message.edit_text("សូមវាយ Link រូបភាពថ្មី៖")
    await state.set_state(AdminState.edit_image)

@router.message(AdminState.edit_image)
async def process_edit_image(message: Message, state: FSMContext):
    data = await state.get_data()
    db.update_product_image(data['pid'], message.text)
    await message.answer("✅ កែប្រែរូបភាពជោគជ័យ!", reply_markup=kb.get_admin_main_menu())
    await state.clear()

# --- Add Stock ---
@router.message(F.text == "📦 បន្ថែមស្តុក (Add Stock)")
async def admin_add_stock_menu(message: Message):
    if message.from_user.id != ADMIN_ID: return
    products = db.get_products()
    await message.answer("សូមជ្រើសរើសផលិតផលដែលចង់បន្ថែមស្តុក៖", reply_markup=kb.get_admin_products_keyboard(products, "admin_set_stock"))

@router.callback_query(F.data.startswith("admin_set_stock_"))
async def admin_set_stock(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID: return
    pid = int(callback.data.split("_")[3])
    await state.update_data(pid=pid)
    await callback.message.edit_text("សូមវាយចំនួនស្តុកដែលត្រូវដាក់ (-1 សម្រាប់គ្មានកំណត់)៖")
    await state.set_state(AdminState.edit_stock)

@router.message(AdminState.edit_stock)
async def process_edit_stock(message: Message, state: FSMContext):
    try:
        stock = int(message.text)
        data = await state.get_data()
        db.update_product_stock(data['pid'], stock)
        await message.answer("✅ កែប្រែស្តុកជោគជ័យ!", reply_markup=kb.get_admin_main_menu())
        await state.clear()
    except ValueError:
        await message.answer("សូមវាយជាលេខ។")

# --- Delete Product ---
@router.message(F.text == "Delete Product")
async def admin_delete_product_menu(message: Message):
    if message.from_user.id != ADMIN_ID: return
    products = db.get_products()
    if not products:
        await message.answer("No products to delete.", reply_markup=kb.get_admin_main_menu())
        return
    await message.answer("Choose a product to delete:", reply_markup=kb.get_admin_products_keyboard(products, "admin_delete_product"))

@router.callback_query(F.data.startswith("admin_delete_product_"))
async def admin_delete_product_confirm(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    product_id = int(callback.data.split("_")[3])
    product = db.get_product(product_id)
    if not product:
        await callback.answer("Product not found.", show_alert=True)
        return
    await callback.message.edit_text(
        f"Delete this product?\n\n{product[1]} - {product[3]}",
        reply_markup=kb.get_delete_product_confirm_keyboard(product_id)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("admin_confirm_delete_"))
async def admin_delete_product(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    product_id = int(callback.data.split("_")[3])
    product = db.get_product(product_id)
    if not product:
        await callback.answer("Product not found.", show_alert=True)
        return
    deleted = db.delete_product(product_id)
    if deleted:
        await callback.message.edit_text(f"Deleted product: {product[1]}")
        await callback.answer("Deleted.")
    else:
        await callback.answer("Could not delete product.", show_alert=True)

# --- Notify Customers ---
@router.message(F.text == "Notify Customers")
async def admin_notify_customers_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    await message.answer(
        "Send the notification message for all customers.\n"
        "Type /cancel to stop."
    )
    await state.set_state(AdminState.notify_customers)

@router.message(AdminState.notify_customers)
async def process_notify_customers(message: Message, state: FSMContext, bot: Bot):
    if message.from_user.id != ADMIN_ID: return

    if message.text == "/cancel":
        await state.clear()
        await message.answer("Notification cancelled.", reply_markup=kb.get_admin_main_menu())
        return

    users = db.get_users()
    sent_count = 0
    failed_count = 0
    for user in users:
        try:
            await bot.send_message(chat_id=user[0], text=message.text)
            sent_count += 1
        except Exception as e:
            print(f"Error notifying customer {user[0]}: {e}")
            failed_count += 1

    await message.answer(
        f"Notification sent.\nSuccess: {sent_count}\nFailed: {failed_count}",
        reply_markup=kb.get_admin_main_menu()
    )
    await state.clear()

# --- Approve / Reject ---
@router.callback_query(F.data.startswith("admin_approve_"))
async def admin_approve_start(callback: CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split("_")[2])
    await state.update_data(
        order_id=order_id,
        approve_msg_id=callback.message.message_id,
        old_caption=callback.message.caption or ""
    )
    await state.set_state(AdminState.send_account)
    await callback.message.answer(
        f"✅ អ្នកបានជ្រើសរើស Approve Order #{order_id}។\n"
        f"⌨️ សូមវាយបញ្ចូលព័ត៌មាន Account (Email / Password) ដើម្បីឱ្យ Bot ផ្ញើទៅកាន់អតិថិជន៖\n"
        f"(ឬវាយ /cancel ដើម្បីបោះបង់)"
    )
    await callback.answer()

@router.message(AdminState.send_account)
async def process_send_account(message: Message, state: FSMContext, bot: Bot):
    if message.from_user.id != ADMIN_ID: return
    
    if message.text == "/cancel":
        await state.clear()
        await message.answer("បានបោះបង់ការបញ្ជូន Account។")
        return
        
    data = await state.get_data()
    order_id = data.get("order_id")
    account_info = message.text
    
    db.update_order_status(order_id, "approved")
    
    order = db.get_order(order_id)
    user_id = order[1]
    prod_name = order[2]
    product_id = order[5]
    
    db.deduct_stock(product_id)
    
    # Edit the original receipt message
    try:
        await bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=data.get("approve_msg_id"),
            caption=data.get("old_caption") + "\n\n✅ ស្ថានភាព៖ បានយល់ព្រម (Approved) - Account Sent"
        )
    except Exception:
        pass
    
    # Try to send account to user
    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"✅ ការបង់ប្រាក់សម្រាប់កញ្ចប់ **{prod_name}** របស់អ្នកត្រូវបានយល់ព្រម!\n\n"
                 f"🎉 **នេះគឺជាព័ត៌មាន Account របស់អ្នក៖**\n"
                 f"```text\n{account_info}\n```\n\n"
                 f"សូមអរគុណសម្រាប់ការគាំទ្រ!",
            parse_mode="Markdown"
        )
        await message.answer("✅ បានផ្ញើ Account ទៅកាន់អតិថិជនដោយជោគជ័យ!")
    except Exception as e:
        print(f"Error notifying user: {e}")
        await message.answer("❌ មានបញ្ហាក្នុងការផ្ញើសារទៅកាន់អតិថិជន។ អាចមកពីអតិថិជនបាន Block Bot។")
        
    await state.clear()

@router.callback_query(F.data.startswith("admin_reject_"))
async def admin_reject(callback: CallbackQuery, bot: Bot):
    order_id = int(callback.data.split("_")[2])
    db.update_order_status(order_id, "rejected")
    
    order = db.get_order(order_id)
    user_id = order[1]
    prod_name = order[2]
    
    await callback.message.edit_caption(
        caption=callback.message.caption + "\n\n❌ ស្ថានភាព៖ បដិសេធ (Rejected)"
    )
    
    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"❌ ការបង់ប្រាក់សម្រាប់កញ្ចប់ **{prod_name}** របស់អ្នកត្រូវបានបដិសេធ។\n\n"
                 f"សូមទាក់ទង Admin សម្រាប់ព័ត៌មានបន្ថែម។",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Error notifying user: {e}")
        
    await callback.answer("Rejected!")
