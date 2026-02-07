import asyncio
from database import get_active_users
from ai import generate_menu

async def daily_sender(bot):
    while True:
        users = get_active_users()

        for user_id, lang, goal in users:
            menu = generate_menu({"goal": goal})
            try:
                await bot.send_message(
                    user_id,
                    "☀️ Ваше меню на сегодня:\n\n" + menu
                )
            except:
                pass

        await asyncio.sleep(86400)  # 24 часа
