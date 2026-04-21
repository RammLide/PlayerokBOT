import json
import os

class AutoConfirmSettings:
    """Класс для управления настройками автоподтверждения"""
    
    def __init__(self, filename='autoconfirm_settings.json'):
        self.filename = filename
        self.settings = self.load()
    
    def load(self):
        """Загрузка настроек из файла"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {'enabled': False, 'global_message': None, 'item_messages': {}}
        return {'enabled': False, 'global_message': None, 'item_messages': {}}
    
    def save(self):
        """Сохранение настроек в файл"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)
    
    def is_enabled(self):
        """Проверка, включено ли автоподтверждение"""
        return self.settings.get('enabled', False)
    
    def enable(self):
        """Включить автоподтверждение"""
        self.settings['enabled'] = True
        self.save()
    
    def disable(self):
        """Выключить автоподтверждение"""
        self.settings['enabled'] = False
        self.save()
    
    def set_global_message(self, message):
        """Установить глобальное сообщение для всех товаров"""
        self.settings['global_message'] = message
        self.save()
    
    def get_global_message(self):
        """Получить глобальное сообщение"""
        return self.settings.get('global_message')
    
    def set_item_message(self, item_id, message):
        """Установить сообщение для конкретного товара"""
        if 'item_messages' not in self.settings:
            self.settings['item_messages'] = {}
        self.settings['item_messages'][item_id] = message
        self.save()
    
    def get_item_message(self, item_id):
        """Получить сообщение для конкретного товара"""
        return self.settings.get('item_messages', {}).get(item_id)
    
    def remove_item_message(self, item_id):
        """Удалить сообщение для конкретного товара"""
        if 'item_messages' in self.settings and item_id in self.settings['item_messages']:
            del self.settings['item_messages'][item_id]
            self.save()
            return True
        return False
    
    def get_message_for_item(self, item_id):
        """
        Получить сообщение для товара с учетом приоритета:
        1. Сообщение для конкретного товара
        2. Глобальное сообщение
        """
        # Приоритет: конкретный товар > все товары
        item_message = self.get_item_message(item_id)
        if item_message:
            return item_message
        
        return self.get_global_message()
    
    def get_all_item_messages(self):
        """Получить все настроенные сообщения для товаров"""
        return self.settings.get('item_messages', {})
