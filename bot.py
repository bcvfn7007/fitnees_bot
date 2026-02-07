import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    LabeledPrice, PreCheckoutQuery
)
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from config import BOT_TOKEN, PAYMENT_TOKEN
from texts import TEXTS
from states import UserForm
from ai import generate_menu
from database import give_trial, has_access, give_subscription

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------- keyboards ----------

def language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        ]
    ])

def goal_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Lose weight", callback_data="goal_lose")],
        [InlineKeyboardButton(text="💪 Gain weight", callback_data="goal_gain")],
        [InlineKeyboardButton(text="⚖️ Keep shape", callback_data="goal_keep")],
    ])

# ---------- start ----------

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    give_trial(message.from_user.id)

    await message.answer(
        TEXTS["ru"]["start"],
        reply_markup=language_keyboard()
    )
    await state.set_state(UserForm.language)

# ---------- language ----------

@dp.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(language=lang)

    await callback.message.edit_text(
        TEXTS[lang]["choose_goal"],
        reply_markup=goal_keyboard()
    )
    await state.set_state(UserForm.goal)

# ---------- goal ----------

@dp.callback_query(F.data.startswith("goal_"))
async def set_goal(callback: CallbackQuery, state: FSMContext):
    if not has_access(callback.from_user.id):
        await callback.message.answer("🔒 Access expired. Use /buy")
        return

    goal = callback.data.split("_")[1]
    await state.update_data(goal=goal)

    lang = (await state.get_data())["language"]
    await callback.message.answer(TEXTS[lang]["ask_weight"])
    await state.set_state(UserForm.weight)

# ---------- weight ----------

@dp.message(UserForm.weight)
async def get_weight(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Send a number 🙂")
        return

    await state.update_data(weight=int(message.text))
    lang = (await state.get_data())["language"]

    await message.answer(TEXTS[lang]["ask_height"])
    await state.set_state(UserForm.height)

# ---------- height ----------

@dp.message(UserForm.height)
async def get_height(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Send a number 🙂")
        return

    await state.update_data(height=int(message.text))
    data = await state.get_data()

    menu = generate_menu(data)
    await message.answer("🍽 Your daily menu:\n\n" + menu)

    await state.clear()

# ---------- buy ----------

@dp.message(Command("buy"))
async def buy(message: Message):
    prices = [LabeledPrice(label="Fitness subscription", amount=10000)]

    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Fitness subscription 💪",
        description="Access for 30 days",
        payload="fitness_sub",
        provider_token=PAYMENT_TOKEN,
        currency="UZS",
        prices=prices,
    )

# ---------- payment ----------

@dp.pre_checkout_query()
async def pre_checkout(pre_checkout: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout.id, ok=True)

@dp.message(F.successful_payment)
async def success(message: Message):
    give_subscription(message.from_user.id)
    await message.answer("✅ Payment successful! Access unlocked.")

# ---------- run ----------

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
