import asyncio
import logging
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiohttp import web
from middlewares.db import DataBaseSession
from database.engine import create_db, drop_db, session_maker
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from handlers.admin_private import admin_router
from handlers.user_group import user_group_router
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

ADMIN_ID = "2031703859"
BOT_TOKEN = "5865582967:AAFNrA6pmu3clrIQQ1gfGf0vWabukSGyQvs"
WEBHOOK_PATH = "/webhook"
BASE_URL = f"https://hookaiogram-github-io.onrender.com{WEBHOOK_PATH}"
# Функция для установки командного меню для бота
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


async def set_commands():
    # Создаем список команд, которые будут доступны пользователям
    commands = [BotCommand(command='admin', description='Старт')]
# Устанавливаем эти команды как дефолтные для всех пользователей
    await bot.set_my_commands(commands, BotCommandScopeDefault())
# Функция, которая будет вызвана при запуске бота


async def on_startup() -> None:
    await drop_db()

    await create_db()
# Устанавливаем командное меню
    await set_commands()
# Устанавливаем вебхук для приема сообщений через заданный URL
    await bot.set_webhook(f"{BASE_URL}{WEBHOOK_PATH}")
# Отправляем сообщение администратору о том, что бот был запущен
    await bot.send_message(chat_id=ADMIN_ID, text='Бот запущен!')
# Функция, которая будет вызвана при остановке бота


async def on_shutdown() -> None:
    # Отправляем сообщение администратору о том, что бот был остановлен
    await bot.send_message(chat_id=ADMIN_ID, text='Бот остановлен!')
# Удаляем вебхук и, при необходимости, очищаем ожидающие обновления
    await bot.delete_webhook(drop_pending_updates=True)
# Закрываем сессию бота, освобождая ресурсы
    await bot.session.close()
# Основная функция, которая запускает приложение


async def main() -> None:
    # Подключаем маршрутизатор (роутер) для обработки сообщений
    dp.include_router(admin_router)
    dp.include_router(user_group_router)
# Регистрируем функцию, которая будет вызвана при старте бота
    dp.startup.register(on_startup)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
# Регистрируем функцию, которая будет вызвана при остановке бота
    dp.shutdown.register(on_shutdown)
# Создаем веб-приложение на базе aiohttp
    app = web.Application()
# Настраиваем обработчик запросов для работы с вебхуком
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
# Передаем диспетчер
# Регистрируем обработчик запросов на определенном пути
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
# Настраиваем приложение и связываем его с диспетчером и ботом
    setup_application(app, dp, bot=bot)
# Запускаем веб-сервер на указанном хосте и порте

    await dp.start_polling(bot)
# Запускаем веб-сервер на указанном хосте и порте
    


# Точка входа в программу
if __name__ == "__main__":
    app = asyncio.run(main())
    web.run_app(app, host="0.0.0.0", port=10000)


