from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
import keyboards as kb
from config import ADMIN_ID, ABA_QR_URL, WELCOME_IMAGE_URL, CHANNEL_URL

router = Router()

class BuyState(StatesGroup):
    waiting_for_receipt = State()

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    db.add_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    welcome_text = (
        f"សួស្តី {message.from_user.full_name}! 👋\n\n"
        "សូមស្វាគមន៍មកកាន់ Premium Account Bot។ សូមជ្រើសរើសជម្រើសខាងក្រោម៖"
    )
    if WELCOME_IMAGE_URL:
        try:
            if WELCOME_IMAGE_URL.startswith("http"):
                await message.answer_photo(photo=WELCOME_IMAGE_URL)
            else:
                await message.answer_photo(photo=FSInputFile(WELCOME_IMAGE_URL))
        except Exception as e:
            print(f"Error sending welcome photo: {e}")
    await message.answer(welcome_text, reply_markup=kb.get_main_menu())
    
    products = db.get_products()
    if products:
        await message.answer(
            "ខាងក្រោមនេះជាកញ្ចប់ផលិតផលរបស់យើង៖",
            reply_markup=kb.get_products_keyboard(products)
        )

@router.callback_query(F.data == "start_menu")
async def start_menu_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.answer()

@router.message(F.text == "🛍️ មើលកញ្ចប់ (Products)")
async def show_catalog(message: Message):
    products = db.get_products()
    if not products:
        await message.answer("មិនទាន់មានទំនិញទេឥឡូវនេះ។")
        return
        
    await message.answer(
        "សូមជ្រើសរើសកញ្ចប់ដែលអ្នកចង់ទិញ៖",
        reply_markup=kb.get_products_keyboard(products)
    )

@router.callback_query(F.data.startswith("buy_"))
async def process_buy(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    product = db.get_product(product_id)
    
    if product:
        if product[5] == 0:
            await callback.answer("ផលិតផលនេះអស់ស្តុកហើយ!", show_alert=True)
            return
            
        order_id = db.create_order(callback.from_user.id, product_id)
        text = (
            f"🛒 អ្នកបានជ្រើសរើសទិញ៖ **{product[1]}**\n"
            f"💰 តម្លៃ៖ **{product[3]}**\n\n"
            f"📝 ការពិពណ៌នា៖ {product[2]}\n\n"
            f"💳 **វិធីបង់ប្រាក់ (ABA)**\n"
            f"សូម Scan កូដ QR ខាងក្រោម ដើម្បីបង់ប្រាក់។\n\n"
            f"បន្ទាប់ពីបង់ប្រាក់រួច សូមចុចប៊ូតុងខាងក្រោមរួចផ្ញើវិក្កយបត្រ (Receipt)។"
        )
        
        image_url = product[4]
        photo_to_send = image_url if image_url else ABA_QR_URL
        
        # If we have an image URL for the product or QR, we send a new message with photo
        if photo_to_send:
            await callback.message.delete()
            caption_text = text
            if ABA_QR_URL and photo_to_send != ABA_QR_URL and str(ABA_QR_URL).startswith("http"):
                 caption_text += f"\n\n🔗 តំណភ្ជាប់កូដ QR៖ {ABA_QR_URL}"
                 
            try:
                if photo_to_send.startswith("http"):
                    photo_obj = photo_to_send
                else:
                    photo_obj = FSInputFile(photo_to_send)
                    
                await callback.message.answer_photo(
                    photo=photo_obj,
                    caption=caption_text,
                    reply_markup=kb.get_payment_keyboard(order_id),
                    parse_mode="Markdown"
                )
            except Exception as e:
                print(f"Error sending product photo: {e}")
                await callback.message.answer(text, reply_markup=kb.get_payment_keyboard(order_id), parse_mode="Markdown")
        else:
            await callback.message.edit_text(
                text,
                reply_markup=kb.get_payment_keyboard(order_id),
                parse_mode="Markdown"
            )
    await callback.answer()

@router.callback_query(F.data.startswith("paid_"))
async def process_paid(callback: CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split("_")[1])
    await state.update_data(order_id=order_id)
    await state.set_state(BuyState.waiting_for_receipt)
    
    await callback.message.delete()
    await callback.message.answer(
        "📸 សូមផ្ញើរូបភាពវិក្កយបត្រ (Receipt) របស់អ្នកមកកាន់ទីនេះ៖\n"
        "(ឬវាយ /cancel ដើម្បីបោះបង់)"
    )
    await callback.answer()

@router.message(BuyState.waiting_for_receipt, F.photo)
async def receipt_received(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    order_id = data.get("order_id")
    
    # Get the largest photo
    photo_id = message.photo[-1].file_id
    
    db.update_order_receipt(order_id, photo_id)
    
    # Notify Admin
    order = db.get_order(order_id) # (id, user_id, prod_name, status, receipt_file_id)
    
    admin_text = (
        f"🔔 **មានការបញ្ជាទិញថ្មី!**\n\n"
        f"Order ID: #{order[0]}\n"
        f"User ID: `{order[1]}`\n"
        f"Product: {order[2]}\n"
        f"Status: {order[3]}"
    )
    
    try:
        await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_id,
            caption=admin_text,
            reply_markup=kb.get_admin_approval_keyboard(order_id),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Error sending to admin: {e}")
        
    await message.answer(
        "✅ វិក្កយបត្ររបស់អ្នកត្រូវបានបញ្ជូនទៅកាន់ Admin។\n"
        "សូមរង់ចាំការពិនិត្យនិងផ្តល់ Account ជូនអ្នកក្នុងពេលបន្តិចទៀតនេះ។",
        reply_markup=kb.get_main_menu()
    )
    await state.clear()

@router.message(BuyState.waiting_for_receipt, F.text == "/cancel")
async def cancel_receipt(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("ការបញ្ជាទិញត្រូវបានបោះបង់។", reply_markup=kb.get_main_menu())

@router.message(F.text == "ℹ️ អំពីយើង (About)")
async def show_about(message: Message):
    text = "ℹ️ **អំពីយើង (About Us)**\n\nយើងខ្ញុំផ្តល់ជូននូវសេវាកម្មលក់ Premium Accounts ដូចជា Capcut Pro, Gemini ក្នុងតម្លៃសមរម្យ និងសេវាកម្មរហ័សទាន់ចិត្ត។"
    await message.answer(text)

@router.message(F.text == "❓ របៀបទិញ (How to buy)")
async def show_how_to_buy(message: Message):
    text = "❓ **របៀបទិញ (How to buy)**\n\n1. ជ្រើសរើសកញ្ចប់ដែលអ្នកចង់ទិញ\n2. ធ្វើការបង់ប្រាក់តាមរយៈកូដ ABA QR ដែលបានផ្តល់\n3. ផ្ញើវិក្កយបត្រ (Receipt) ចូលមកកាន់ Bot\n4. រង់ចាំ Admin ពិនិត្យ និងផ្តល់ Account ជូនអ្នក"
    await message.answer(text)

@router.message(F.text == "📢 ឆានែលរបស់យើង (Our Channel)")
async def show_channel(message: Message):
    await message.answer(f"ចូលរួមឆានែលរបស់យើងនៅទីនេះ៖\nhttps://t.me/smarttech_digital")

@router.message(F.text == "📞 ទំនាក់ទំនង Admin")
async def show_admin_contact(message: Message):
    await message.answer("ទំនាក់ទំនង Admin តាមរយៈ៖\nhttps://t.me/set_rosa")
