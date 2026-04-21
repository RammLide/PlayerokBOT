import threading
import logging
from playerokapi.listener.listener import EventListener
from playerokapi.enums import EventTypes, ItemDealStatuses

logger = logging.getLogger(__name__)


class PlayerokListener:
    """Класс для прослушивания событий Playerok"""
    
    def __init__(self, account, bot, admin_ids, autoconfirm_settings=None):
        self.account = account
        self.bot = bot
        self.admin_ids = admin_ids
        self.autoconfirm_settings = autoconfirm_settings
        self.listener = EventListener(account)
        self.running = False
        self.thread = None
    
    def start(self):
        """Запуск слушателя в отдельном потоке"""
        if self.running:
            logger.warning("Слушатель уже запущен")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._listen, daemon=True)
        self.thread.start()
        logger.info("Слушатель событий Playerok запущен")
    
    def stop(self):
        """Остановка слушателя"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Слушатель событий Playerok остановлен")
    
    def _listen(self):
        """Основной цикл прослушивания событий"""
        try:
            for event in self.listener.listen():
                if not self.running:
                    break
                
                self._handle_event(event)
        except Exception as e:
            logger.error(f"Ошибка в слушателе событий: {e}")
            if self.running:
                # Перезапуск слушателя при ошибке
                logger.info("Перезапуск слушателя...")
                self._listen()
    
    def _handle_event(self, event):
        """Обработка события"""
        try:
            if event.type == EventTypes.NEW_MESSAGE:
                self._handle_new_message(event)
            elif event.type == EventTypes.NEW_DEAL:
                self._handle_new_deal(event)
            elif event.type == EventTypes.DEAL_CONFIRMED:
                self._handle_deal_confirmed(event)
            elif event.type == EventTypes.DEAL_CONFIRMED_AUTOMATICALLY:
                self._handle_deal_confirmed_auto(event)
            elif event.type == EventTypes.NEW_REVIEW:
                self._handle_new_review(event)
            elif event.type == EventTypes.ITEM_PAID:
                self._handle_item_paid(event)
            elif event.type == EventTypes.DEAL_HAS_PROBLEM:
                self._handle_deal_problem(event)
        except Exception as e:
            logger.error(f"Ошибка при обработке события {event.type}: {e}")
    
    def _handle_new_message(self, event):
        """Обработка нового сообщения"""
        # Игнорируем свои сообщения
        if event.message.user.id == self.account.id:
            return
        
        message_text = (
            f"💬 Новое сообщение\n\n"
            f"От: {event.message.user.username}\n"
            f"Чат ID: {event.chat.id}\n\n"
            f"Сообщение:\n{event.message.text}"
        )
        
        self._send_to_admins(message_text, chat_id=event.chat.id)
    
    def _handle_new_deal(self, event):
        """Обработка новой покупки"""
        message_text = (
            f"🛒 Новая покупка!\n\n"
            f"Товар: {event.deal.item.name if hasattr(event.deal, 'item') else 'N/A'}\n"
            f"Сумма: {event.deal.amount if hasattr(event.deal, 'amount') else 'N/A'} ₽\n"
            f"Покупатель: {event.deal.buyer.username if hasattr(event.deal, 'buyer') else 'N/A'}\n"
            f"Сделка ID: {event.deal.id}"
        )
        
        self._send_to_admins(message_text)
    
    def _handle_deal_confirmed(self, event):
        """Обработка подтверждения сделки"""
        message_text = (
            f"✅ Сделка подтверждена\n\n"
            f"Товар: {event.deal.item.name if hasattr(event.deal, 'item') else 'N/A'}\n"
            f"Сумма: {event.deal.amount if hasattr(event.deal, 'amount') else 'N/A'} ₽\n"
            f"Сделка ID: {event.deal.id}"
        )
        
        self._send_to_admins(message_text)
    
    def _handle_deal_confirmed_auto(self, event):
        """Обработка автоматического подтверждения сделки"""
        message_text = (
            f"✅ Сделка подтверждена автоматически\n\n"
            f"Товар: {event.deal.item.name if hasattr(event.deal, 'item') else 'N/A'}\n"
            f"Сумма: {event.deal.amount if hasattr(event.deal, 'amount') else 'N/A'} ₽\n"
            f"Сделка ID: {event.deal.id}"
        )
        
        self._send_to_admins(message_text)
    
    def _handle_new_review(self, event):
        """Обработка нового отзыва"""
        message_text = (
            f"⭐ Новый отзыв\n\n"
            f"От: {event.review.user.username if hasattr(event.review, 'user') else 'N/A'}\n"
            f"Оценка: {'⭐' * (event.review.rating if hasattr(event.review, 'rating') else 0)}\n"
            f"Текст: {event.review.text if hasattr(event.review, 'text') else 'N/A'}"
        )
        
        self._send_to_admins(message_text)
    
    def _handle_item_paid(self, event):
        """Обработка оплаты товара"""
        message_text = (
            f"💳 Товар оплачен\n\n"
            f"Товар: {event.deal.item.name if hasattr(event.deal, 'item') else 'N/A'}\n"
            f"Сумма: {event.deal.amount if hasattr(event.deal, 'amount') else 'N/A'} ₽\n"
            f"Сделка ID: {event.deal.id}"
        )
        
        self._send_to_admins(message_text)
        
        # Автоподтверждение заказа
        if self.autoconfirm_settings and self.autoconfirm_settings.is_enabled():
            try:
                # Получаем ID товара
                item_id = event.deal.item.id if hasattr(event.deal, 'item') and hasattr(event.deal.item, 'id') else None
                
                if item_id:
                    # Получаем сообщение для товара (с учетом приоритета)
                    custom_message = self.autoconfirm_settings.get_message_for_item(item_id)
                    
                    # Подтверждаем сделку (статус SENT = товар отправлен)
                    self.account.update_deal(deal_id=event.deal.id, new_status=ItemDealStatuses.SENT)
                    logger.info(f"Автоподтверждение: сделка {event.deal.id} подтверждена")
                    
                    # Отправляем сообщение покупателю, если настроено
                    if custom_message and hasattr(event, 'chat') and event.chat:
                        self.account.send_message(
                            chat_id=event.chat.id,
                            text=custom_message,
                            mark_chat_as_read=True
                        )
                        logger.info(f"Автоподтверждение: сообщение отправлено в чат {event.chat.id}")
                    
                    # Уведомляем админов
                    admin_msg = f"✅ Автоподтверждение выполнено\n\nСделка ID: {event.deal.id}"
                    if custom_message:
                        admin_msg += f"\n\nОтправлено сообщение:\n{custom_message[:100]}"
                    self._send_to_admins(admin_msg)
                    
            except Exception as e:
                logger.error(f"Ошибка автоподтверждения: {e}")
                error_msg = f"❌ Ошибка автоподтверждения\n\nСделка ID: {event.deal.id}\nОшибка: {str(e)}"
                self._send_to_admins(error_msg)
    
    def _handle_deal_problem(self, event):
        """Обработка проблемы в сделке"""
        message_text = (
            f"⚠️ Проблема в сделке\n\n"
            f"Товар: {event.deal.item.name if hasattr(event.deal, 'item') else 'N/A'}\n"
            f"Сделка ID: {event.deal.id}\n"
            f"Описание: {event.problem.description if hasattr(event, 'problem') else 'N/A'}"
        )
        
        self._send_to_admins(message_text)
    
    def _send_to_admins(self, text, chat_id=None):
        """Отправка уведомления всем администраторам"""
        from telebot import types as tg_types
        
        for admin_id in self.admin_ids:
            try:
                # Добавляем кнопки если это сообщение из чата
                if chat_id:
                    markup = tg_types.InlineKeyboardMarkup()
                    view_btn = tg_types.InlineKeyboardButton(
                        text="📖 Открыть чат",
                        callback_data=f"open_chat_{chat_id}"
                    )
                    markup.add(view_btn)
                    self.bot.send_message(admin_id, text, reply_markup=markup)
                else:
                    self.bot.send_message(admin_id, text)
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления админу {admin_id}: {e}")
