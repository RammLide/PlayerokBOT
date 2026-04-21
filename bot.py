import telebot
from telebot import types
import logging
from datetime import datetime
import re

from playerokapi.account import Account
from playerokapi.exceptions import *
from playerokapi.enums import ItemStatuses
import config
from listener import PlayerokListener
from autoconfirm import AutoConfirmSettings

# Хранилище для состояния пользователей
user_states = {}
ITEMS_PER_PAGE = 15
CHATS_PER_PAGE = 10

# Инициализация настроек автоподтверждения
autoconfirm_settings = AutoConfirmSettings()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = telebot.TeleBot(config.TELEGRAM_BOT_TOKEN)

# Инициализация Playerok аккаунта
try:
    playerok_account = Account(
        token=config.PLAYEROK_TOKEN,
        user_agent=config.USER_AGENT,
        proxy=config.PROXY
    ).get()
    logger.info(f"Playerok аккаунт инициализирован: {playerok_account.username}")
except Exception as e:
    logger.error(f"Ошибка инициализации Playerok аккаунта: {e}")
    playerok_account = None

# Инициализация слушателя событий
playerok_listener = None
if playerok_account and config.ADMIN_IDS:
    try:
        playerok_listener = PlayerokListener(playerok_account, bot, config.ADMIN_IDS, autoconfirm_settings)
        playerok_listener.start()
    except Exception as e:
        logger.error(f"Ошибка запуска слушателя событий: {e}")


def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором"""
    return user_id in config.ADMIN_IDS or len(config.ADMIN_IDS) == 0


@bot.message_handler(commands=['start'])
def start_command(message):
    """Обработчик команды /start"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_products = types.KeyboardButton("📦 Мои товары")
    btn_chats = types.KeyboardButton("💬 Чаты")
    btn_autoconfirm = types.KeyboardButton("⚙️ Автоподтверждение")
    btn_search = types.KeyboardButton("🔍 Поиск товара")
    btn_help = types.KeyboardButton("❓ Помощь")
    markup.add(btn_products, btn_chats)
    markup.add(btn_autoconfirm, btn_search)
    markup.add(btn_help)
    
    welcome_text = (
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        f"Я бот для работы с Playerok API.\n\n"
        f"Используйте кнопки ниже для навигации."
    )
    bot.reply_to(message, welcome_text, reply_markup=markup)


@bot.message_handler(commands=['help'])
def help_command(message):
    """Обработчик команды /help"""
    help_text = (
        "📚 Доступные команды:\n\n"
        "/start - Начать работу с ботом\n"
        "/products - Получить список всех товаров\n"
        "/chats - Открыть список чатов\n"
        "/autoconfirm - Настройка автоподтверждения\n"
        "/search - Поиск товара по названию\n"
        "/help - Показать это сообщение\n\n"
        "Или используйте кнопки:\n"
        "📦 Мои товары - список активных товаров\n"
        "💬 Чаты - список чатов с покупателями\n"
        "⚙️ Автоподтверждение - настройка автовыдачи\n"
        "🔍 Поиск товара - найти товар по названию\n"
        "❓ Помощь - это сообщение"
    )
    bot.reply_to(message, help_text)


@bot.message_handler(func=lambda message: message.text == "📦 Мои товары")
def products_button_handler(message):
    """Обработчик кнопки 'Мои товары'"""
    products_command(message)


@bot.message_handler(func=lambda message: message.text == "💬 Чаты")
def chats_button_handler(message):
    """Обработчик кнопки 'Чаты'"""
    chats_command(message)


@bot.message_handler(func=lambda message: message.text == "⚙️ Автоподтверждение")
def autoconfirm_button_handler(message):
    """Обработчик кнопки 'Автоподтверждение'"""
    autoconfirm_command(message)


@bot.message_handler(func=lambda message: message.text == "🔍 Поиск товара")
def search_button_handler(message):
    """Обработчик кнопки 'Поиск товара'"""
    search_command(message)


@bot.message_handler(func=lambda message: message.text == "❓ Помощь")
def help_button_handler(message):
    """Обработчик кнопки 'Помощь'"""
    help_command(message)


def get_all_active_items():
    """Получает все активные товары пользователя"""
    user = playerok_account.get_user(id=playerok_account.id)
    
    all_items = []
    after_cursor = None
    
    while True:
        items = user.get_items(count=24, statuses=[ItemStatuses.APPROVED], after_cursor=after_cursor)
        
        if not items or not items.items:
            break
        
        all_items.extend(items.items)
        
        if hasattr(items, 'page_info') and items.page_info and items.page_info.has_next_page:
            after_cursor = items.page_info.end_cursor
        else:
            break
    
    return all_items


def create_items_keyboard(items, page=0, search_query=None):
    """Создает клавиатуру с товарами и пагинацией"""
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_items = items[start_idx:end_idx]
    
    markup = types.InlineKeyboardMarkup()
    
    # Добавляем кнопку поиска первой (только если это не результаты поиска)
    if not search_query:
        search_btn = types.InlineKeyboardButton(
            text="🔍 Поиск товара",
            callback_data="start_search"
        )
        markup.add(search_btn)
    else:
        # Если это результаты поиска, добавляем кнопку возврата к полному списку
        back_btn = types.InlineKeyboardButton(
            text="◀️ Вернуться к полному списку",
            callback_data="back_to_all_items"
        )
        markup.add(back_btn)
    
    for item in page_items:
        btn_text = item.name if len(item.name) <= 50 else item.name[:47] + "..."
        btn = types.InlineKeyboardButton(
            text=btn_text,
            callback_data=f"item_{item.id}"
        )
        markup.add(btn)
    
    # Кнопки навигации
    nav_buttons = []
    
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(
            text="◀️ Назад",
            callback_data=f"page_{page-1}_{search_query if search_query else 'all'}"
        ))
    
    total_pages = (len(items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    nav_buttons.append(types.InlineKeyboardButton(
        text=f"📄 {page + 1}/{total_pages}",
        callback_data="current_page"
    ))
    
    if end_idx < len(items):
        nav_buttons.append(types.InlineKeyboardButton(
            text="Вперед ▶️",
            callback_data=f"page_{page+1}_{search_query if search_query else 'all'}"
        ))
    
    if nav_buttons:
        markup.row(*nav_buttons)
    
    return markup


@bot.message_handler(commands=['search'])
def search_command(message):
    """Обработчик команды /search"""
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ У вас нет доступа к этой команде.")
        return
    
    if not playerok_account:
        bot.reply_to(message, "❌ Ошибка: Playerok аккаунт не инициализирован. Проверьте config.py")
        return
    
    user_states[message.from_user.id] = 'waiting_search'
    bot.reply_to(message, "🔍 Введите название товара или его часть для поиска:")


@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == 'waiting_search')
def handle_search_query(message):
    """Обработчик поискового запроса"""
    try:
        search_query = message.text.strip().lower()
        
        if len(search_query) < 2:
            bot.reply_to(message, "❌ Запрос слишком короткий. Введите минимум 2 символа.")
            return
        
        # Получаем информацию о сообщении для редактирования
        search_msg_info = user_states.get(f'search_msg_{message.from_user.id}')
        
        # Получаем все товары
        all_items = get_all_active_items()
        
        # Фильтруем по поисковому запросу
        filtered_items = [
            item for item in all_items 
            if search_query in item.name.lower()
        ]
        
        user_states.pop(message.from_user.id, None)
        
        if not filtered_items:
            response = f"❌ Товары по запросу '{search_query}' не найдены."
            
            # Добавляем кнопку возврата
            markup = types.InlineKeyboardMarkup()
            back_btn = types.InlineKeyboardButton(text="◀️ Вернуться к списку", callback_data="back_to_all_items")
            markup.add(back_btn)
            
            if search_msg_info:
                bot.edit_message_text(
                    chat_id=search_msg_info['chat_id'],
                    message_id=search_msg_info['message_id'],
                    text=response,
                    reply_markup=markup
                )
                # Удаляем сообщение пользователя с запросом
                try:
                    bot.delete_message(message.chat.id, message.message_id)
                except:
                    pass
            else:
                bot.send_message(message.chat.id, response, reply_markup=markup)
            
            user_states.pop(f'search_msg_{message.from_user.id}', None)
            return
        
        markup = create_items_keyboard(filtered_items, page=0, search_query=search_query)
        response = f"🔍 Найдено товаров: {len(filtered_items)}\n\nНажмите на товар для просмотра деталей:"
        
        # Сохраняем результаты поиска
        user_states[f"search_{message.from_user.id}"] = {
            'items': filtered_items,
            'query': search_query
        }
        
        if search_msg_info:
            bot.edit_message_text(
                chat_id=search_msg_info['chat_id'],
                message_id=search_msg_info['message_id'],
                text=response,
                reply_markup=markup
            )
            # Удаляем сообщение пользователя с запросом
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except:
                pass
        else:
            bot.send_message(message.chat.id, response, reply_markup=markup)
        
        user_states.pop(f'search_msg_{message.from_user.id}', None)
        
    except Exception as e:
        logger.error(f"Ошибка при поиске: {e}")
        bot.reply_to(message, f"❌ Произошла ошибка при поиске: {str(e)}")
        user_states.pop(message.from_user.id, None)
        user_states.pop(f'search_msg_{message.from_user.id}', None)


@bot.message_handler(commands=['products'])
def products_command(message):
    """Обработчик команды /products - получение товаров"""
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ У вас нет доступа к этой команде.")
        return
    
    if not playerok_account:
        bot.reply_to(message, "❌ Ошибка: Playerok аккаунт не инициализирован. Проверьте config.py")
        return
    
    try:
        bot.reply_to(message, "⏳ Получаю список товаров...")
        
        # Получаем все активные товары
        all_items = get_all_active_items()
        
        if not all_items:
            bot.reply_to(message, "📦 У вас нет активных товаров на Playerok.")
            return
        
        # Сохраняем все товары для пагинации
        user_states[f"all_{message.from_user.id}"] = all_items
        
        markup = create_items_keyboard(all_items, page=0)
        response = f"📦 Ваши активные товары ({len(all_items)} шт.):\n\nНажмите на товар для просмотра деталей:"
        bot.send_message(message.chat.id, response, reply_markup=markup)
            
        logger.info(f"Пользователь {message.from_user.id} запросил список товаров")
        
    except (RequestPlayerokError, RequestFailedError, UnauthorizedError) as e:
        logger.error(f"Ошибка Playerok API: {e}")
        bot.reply_to(message, f"❌ Ошибка Playerok API: {str(e)}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        bot.reply_to(message, f"❌ Произошла ошибка: {str(e)}")


@bot.callback_query_handler(func=lambda call: call.data == "start_search")
def start_search_callback(call):
    """Обработчик кнопки 'Поиск товара'"""
    user_states[call.from_user.id] = 'waiting_search'
    user_states[f'search_msg_{call.from_user.id}'] = {
        'chat_id': call.message.chat.id,
        'message_id': call.message.message_id
    }
    
    # Редактируем текущее сообщение
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="🔍 Введите название товара или его часть для поиска:"
    )
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_all_items")
def back_to_all_items_callback(call):
    """Обработчик кнопки 'Вернуться к списку всех товаров'"""
    try:
        # Очищаем результаты поиска
        user_states.pop(f"search_{call.from_user.id}", None)
        
        # Получаем все товары
        all_cache_key = f"all_{call.from_user.id}"
        
        if all_cache_key in user_states:
            items = user_states[all_cache_key]
        else:
            items = get_all_active_items()
            user_states[all_cache_key] = items
        
        if not items:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="📦 У вас нет активных товаров на Playerok."
            )
            bot.answer_callback_query(call.id)
            return
        
        response = f"📦 Ваши активные товары ({len(items)} шт.):\n\nНажмите на товар для просмотра деталей:"
        markup = create_items_keyboard(items, page=0)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=response,
            reply_markup=markup
        )
        
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        logger.error(f"Ошибка при возврате к списку: {e}")
        bot.answer_callback_query(call.id, text="❌ Ошибка при загрузке списка")


@bot.callback_query_handler(func=lambda call: call.data.startswith("page_"))
def page_navigation_callback(call):
    """Обработчик навигации по страницам"""
    try:
        parts = call.data.split("_")
        page = int(parts[1])
        search_query = parts[2] if len(parts) > 2 and parts[2] != 'all' else None
        
        # Получаем товары из кэша
        if search_query:
            cache_key = f"search_{call.from_user.id}"
            cached_data = user_states.get(cache_key)
            if not cached_data:
                bot.answer_callback_query(call.id, text="❌ Результаты поиска устарели. Выполните поиск заново.")
                return
            items = cached_data['items']
            response = f"🔍 Найдено товаров: {len(items)}\n\nНажмите на товар для просмотра деталей:"
        else:
            cache_key = f"all_{call.from_user.id}"
            items = user_states.get(cache_key)
            if not items:
                bot.answer_callback_query(call.id, text="❌ Данные устарели. Обновите список товаров.")
                return
            response = f"📦 Ваши активные товары ({len(items)} шт.):\n\nНажмите на товар для просмотра деталей:"
        
        markup = create_items_keyboard(items, page=page, search_query=search_query)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=response,
            reply_markup=markup
        )
        
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        logger.error(f"Ошибка при навигации по страницам: {e}")
        bot.answer_callback_query(call.id, text="❌ Ошибка при переключении страницы")


@bot.callback_query_handler(func=lambda call: call.data == "current_page")
def current_page_callback(call):
    """Обработчик нажатия на текущую страницу (ничего не делает)"""
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("item_"))
def item_details_callback(call):
    """Обработчик нажатия на кнопку товара"""
    try:
        item_id = call.data.replace("item_", "")
        
        # Получаем детальную информацию о товаре
        item = playerok_account.get_item(id=item_id)
        
        # Формируем детальное сообщение
        response = f"📦 {item.name}\n\n"
        response += f"💰 Цена: {item.price} ₽\n"
        
        if item.raw_price and item.raw_price != item.price:
            response += f"💵 Цена без скидки: {item.raw_price} ₽\n"
        
        response += f"📊 Статус: {item.status.name}\n"
        response += f"🔍 Приоритет: {item.priority.name}\n"
        
        if hasattr(item, 'views_counter') and item.views_counter:
            response += f"👁 Просмотров: {item.views_counter}\n"
        
        if hasattr(item, 'game') and item.game:
            response += f"🎮 Игра: {item.game.name}\n"
        
        if hasattr(item, 'category') and item.category:
            response += f"📁 Категория: {item.category.name}\n"
        
        if item.description:
            response += f"\n📝 Описание:\n{item.description[:500]}"
            if len(item.description) > 500:
                response += "..."
        
        # Кнопка "Назад"
        markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton(text="◀️ Назад к списку", callback_data="back_to_list")
        markup.add(back_btn)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=response,
            reply_markup=markup
        )
        
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        logger.error(f"Ошибка при получении деталей товара: {e}")
        bot.answer_callback_query(call.id, text="❌ Ошибка при загрузке товара")


@bot.callback_query_handler(func=lambda call: call.data == "back_to_list")
def back_to_list_callback(call):
    """Обработчик кнопки 'Назад к списку'"""
    try:
        # Проверяем есть ли результаты поиска
        search_cache_key = f"search_{call.from_user.id}"
        all_cache_key = f"all_{call.from_user.id}"
        
        if search_cache_key in user_states:
            cached_data = user_states[search_cache_key]
            items = cached_data['items']
            search_query = cached_data['query']
            response = f"🔍 Найдено товаров: {len(items)}\n\nНажмите на товар для просмотра деталей:"
            markup = create_items_keyboard(items, page=0, search_query=search_query)
        elif all_cache_key in user_states:
            items = user_states[all_cache_key]
            response = f"📦 Ваши активные товары ({len(items)} шт.):\n\nНажмите на товар для просмотра деталей:"
            markup = create_items_keyboard(items, page=0)
        else:
            # Если кэша нет, получаем заново
            all_items = get_all_active_items()
            
            if not all_items:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="📦 У вас нет активных товаров на Playerok."
                )
                bot.answer_callback_query(call.id)
                return
            
            user_states[all_cache_key] = all_items
            response = f"📦 Ваши активные товары ({len(all_items)} шт.):\n\nНажмите на товар для просмотра деталей:"
            markup = create_items_keyboard(all_items, page=0)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=response,
            reply_markup=markup
        )
        
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        logger.error(f"Ошибка при возврате к списку: {e}")
        bot.answer_callback_query(call.id, text="❌ Ошибка при загрузке списка")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """Обработчик всех остальных сообщений"""
    # Проверяем, не отвечает ли пользователь в чате
    if message.from_user.id in user_states and user_states[message.from_user.id].startswith('replying_'):
        handle_chat_reply(message)
    # Проверяем, не настраивает ли пользователь автоподтверждение
    elif message.from_user.id in user_states and user_states[message.from_user.id].startswith('setting_'):
        handle_autoconfirm_message(message)
    else:
        bot.reply_to(message, "Используйте /help для просмотра доступных команд.")


@bot.message_handler(commands=['autoconfirm'])
def autoconfirm_command(message):
    """Обработчик команды /autoconfirm - настройка автоподтверждения"""
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ У вас нет доступа к этой команде.")
        return
    
    if not playerok_account:
        bot.reply_to(message, "❌ Ошибка: Playerok аккаунт не инициализирован.")
        return
    
    # Формируем меню настроек
    status = "✅ Включено" if autoconfirm_settings.is_enabled() else "❌ Выключено"
    global_msg = autoconfirm_settings.get_global_message()
    global_status = f"✅ Установлено" if global_msg else "❌ Не установлено"
    
    item_messages = autoconfirm_settings.get_all_item_messages()
    item_count = len(item_messages)
    
    response = (
        f"⚙️ Настройки автоподтверждения\n\n"
        f"Статус: {status}\n"
        f"Глобальное сообщение: {global_status}\n"
        f"Настроено товаров: {item_count}\n\n"
        f"Выберите действие:"
    )
    
    markup = types.InlineKeyboardMarkup()
    
    # Кнопка включения/выключения
    toggle_text = "❌ Выключить" if autoconfirm_settings.is_enabled() else "✅ Включить"
    toggle_btn = types.InlineKeyboardButton(
        text=toggle_text,
        callback_data="autoconfirm_toggle"
    )
    
    # Кнопка настройки глобального сообщения
    global_btn = types.InlineKeyboardButton(
        text="🌐 Сообщение для всех товаров",
        callback_data="autoconfirm_global"
    )
    
    # Кнопка настройки для конкретного товара
    item_btn = types.InlineKeyboardButton(
        text="📦 Сообщение для товара",
        callback_data="autoconfirm_item"
    )
    
    # Кнопка просмотра настроенных товаров
    if item_count > 0:
        view_btn = types.InlineKeyboardButton(
            text=f"📋 Просмотр настроек ({item_count})",
            callback_data="autoconfirm_view"
        )
        markup.add(toggle_btn)
        markup.add(global_btn)
        markup.add(item_btn)
        markup.add(view_btn)
    else:
        markup.add(toggle_btn)
        markup.add(global_btn)
        markup.add(item_btn)
    
    bot.send_message(message.chat.id, response, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "autoconfirm_toggle")
def autoconfirm_toggle_callback(call):
    """Переключение автоподтверждения"""
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, text="❌ У вас нет доступа")
        return
    
    if autoconfirm_settings.is_enabled():
        autoconfirm_settings.disable()
        bot.answer_callback_query(call.id, text="❌ Автоподтверждение выключено")
    else:
        autoconfirm_settings.enable()
        bot.answer_callback_query(call.id, text="✅ Автоподтверждение включено")
    
    # Обновляем меню
    status = "✅ Включено" if autoconfirm_settings.is_enabled() else "❌ Выключено"
    global_msg = autoconfirm_settings.get_global_message()
    global_status = f"✅ Установлено" if global_msg else "❌ Не установлено"
    
    item_messages = autoconfirm_settings.get_all_item_messages()
    item_count = len(item_messages)
    
    response = (
        f"⚙️ Настройки автоподтверждения\n\n"
        f"Статус: {status}\n"
        f"Глобальное сообщение: {global_status}\n"
        f"Настроено товаров: {item_count}\n\n"
        f"Выберите действие:"
    )
    
    markup = types.InlineKeyboardMarkup()
    
    toggle_text = "❌ Выключить" if autoconfirm_settings.is_enabled() else "✅ Включить"
    toggle_btn = types.InlineKeyboardButton(
        text=toggle_text,
        callback_data="autoconfirm_toggle"
    )
    
    global_btn = types.InlineKeyboardButton(
        text="🌐 Сообщение для всех товаров",
        callback_data="autoconfirm_global"
    )
    
    item_btn = types.InlineKeyboardButton(
        text="📦 Сообщение для товара",
        callback_data="autoconfirm_item"
    )
    
    if item_count > 0:
        view_btn = types.InlineKeyboardButton(
            text=f"📋 Просмотр настроек ({item_count})",
            callback_data="autoconfirm_view"
        )
        markup.add(toggle_btn)
        markup.add(global_btn)
        markup.add(item_btn)
        markup.add(view_btn)
    else:
        markup.add(toggle_btn)
        markup.add(global_btn)
        markup.add(item_btn)
    
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=response,
            reply_markup=markup
        )
    except:
        pass


@bot.callback_query_handler(func=lambda call: call.data == "autoconfirm_global")
def autoconfirm_global_callback(call):
    """Настройка глобального сообщения"""
    user_states[call.from_user.id] = 'setting_global'
    
    current_msg = autoconfirm_settings.get_global_message()
    if current_msg:
        text = f"📝 Текущее глобальное сообщение:\n\n{current_msg}\n\n"
    else:
        text = "📝 Глобальное сообщение не установлено.\n\n"
    
    text += "Отправьте новое сообщение, которое будет отправляться всем покупателям после покупки.\n\n"
    text += "Или отправьте /cancel для отмены."
    
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, text)


@bot.callback_query_handler(func=lambda call: call.data == "autoconfirm_item")
def autoconfirm_item_callback(call):
    """Выбор товара для настройки"""
    try:
        bot.answer_callback_query(call.id, text="⏳ Загружаю товары...")
        
        # Получаем все товары
        all_items = get_all_active_items()
        
        if not all_items:
            bot.send_message(call.message.chat.id, "❌ У вас нет активных товаров.")
            return
        
        # Сохраняем товары для выбора
        user_states[f"autoconfirm_items_{call.from_user.id}"] = all_items
        
        # Показываем первую страницу
        show_autoconfirm_items_page(call.message.chat.id, call.from_user.id, page=0)
        
    except Exception as e:
        logger.error(f"Ошибка при выборе товара: {e}")
        bot.send_message(call.message.chat.id, f"❌ Ошибка: {str(e)}")


def show_autoconfirm_items_page(chat_id, user_id, page=0, message_id=None):
    """Показать страницу с товарами для настройки"""
    all_items = user_states.get(f"autoconfirm_items_{user_id}", [])
    
    if not all_items:
        return
    
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_items = all_items[start_idx:end_idx]
    
    # Создаем кнопки с товарами
    markup = types.InlineKeyboardMarkup()
    
    # Кнопка поиска
    search_btn = types.InlineKeyboardButton(
        text="🔍 Поиск товара",
        callback_data="autoconfirm_search"
    )
    markup.add(search_btn)
    
    for item in page_items:
        has_message = autoconfirm_settings.get_item_message(item.id) is not None
        prefix = "✅ " if has_message else ""
        btn_text = f"{prefix}{item.name[:40]}"
        btn = types.InlineKeyboardButton(
            text=btn_text,
            callback_data=f"autoconfirm_select_{item.id}"
        )
        markup.add(btn)
    
    # Кнопки навигации
    nav_buttons = []
    
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(
            text="◀️ Назад",
            callback_data=f"autoconfirm_items_page_{page-1}"
        ))
    
    total_pages = (len(all_items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    nav_buttons.append(types.InlineKeyboardButton(
        text=f"📄 {page + 1}/{total_pages}",
        callback_data="current_page"
    ))
    
    if end_idx < len(all_items):
        nav_buttons.append(types.InlineKeyboardButton(
            text="Вперед ▶️",
            callback_data=f"autoconfirm_items_page_{page+1}"
        ))
    
    if nav_buttons:
        markup.row(*nav_buttons)
    
    back_btn = types.InlineKeyboardButton(
        text="◀️ К настройкам",
        callback_data="autoconfirm_back"
    )
    markup.add(back_btn)
    
    text = f"📦 Выберите товар для настройки:\n\n✅ - сообщение уже настроено\n\nВсего товаров: {len(all_items)}"
    
    if message_id:
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=markup
            )
        except:
            bot.send_message(chat_id, text, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("autoconfirm_items_page_"))
def autoconfirm_items_page_callback(call):
    """Навигация по страницам товаров"""
    page = int(call.data.replace("autoconfirm_items_page_", ""))
    bot.answer_callback_query(call.id)
    show_autoconfirm_items_page(call.message.chat.id, call.from_user.id, page, call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data == "autoconfirm_search")
def autoconfirm_search_callback(call):
    """Поиск товара для настройки"""
    user_states[call.from_user.id] = 'autoconfirm_searching'
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "🔍 Введите название товара для поиска:")


def handle_autoconfirm_search(message):
    """Обработчик поиска товара для автоподтверждения"""
    search_query = message.text.strip().lower()
    
    if len(search_query) < 2:
        bot.reply_to(message, "❌ Запрос слишком короткий. Введите минимум 2 символа.")
        return
    
    # Получаем все товары
    all_items = user_states.get(f"autoconfirm_items_{message.from_user.id}", [])
    
    if not all_items:
        all_items = get_all_active_items()
        user_states[f"autoconfirm_items_{message.from_user.id}"] = all_items
    
    # Фильтруем
    filtered_items = [
        item for item in all_items 
        if search_query in item.name.lower()
    ]
    
    user_states.pop(message.from_user.id, None)
    
    if not filtered_items:
        bot.reply_to(message, f"❌ Товары по запросу '{search_query}' не найдены.")
        return
    
    # Показываем результаты
    markup = types.InlineKeyboardMarkup()
    
    for item in filtered_items[:15]:
        has_message = autoconfirm_settings.get_item_message(item.id) is not None
        prefix = "✅ " if has_message else ""
        btn_text = f"{prefix}{item.name[:40]}"
        btn = types.InlineKeyboardButton(
            text=btn_text,
            callback_data=f"autoconfirm_select_{item.id}"
        )
        markup.add(btn)
    
    back_btn = types.InlineKeyboardButton(
        text="◀️ К списку товаров",
        callback_data="autoconfirm_item"
    )
    markup.add(back_btn)
    
    bot.send_message(
        message.chat.id,
        f"🔍 Найдено товаров: {len(filtered_items)}\n\n✅ - сообщение уже настроено",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("autoconfirm_select_"))
def autoconfirm_select_item_callback(call):
    """Настройка сообщения для выбранного товара"""
    item_id = call.data.replace("autoconfirm_select_", "")
    
    # Находим товар
    cached_items = user_states.get(f"autoconfirm_items_{call.from_user.id}", [])
    selected_item = None
    for item in cached_items:
        if item.id == item_id:
            selected_item = item
            break
    
    if not selected_item:
        bot.answer_callback_query(call.id, text="❌ Товар не найден")
        return
    
    user_states[call.from_user.id] = f'setting_item_{item_id}'
    
    current_msg = autoconfirm_settings.get_item_message(item_id)
    
    text = f"📦 Товар: {selected_item.name}\n\n"
    if current_msg:
        text += f"📝 Текущее сообщение:\n{current_msg}\n\n"
    else:
        text += "📝 Сообщение не установлено.\n\n"
    
    text += "Отправьте новое сообщение для этого товара.\n\n"
    text += "Или отправьте /cancel для отмены.\n"
    text += "Или отправьте /delete для удаления сообщения."
    
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, text)


@bot.callback_query_handler(func=lambda call: call.data == "autoconfirm_view")
def autoconfirm_view_callback(call):
    """Просмотр настроенных товаров"""
    item_messages = autoconfirm_settings.get_all_item_messages()
    
    if not item_messages:
        bot.answer_callback_query(call.id, text="❌ Нет настроенных товаров")
        return
    
    response = "📋 Настроенные товары:\n\n"
    
    for item_id, message in item_messages.items():
        # Пытаемся получить название товара
        try:
            item = playerok_account.get_item(id=item_id)
            item_name = item.name[:30]
        except:
            item_name = f"ID: {item_id[:8]}"
        
        response += f"📦 {item_name}\n"
        response += f"💬 {message[:50]}...\n\n"
    
    markup = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="autoconfirm_back"
    )
    markup.add(back_btn)
    
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, response, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "autoconfirm_back")
def autoconfirm_back_callback(call):
    """Возврат к меню автоподтверждения"""
    bot.answer_callback_query(call.id)
    autoconfirm_command(call.message)


def handle_autoconfirm_message(message):
    """Обработчик сообщений для настройки автоподтверждения"""
    state = user_states.get(message.from_user.id, '')
    
    if message.text == '/cancel':
        user_states.pop(message.from_user.id, None)
        bot.reply_to(message, "❌ Отменено")
        return
    
    # Обработка поиска товара
    if state == 'autoconfirm_searching':
        handle_autoconfirm_search(message)
        return
    
    if state == 'setting_global':
        # Устанавливаем глобальное сообщение
        autoconfirm_settings.set_global_message(message.text)
        user_states.pop(message.from_user.id, None)
        bot.reply_to(message, "✅ Глобальное сообщение установлено!")
        
    elif state.startswith('setting_item_'):
        item_id = state.replace('setting_item_', '')
        
        if message.text == '/delete':
            # Удаляем сообщение для товара
            if autoconfirm_settings.remove_item_message(item_id):
                bot.reply_to(message, "✅ Сообщение для товара удалено!")
            else:
                bot.reply_to(message, "❌ Сообщение не было установлено")
        else:
            # Устанавливаем сообщение для товара
            autoconfirm_settings.set_item_message(item_id, message.text)
            bot.reply_to(message, "✅ Сообщение для товара установлено!")
        
        user_states.pop(message.from_user.id, None)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """Обработчик всех остальных сообщений"""
    # Проверяем, не отвечает ли пользователь в чате
    if message.from_user.id in user_states and user_states[message.from_user.id].startswith('replying_'):
        handle_chat_reply(message)
    # Проверяем, не настраивает ли пользователь автоподтверждение
    elif message.from_user.id in user_states and user_states[message.from_user.id].startswith('setting_'):
        handle_autoconfirm_message(message)
    else:
        bot.reply_to(message, "Используйте /help для просмотра доступных команд.")


def handle_chat_reply(message):
    """Обработчик ответа в чате"""
    try:
        chat_id = user_states[message.from_user.id].replace('replying_', '')
        
        # Отправляем сообщение в чат Playerok с пометкой как прочитанное
        result = playerok_account.send_message(
            chat_id=chat_id, 
            text=message.text,
            mark_chat_as_read=True
        )
        
        # Проверяем что сообщение отправлено
        if result and hasattr(result, 'id'):
            # Создаем inline кнопку для возврата в чат
            markup = types.InlineKeyboardMarkup()
            back_btn = types.InlineKeyboardButton(
                text="💬 Вернуться в чат",
                callback_data=f"open_chat_{chat_id}"
            )
            markup.add(back_btn)
            
            bot.reply_to(
                message, 
                "✅ Сообщение успешно отправлено!\n\nПолучатель увидит его в чате на Playerok.",
                reply_markup=markup
            )
        else:
            bot.reply_to(message, "✅ Сообщение отправлено!")
        
        # Очищаем состояние
        user_states.pop(message.from_user.id, None)
        
        logger.info(f"Сообщение отправлено в чат {chat_id}: {message.text[:50]}")
        
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}")
        bot.reply_to(message, f"❌ Ошибка отправки: {str(e)}\n\nПопробуйте еще раз или проверьте подключение.")
        user_states.pop(message.from_user.id, None)


@bot.message_handler(commands=['chats'])
def chats_command(message):
    """Обработчик команды /chats - получение списка чатов"""
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ У вас нет доступа к этой команде.")
        return
    
    if not playerok_account:
        bot.reply_to(message, "❌ Ошибка: Playerok аккаунт не инициализирован. Проверьте config.py")
        return
    
    try:
        bot.reply_to(message, "⏳ Получаю список чатов...")
        
        # Получаем чаты
        chats = playerok_account.get_chats(count=50)
        
        if not chats or not chats.chats:
            bot.reply_to(message, "💬 У вас пока нет чатов.")
            return
        
        logger.info(f"Получено чатов: {len(chats.chats)}")
        
        # Логируем информацию о первом чате для отладки
        if chats.chats:
            first_chat = chats.chats[0]
            logger.info(f"Первый чат ID: {first_chat.id}, атрибуты: {dir(first_chat)}")
        
        # Сохраняем чаты для пагинации
        user_states[f"chats_{message.from_user.id}"] = chats.chats
        
        markup = create_chats_keyboard(chats.chats, page=0)
        response = f"💬 Ваши чаты ({len(chats.chats)} шт.):\n\nНажмите на чат для просмотра:"
        bot.send_message(message.chat.id, response, reply_markup=markup)
        
        logger.info(f"Пользователь {message.from_user.id} запросил список чатов")
        
    except Exception as e:
        logger.error(f"Ошибка при получении чатов: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Произошла ошибка: {str(e)}")


def create_chats_keyboard(chats, page=0):
    """Создает клавиатуру с чатами и пагинацией"""
    start_idx = page * CHATS_PER_PAGE
    end_idx = start_idx + CHATS_PER_PAGE
    page_chats = chats[start_idx:end_idx]
    
    markup = types.InlineKeyboardMarkup()
    
    for chat in page_chats:
        # Определяем имя чата
        chat_name = None
        
        # Пытаемся получить имя из объекта чата
        if hasattr(chat, 'user') and chat.user and hasattr(chat.user, 'username'):
            chat_name = chat.user.username
        
        # Если не нашли, пытаемся получить из последнего сообщения
        if not chat_name and hasattr(chat, 'last_message') and chat.last_message:
            if hasattr(chat.last_message, 'user') and chat.last_message.user:
                if hasattr(chat.last_message.user, 'id') and chat.last_message.user.id != playerok_account.id:
                    if hasattr(chat.last_message.user, 'username'):
                        chat_name = chat.last_message.user.username
        
        # Формируем текст кнопки
        if chat_name:
            unread = ""
            if hasattr(chat, 'unread_messages_counter') and chat.unread_messages_counter > 0:
                unread = f" ({chat.unread_messages_counter})"
            btn_text = f"💬 {chat_name}{unread}"
        else:
            btn_text = f"💬 Чат {chat.id[:8]}"
        
        btn = types.InlineKeyboardButton(
            text=btn_text,
            callback_data=f"open_chat_{chat.id}"
        )
        markup.add(btn)
    
    # Кнопки навигации
    nav_buttons = []
    
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(
            text="◀️ Назад",
            callback_data=f"chats_page_{page-1}"
        ))
    
    total_pages = (len(chats) + CHATS_PER_PAGE - 1) // CHATS_PER_PAGE
    nav_buttons.append(types.InlineKeyboardButton(
        text=f"📄 {page + 1}/{total_pages}",
        callback_data="current_page"
    ))
    
    if end_idx < len(chats):
        nav_buttons.append(types.InlineKeyboardButton(
            text="Вперед ▶️",
            callback_data=f"chats_page_{page+1}"
        ))
    
    if nav_buttons:
        markup.row(*nav_buttons)
    
    return markup


@bot.callback_query_handler(func=lambda call: call.data.startswith("chats_page_"))
def chats_page_navigation_callback(call):
    """Обработчик навигации по страницам чатов"""
    try:
        page = int(call.data.replace("chats_page_", ""))
        
        cache_key = f"chats_{call.from_user.id}"
        chats = user_states.get(cache_key)
        
        if not chats:
            bot.answer_callback_query(call.id, text="❌ Данные устарели. Обновите список чатов.")
            return
        
        response = f"💬 Ваши чаты ({len(chats)} шт.):\n\nНажмите на чат для просмотра:"
        markup = create_chats_keyboard(chats, page=page)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=response,
            reply_markup=markup
        )
        
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        logger.error(f"Ошибка при навигации по чатам: {e}")
        bot.answer_callback_query(call.id, text="❌ Ошибка при переключении страницы")


@bot.callback_query_handler(func=lambda call: call.data.startswith("open_chat_"))
def open_chat_callback(call):
    """Обработчик открытия чата"""
    try:
        chat_id = call.data.replace("open_chat_", "")
        
        # Получаем сообщения чата (без фильтра по статусу)
        messages = playerok_account.get_chat_messages(chat_id=chat_id, count=20)
        
        if not messages or not messages.messages:
            bot.answer_callback_query(call.id, text="❌ Чат пуст")
            return
        
        # Определяем имя собеседника
        chat_name = "Неизвестный"
        for msg in messages.messages:
            if hasattr(msg, 'user') and msg.user and hasattr(msg.user, 'id') and msg.user.id != playerok_account.id:
                chat_name = msg.user.username if hasattr(msg.user, 'username') else "Неизвестный"
                break
        
        # Словарь для замены системных сообщений
        system_messages = {
            '{{ITEM_PAID}}': '💳 Товар оплачен',
            '{{ITEM_SENT}}': '📦 Товар отправлен',
            '{{DEAL_CONFIRMED}}': '✅ Сделка подтверждена',
            '{{DEAL_ROLLED_BACK}}': '↩️ Возврат средств',
            '{{PROBLEM_REPORTED}}': '⚠️ Сообщено о проблеме',
            '{{PROBLEM_RESOLVED}}': '✅ Проблема решена'
        }
        
        # Формируем текст с последними сообщениями
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        response = f"💬 Чат с {chat_name}\n"
        response += f"🕐 Обновлено: {current_time}\n\n"
        
        # Показываем ВСЕ сообщения (не только последние 10)
        for msg in reversed(messages.messages):
            if hasattr(msg, 'user') and msg.user and hasattr(msg.user, 'id'):
                sender = "Вы" if msg.user.id == playerok_account.id else (msg.user.username if hasattr(msg.user, 'username') else "Неизвестный")
            else:
                sender = "Система"
            
            msg_text = msg.text if hasattr(msg, 'text') and msg.text else "[Нет текста]"
            
            # Заменяем системные сообщения
            for key, value in system_messages.items():
                if key in msg_text:
                    msg_text = msg_text.replace(key, value)
            
            response += f"{sender}: {msg_text}\n\n"
        
        # Кнопки
        markup = types.InlineKeyboardMarkup()
        
        refresh_btn = types.InlineKeyboardButton(
            text="🔄 Обновить",
            callback_data=f"open_chat_{chat_id}"
        )
        reply_btn = types.InlineKeyboardButton(
            text="✍️ Ответить",
            callback_data=f"reply_chat_{chat_id}"
        )
        back_btn = types.InlineKeyboardButton(
            text="◀️ Назад к чатам",
            callback_data="back_to_chats"
        )
        markup.add(refresh_btn)
        markup.add(reply_btn)
        markup.add(back_btn)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=response,
            reply_markup=markup
        )
        
        bot.answer_callback_query(call.id, text="✅ Обновлено")
        
    except Exception as e:
        error_msg = str(e)
        if "message is not modified" in error_msg:
            bot.answer_callback_query(call.id, text="✅ Нет новых сообщений")
        else:
            logger.error(f"Ошибка при открытии чата: {e}")
            bot.answer_callback_query(call.id, text="❌ Ошибка при загрузке чата")


@bot.callback_query_handler(func=lambda call: call.data.startswith("reply_chat_"))
def reply_chat_callback(call):
    """Обработчик кнопки 'Ответить'"""
    chat_id = call.data.replace("reply_chat_", "")
    
    user_states[call.from_user.id] = f'replying_{chat_id}'
    
    bot.answer_callback_query(call.id, text="Напишите сообщение в чат")
    bot.send_message(call.message.chat.id, "✍️ Напишите ваше сообщение:")


@bot.callback_query_handler(func=lambda call: call.data == "back_to_chats")
def back_to_chats_callback(call):
    """Обработчик кнопки 'Назад к чатам'"""
    try:
        cache_key = f"chats_{call.from_user.id}"
        chats = user_states.get(cache_key)
        
        if not chats:
            # Получаем заново
            chats_list = playerok_account.get_chats(count=50)
            if not chats_list or not chats_list.chats:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="💬 У вас пока нет чатов."
                )
                bot.answer_callback_query(call.id)
                return
            chats = chats_list.chats
            user_states[cache_key] = chats
        
        response = f"💬 Ваши чаты ({len(chats)} шт.):\n\nНажмите на чат для просмотра:"
        markup = create_chats_keyboard(chats, page=0)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=response,
            reply_markup=markup
        )
        
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        logger.error(f"Ошибка при возврате к чатам: {e}")
        bot.answer_callback_query(call.id, text="❌ Ошибка при загрузке чатов")


def main():
    """Запуск бота"""
    logger.info("Бот запущен...")
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        if playerok_listener:
            playerok_listener.stop()


if __name__ == '__main__':
    main()
