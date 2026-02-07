import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, Command

from config import BOT_TOKEN, PAYMENT_TOKEN
from texts import TEXTS
from states import UserForm
from ai import generate_menu
from database import give_trial, has_access, give_subscription

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# ───── KEYBOARDS ─────

def language_keyboard():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
    )

def goal_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔥 Lose weight", callback_data="goal_lose"))
    kb.add(InlineKeyboardButton("💪 Gain weight", callback_data="goal_gain"))
    kb.add(InlineKeyboardButton("⚖️ Keep shape", callback_data="goal_keep"))
    return kb

# ───── START ─────

@dp.message_handler(CommandStart())
async def start(message: types.Message):
    give_trial(message.from_user.id)

    await message.answer(
        TEXTS["ru"]["start"],
        reply_markup=language_keyboard()
    )
    await UserForm.language.set()

# ───── LANGUAGE ─────

@dp.callback_query_handler(lambda c: c.data.startswith("lang_"), state=UserForm.language)
async def set_language(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(language=lang)

    await callback.message.edit_text(
        TEXTS[lang]["choose_goal"],
        reply_markup=goal_keyboard()
    )
    await UserForm.goal.set()

# ───── GOAL ─────

@dp.callback_query_handler(lambda c: c.data.startswith("goal_"), state=UserForm.goal)
async def set_goal(callback: types.CallbackQuery, state: FSMContext):

    if not has_access(callback.from_user.id):
        await callback.message.answer("🔒 Access expired. Use /buy")
        return

    goal = callback.data.split("_")[1]
    await state.update_data(goal=goal)

    data = await state.get_data()
    await callback.message.answer(TEXTS[data["language"]]["ask_weight"])
    await UserForm.weight.set()

# ───── WEIGHT ─────

@dp.message_handler(state=UserForm.weight)
async def get_weight(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Send a number 🙂")
        return

    await state.update_data(weight=int(message.text))
    data = await state.get_data()
    await message.answer(TEXTS[data["language"]]["ask_height"])
    await UserForm.height.set()

# ───── HEIGHT ─────

@dp.message_handler(state=UserForm.height)
async def get_height(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Send a number 🙂")
        return

    await state.update_data(height=int(message.text))
    data = await state.get_data()

    menu = generate_menu(data)
    await message.answer("🍽 Your daily menu:\n\n" + menu)
    await state.finish()

# ───── BUY ─────

@dp.message_handler(Command("buy"))
async def buy(message: types.Message):
    prices = [LabeledPrice("Fitness subscription", 10000)]

    await bot.send_invoice(
        message.chat.id,
        "Fitness subscription 💪",
        "Access for 30 days",
        "fitness_sub",
        PAYMENT_TOKEN,
        "UZS",
        prices
    )

@dp.pre_checkout_query_handler(lambda q: True)
async def checkout(pre_checkout: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout.id, ok=True)

@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def success(message: types.Message):
    give_subscription(message.from_user.id)
    await message.answer("✅ Payment successful! Access unlocked.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
