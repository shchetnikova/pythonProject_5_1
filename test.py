from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import KeyboardButton, BotCommand, ReplyKeyboardMarkup, BotCommandScopeChat, BotCommandScopeDefault
import os  # Импорт модуля os для работы с ОС
import logging  # Импорт модуля logging для логирования
import psycopg2  # Импорт модуля psycopg2 для работы с PostgreSQL


bot_token = os.getenv('API_TOKEN')  # Получение токена бота из переменных окружения
bot = Bot(token=bot_token)  # Создание бота с токеном, который выдал в BotFather при регистрации бота
dp = Dispatcher(bot, storage=MemoryStorage())  #Инициализация диспетчера команд
logging.basicConfig(level=logging.INFO)  # Активация системы логирования
saved_state_global = {}  # Создание словаря для хранения состояний


def ADMIN_ID():
    # Подключение к базе данных
    conn = psycopg2.connect(
        host="localhost",
        database="RPP",
        user="postgres",
        password="postgres",
        port="5432"
    )
    cursor = conn.cursor()
    # Выполнение запроса к таблице Admins
    cursor.execute("SELECT chat_id FROM Admins LIMIT 1")
    admin_chat_id = cursor.fetchone()[0]
    # Закрытие соединения с базой данных
    cursor.close()
    conn.close()
    return admin_chat_id


admins = ADMIN_ID()


admin_commands = [
    BotCommand(command="/manage_currency", description="MANAGE CURRENCY"),  # Команда для управления валютой
    BotCommand(command="/start", description="START"),  # Команда для начала использования бота
    BotCommand(command="/get_currencies", description="GET CURRENCIES"),  # Команда для получения списка валют
    BotCommand(command="/convert", description="CONVERT")  # Команда для конвертации валюты
]

user_commands = [
    BotCommand(command="/start", description="START"),  # Команда для начала использования бота (пользовательская версия)
    BotCommand(command="/get_currencies", description="GET CURRENCIES"),  # Команда для получения списка валют (пользовательская версия)
    BotCommand(command="/convert", description="CONVERT")  # Команда для конвертации валюты (пользовательская версия)
]


# Создание класса для управления состояний процессов
class ManageStateGroup(StatesGroup):
    Add_currency_name_state = State()  # Состояние: Добавление названия валюты
    Add_currency_rate_state = State()  # Состояние: Добавление курса валюты
    Edit_currency_name_state = State()  # Состояние: Редактирование названия валюты
    Edit_currency_rate_state = State()  # Состояние: Редактирование курса валюты
    Delete_currency_state = State()  # Состояние: Удаление валюты


# Создание класса для управления состояний convert
class Step2(StatesGroup):
    currency_name2 = State()  # Состояние: Название валюты (Шаг 2)
    amount = State()  # Состояние: Сумма (Шаг 2)


# Функция для установления команд
async def setup_bot_commands(dispatcher: Dispatcher):
    await bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())  # Установка пользовательских команд для бота по умолчанию

    for admin in admins:
        await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=admins))  # Установка команд для админа с указанным chat_id


add_currency = KeyboardButton(text='Добавить валюту')  # Кнопка для добавления валюты
delete_currency = KeyboardButton(text='Удалить валюту')  # Кнопка для удаления валюты
change_rate = KeyboardButton(text='Изменить валюту')  # Кнопка для изменения валюты

markup = ReplyKeyboardMarkup(resize_keyboard=True).row(add_currency, delete_currency, change_rate)  # Создание разметки клавиатуры с кнопками


# Функция, которая загружает курсы валют из базы данных PostgreSQL
def get_currency_rates():
    conn = psycopg2.connect(
        host="localhost",
        database="RPP",
        user="postgres",
        password="postgres",
        port="5432"
    )  # Установление соединения с базой данных PostgreSQL
    cursor = conn.cursor()  # Создание курсора для выполнения SQL-запросов
    cursor.execute("SELECT currency_name, rate FROM currencies")  # Выполнение SQL-запроса для получения курсов валют
    rows = cursor.fetchall()  # Получение всех результатов запроса
    conn.close()  # Закрытие соединения с базой данных
    logging.info(rows)  # Логирование результатов запроса
    return rows  # Возврат полученных курсов валют


#Обработчик команды start
@dp.message_handler(commands=['start'])  # Получение чат-id пользователя, который прислал сообщение
async def add_chat_id(message: types.Message):
    await message.reply("Добро пожаловать в бота")
    chat_id = message.chat.id


def add_chat_id(chat_id):
    conn = psycopg2.connect(
        host="localhost",
        database="RPP",
        user="postgres",
        password="postgres",
        port="5432"
        )
    cursor = conn.cursor()
    cursor.execute("""insert into admin (id, chat_id) VALUES  (:id, :chat_id) """,
                   {"id": id, "chat_id": chat_id})  # Вставка значения id и chat_id в таблицу admin


#Обработчик команды get_currencies
@dp.message_handler(commands=['get_currencies'])
async def viewing_recorded_currencies(message: types.Message):
    currencies = get_currency_rates()  # Получение курсов валют
    response = ""
    if currencies:
        response = "Курсы валют к рублю:\n"
        for rate in currencies:
            response += f"{rate[0]}: {rate[1]} руб.\n"  # Формирование строки с курсом валюты
    else:
        response = "Курсы валют не найдены"
    await bot.send_message(message.chat.id, response)  # Отправка сообщения с курсами валют


# Обработка сообщения с помощью регулярного выражения "^Добавить валюту$"
@dp.message_handler(regexp=r"^Добавить валюту$")
async def add_currency_command(message: types.Message):
    await ManageStateGroup.Add_currency_name_state.set()  # Установка состояния для добавления имени валюты
    await message.reply("Введите название валюты")  # Отправка ответного сообщения с просьбой ввести название валюты


# Обработка сообщения с помощью регулярного выражения "^Удалить валюту$"
@dp.message_handler(regexp=r"^Удалить валюту$")
async def command_delete_currency(message: types.Message):
    await message.reply("Введите название валюты, которую вы хотите удалить")  # Отправка ответного сообщения с просьбой ввести название валюты для удаления
    await ManageStateGroup.Delete_currency_state.set()  # Установка состояния для удаления валюты


#Объявление функции обработчика сообщений с состоянием Delete_currency_state
@dp.message_handler(state=ManageStateGroup.Delete_currency_state)
async def process_delete_currency(message: types.Message, state: FSMContext):
    currency_name = message.text  # Получение названия валюты из сообщения пользователя
    try:
        delete_currency_in_database(currency_name=currency_name)  # Удаление валюты из базы данных
        await message.answer("Валюта удалена")  # Отправка ответного сообщения об успешном удалении валюты
    except Exception as e:
        logging.error("Ошибка удаления из БД", e)
        error_message = e.args[0] if len(e.args) > 0 else "Причина неизвестна"
        await message.answer(f"Валюту не удалось удалить: {error_message}")  # Отправка ответного сообщения с информацией об ошибке удаления валюты
    finally:
        await state.finish()  # Завершение текущего состояния


# Функция для удаления валюты из базы данных
def delete_currency_in_database(currency_name: str):
    conn = psycopg2.connect(
        host="localhost",
        database="RPP",
        user="postgres",
        password="postgres",
        port="5432"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM currencies WHERE currency_name = %(currency_name)s", {"currency_name": currency_name}) # Выполнение SQL-запроса для поиска валюты по названию
    found_currencies = cursor.fetchall()  # Получение результатов запроса

    if len(found_currencies) == 0:  # Если валюта не найдена
        raise Exception("Валюты не существует")  # Генерация исключения с сообщением о несуществующей валюте

    cursor.execute(
        "DELETE FROM currencies WHERE currency_name = %(currency_name)s", {"currency_name": currency_name}  # Выполнение SQL-запроса для удаления валюты по названию
    )
    conn.commit()  # Применение изменений в базе данных
    conn.close()  # Закрытие соединения с базой данных


# Обработка сообщения с помощью регулярного выражения "^Изменить валюту$"
@dp.message_handler(regexp=r"^Изменить валюту$")
async def command_edit_currency(message: types.Message):
    await message.reply("Введите название валюты, которую вы хотите изменить")  # Отправка сообщения пользователю с просьбой ввести название валюты для изменения
    await ManageStateGroup.Edit_currency_name_state.set()  # Установка состояния для получения названия валюты


#Объявление функции обработчика сообщений с состоянием Edit_currency_name_state
@dp.message_handler(state=ManageStateGroup.Edit_currency_name_state)
async def command_edit_currency(message: types.Message, state: FSMContext):
    await message.reply("Введите новый курс валюты")  # Отправка сообщения пользователю с просьбой ввести новый курс валюты
    await state.update_data(currency_name=message.text)  # Обновление данных состояния с указанием названия валюты
    await ManageStateGroup.Edit_currency_rate_state.set()  # Установка состояния для получения нового курса валюты


#Объявление функции обработчика сообщений с состоянием Edit_currency_rate_state
@dp.message_handler(state=ManageStateGroup.Edit_currency_rate_state)
async def process_edit_currency(message: types.Message, state: FSMContext):
    state_data = await state.get_data() # Получение данных состояния
    rate = message.text  # Получение нового курса валюты из сообщения пользователя
    try:
        edit_currency_in_database(currency_name=state_data['currency_name'], rate=rate)  # Вызов функции для изменения курса валюты в базе данных
        await message.answer("Курс валюты изменен")  # Отправка ответного сообщения о успешном изменении курса валюты
        # saved_state_global['rate'] = rate  # Обновление сохраненного значения курса валюты
    except Exception as e:
        logging.error("Ошибка взаимодействия с БД", e)  # Логирование ошибки взаимодействия с базой данных
        error_message = e.args[0] if len(e.args) > 0 else "Причина неизвестна"  # Получение сообщения об ошибке
        await message.answer(f"Не удалось изменить курс валюты: {error_message}")  # Отправка сообщения с информацией об ошибке
    finally:
        await state.finish()  # Завершение текущего состояния


# Функция для обновления валюты в базе данных
def edit_currency_in_database(currency_name: str, rate: float):
    conn = psycopg2.connect(
            host="localhost",
            database="RPP",
            user="postgres",
            password="postgres",
            port="5432"
        )
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM currencies WHERE currency_name = %(currency_name)s", {"currency_name": currency_name})
    found_currencies = cursor.fetchall()

    if len(found_currencies) == 0: # Если валюта не найдена
        raise Exception("Валюты не существует") # Генерация исключения с сообщением о несуществующей валюте

    cursor.execute(
        "UPDATE currencies SET rate=%(rate)s WHERE currency_name=%(currency_name)s",
        {"currency_name": currency_name, "rate": rate}  # Выполнение SQL-запроса для обновления курса валюты
    )
    conn.commit()  # Применение изменений в базе данных
    conn.close()  # Закрытие соединения с базой данных


#Объявление функции обработчика сообщений с состоянием Add_currency_name_state
@dp.message_handler(state=ManageStateGroup.Add_currency_name_state)
async def process_currency(message: types.Message, state: FSMContext):
    await state.update_data(currency_name=message.text)  # Обновление данных состояния с указанием названия валюты
    user_data = await state.get_data()  # Получение данных состояния
    await ManageStateGroup.Add_currency_rate_state.set()  # Установка состояния для получения курса валюты
    await message.reply("Введите курс валюты к рублю")  # Отправка сообщения пользователю с просьбой ввести курс валюты


# Функция для добавления новой валюты и ее курса в базу данных
def add_currency_in_database(currency_name: str, rate: float):
    conn = psycopg2.connect(
            host="localhost",
            database="RPP",
            user="postgres",
            password="postgres",
            port="5432"
        )
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM currencies WHERE currency_name = %(currency_name)s", {"currency_name": currency_name})
    found_currencies = cursor.fetchall()

    if len(found_currencies) > 0:
        raise Exception("Валюта уже существует")  # Если найдены валюты с указанным названием, генерируется исключение

    cursor.execute(
        "INSERT INTO currencies(currency_name, rate) VALUES (%(currency_name)s, %(rate)s)",
        {
            "currency_name": currency_name,
            "rate": rate
        }  # Выполнение SQL-запроса для добавления новой валюты в базу данных
    )
    conn.commit()  # Применение изменений в базе данных
    conn.close()  # Закрытие соединения с базой данных


#Объявление функции обработчика сообщений с состоянием Add_currency_rate_state
@dp.message_handler(state=ManageStateGroup.Add_currency_rate_state)
async def process_rate(message: types.Message, state: FSMContext):
    await state.update_data(rate=message.text)  # Обновление данных состояния с указанием курса валюты
    user_data = await state.get_data()  # Получение данных состояния
    # saved_state_global = user_data  # Обновление сохраненного состояния

    try:
        add_currency_in_database(currency_name=user_data['currency_name'], rate=user_data['rate'])  # Вызов функции для добавления валюты в базу данных
        await message.reply("Курс валюты сохранен")  # Отправка сообщения о успешном сохранении курса валюты
    except Exception as e:
        logging.error("Ошибка записи в БД", e)  # Логирование ошибки записи в базу данных
        error_message = e.args[0] if len(e.args) > 0 else "Причина неизвестна"  # Получение сообщения об ошибке
        await message.reply(f"Курс валюты не удалось сохранить: {error_message}")  # Отправка сообщения с информацией об ошибке
    finally:
        await state.finish()  # Завершение текущего состояния


#Обработчик команды convert
@dp.message_handler(commands=['convert'])
async def start_command2(message: types.Message):
    await Step2.currency_name2.set()  # Установка состояния "currency_name2"
    await message.reply("Введите название валюты")  # Отправка сообщения с просьбой ввести название валюты


#Объявление функции обработчика сообщений с состоянием currency_name2
@dp.message_handler(state=Step2.currency_name2)
async def process_currency2(message: types.Message, state: FSMContext):
    await state.update_data(currency_name2=message.text)  # Обновление данных состояния с указанием названия валюты
    # user_data = await state.get_data()  # Получение данных состояния
    await Step2.amount.set()  # Установка состояния "amount"
    await message.reply("Введите сумму в указанной валюте")  # Отправка сообщения с просьбой ввести сумму в указанной валюте


#Объявление функции обработчика сообщений с состоянием amount
@dp.message_handler(state=Step2.amount)
async def process_convert(message: types.Message, state: FSMContext):
    conn = psycopg2.connect(
            host="localhost",
            database="RPP",
            user="postgres",
            password="postgres",
            port="5432"
        )

    await state.update_data(amount=message.text)  # Обновление данных состояния с указанием суммы
    user_data = await state.get_data()  # Получение данных состояния
    # todo сделать получение курса из БД
    # получение данных (курс) из таблички с помощью user_data['currency_name2']
    cursor = conn.cursor()
    # Выполнение запроса к таблице Admins
    cursor.execute("SELECT rate FROM currencies where currency_name = %(currency_name2)s", {"currency_name2": user_data['currency_name2']})
    user_data2 = cursor.fetchone()[0]
    # Закрытие соединения с базой данных
    cursor.close()
    conn.close()
    await state.finish()

    await message.reply(float(user_data['amount']) * float(user_data2))  # Выполнение конвертации и отправка результата


#Обработчик команды manage_currency
@dp.message_handler(commands=['manage_currency'])
async def process_manage_currency(message: types.Message):
    await message.reply(text="Выберите операцию из доступных", reply_markup=markup)  # Отправка сообщения с выбором операции


# Точка входа в приложение
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)  # Настройка логирования
    dp.middleware.setup(LoggingMiddleware())  # Подключение системы логирования к боту
    executor.start_polling(dp, skip_updates=True, on_startup=setup_bot_commands)  # Запуск бота