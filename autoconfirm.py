import json
import os
import time

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
                return {
                    'enabled': False, 
                    'global_message': None, 
                    'item_messages': {},
                    'auto_restore': {
                        'enabled': False,
                        'photo_groups': {}
                    }
                }
        return {
            'enabled': False, 
            'global_message': None, 
            'item_messages': {},
            'auto_restore': {
                'enabled': False,
                'photo_groups': {}
            }
        }
    
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
    
    # Методы для автовосстановления товаров
    
    def is_auto_restore_enabled(self):
        """Проверка, включено ли автовосстановление"""
        return self.settings.get('auto_restore', {}).get('enabled', False)
    
    def enable_auto_restore(self):
        """Включить автовосстановление"""
        if 'auto_restore' not in self.settings:
            self.settings['auto_restore'] = {'enabled': False, 'photo_groups': {}}
        self.settings['auto_restore']['enabled'] = True
        self.save()
    
    def disable_auto_restore(self):
        """Выключить автовосстановление"""
        if 'auto_restore' not in self.settings:
            self.settings['auto_restore'] = {'enabled': False, 'photo_groups': {}}
        self.settings['auto_restore']['enabled'] = False
        self.save()
    
    def create_photo_group(self, item_ids, photo_path):
        """Создать группу товаров с общим фото"""
        if 'auto_restore' not in self.settings:
            self.settings['auto_restore'] = {'enabled': False, 'photo_groups': {}}
        
        group_id = f"group_{int(time.time())}"
        self.settings['auto_restore']['photo_groups'][group_id] = {
            'photo_path': photo_path,
            'item_ids': item_ids
        }
        self.save()
        return group_id
    
    def get_photo_for_item(self, item_id):
        """Получить путь к фото для товара"""
        photo_groups = self.settings.get('auto_restore', {}).get('photo_groups', {})
        
        for group_id, group_data in photo_groups.items():
            if item_id in group_data.get('item_ids', []):
                return group_data.get('photo_path')
        
        return None
    
    def get_all_photo_groups(self):
        """Получить все группы товаров с фото"""
        return self.settings.get('auto_restore', {}).get('photo_groups', {})
    
    def delete_photo_group(self, group_id):
        """Удалить группу товаров"""
        if 'auto_restore' in self.settings and 'photo_groups' in self.settings['auto_restore']:
            if group_id in self.settings['auto_restore']['photo_groups']:
                # Удаляем файл фото
                photo_path = self.settings['auto_restore']['photo_groups'][group_id].get('photo_path')
                if photo_path and os.path.exists(photo_path):
                    try:
                        os.remove(photo_path)
                    except:
                        pass
                
                del self.settings['auto_restore']['photo_groups'][group_id]
                self.save()
                return True
        return False
    
    def remove_item_from_groups(self, item_id):
        """Удалить товар из всех групп"""
        if 'auto_restore' not in self.settings:
            return
        
        photo_groups = self.settings['auto_restore'].get('photo_groups', {})
        groups_to_delete = []
        
        for group_id, group_data in photo_groups.items():
            if item_id in group_data.get('item_ids', []):
                group_data['item_ids'].remove(item_id)
                
                # Если группа пустая, помечаем на удаление
                if not group_data['item_ids']:
                    groups_to_delete.append(group_id)
        
        # Удаляем пустые группы
        for group_id in groups_to_delete:
            self.delete_photo_group(group_id)
        
        if not groups_to_delete:
            self.save()
