# 🔙 Руководство по кнопкам "Назад" в боте

## ✅ **Что добавлено:**

Теперь во всех FSM состояниях (когда бот ожидает ввода данных) есть возможность отменить действие:

### 🎯 **Как использовать:**

1. **Текстовые команды:** Напишите `назад` или `отмена`
2. **Кнопка:** Нажмите кнопку "Назад" под сообщением

### 📋 **Где работает:**

#### 👤 **Создание/редактирование профиля:**
- Ввод имени → `назад` → отмена создания
- Ввод возраста → `назад` → отмена создания  
- Ввод пола → `назад` → отмена создания
- Ввод веса → `назад` → отмена создания
- Ввод роста → `назад` → отмена создания
- Ввод активности → `назад` → отмена создания

#### 🍽️ **Добавление еды:**
- Ввод названия и веса → `назад` → отмена добавления

#### 💧 **Трекер воды:**
- Ввод количества мл → `назад` → отмена добавления

#### 📝 **Создание шаблонов:**
- Ввод названия шаблона → `назад` → отмена создания
- Ввод блюд → `назад` → отмена создания
- Простой формат → `назад` → отмена создания

#### 📊 **Трекер жировой массы:**
- Ввод обхвата талии → `назад` → отмена измерения
- Ввод обхвата бедер → `назад` → отмена измерения  
- Ввод обхвата шеи → `назад` → отмена измерения
- Ввод целевого % жира → `назад` → отмена измерения

### 🎨 **UX улучшения:**

- ✅ **Кнопка "Назад"** под каждым сообщением с запросом данных
- ✅ **Текстовые команды** `назад` и `отмена` работают везде
- ✅ **Автоматический возврат** в главное меню после отмены
- ✅ **Очистка состояния** FSM при отмене

### 💡 **Примеры использования:**

```
Бот: "Введите ваш возраст (число):"
Пользователь: "назад"
Бот: "Создание профиля отменено" [главное меню]

Бот: "Введите количество мл, которое вы выпили:"
Пользователь: "отмена" 
Бот: "Действие отменено" [главное меню]
```

### 🔧 **Техническая реализация:**

- Добавлена проверка `message.text.lower() in ['отмена', 'назад']` во все FSM обработчики
- Добавлена кнопка `back_kb` под всеми сообщениями с запросом данных
- Автоматическая очистка состояния FSM при отмене
- Возврат в главное меню с соответствующей клавиатурой

---

**Теперь пользователь всегда может отменить любое действие и вернуться в главное меню!** 🎉 