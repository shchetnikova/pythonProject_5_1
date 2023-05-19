import sqlite3
#создание соединения с бд (в скобках название бд)
conn = sqlite3.connect('users')
#создаем таблицу пользователей
def create_table_users():
    conn = sqlite3.connect('users')
    #создаем курсор, который будет использоваться для выполнения запросов к базе данных SQLite
    cursor = conn.cursor()
    #выполняем запросы к базе данных SQLite, используя метод execute()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL
                    )""")
    #если не вызывается метод conn.commit(),
    #изменения в базе данных не будут сохранены и будут потеряны при закрытии
    #соединения или перезапуске приложения.
    conn.commit()
    #закончив работу с базой данных, закрываем соединение
    conn.close()

    #добавление полей
def add_user(name, email):
    conn = sqlite3.connect('users')
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO users (name, email)
                    VALUES (?, ?)""", (name, email))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('users')
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM users""")
    #присваивание переменной `rows` результата выполнения запроса, который был выполнен
    #с помощью объекта `cursor`.
    #В этом случае, `rows` будет содержать все строки, возвращенные из базы данных в
    #качестве результата выполнения запроса.
    rows = cursor.fetchall()
    #цикл `for` проходит по списку строк `rows`, и для каждой строки выполняется команда `print(row)`,
    #которая выводит содержание этой строки на экран. В итоге, на экран будут выведены все строки таблицы.
    for row in rows:
        print(row)
    conn.close()

def get_user_by_id(user_id):
    conn = sqlite3.connect('users')
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM users WHERE id = ?""", (user_id,))
    #строки = метод объекта `cursor` в Python, который используется
    #для выбора всех строк из результата запроса к базе данных.
    row = cursor.fetchone()
    print(row)
    conn.close()

def delete_user_by_id(user_id):
    conn = sqlite3.connect('users')
    cursor = conn.cursor()
    cursor.execute("""DELETE FROM users WHERE id = ?""", (user_id,))
    conn.commit()
    conn.close()
def delete_user_by_name(name):
    conn = sqlite3.connect('users')
    cursor = conn.cursor()
    cursor.execute("""DELETE FROM users WHERE name = ?""", (name,))
    conn.commit()
    conn.close()
def main():
    create_table_users()
    #добавляем пользователей
    add_user('Семен Семеныч', 'Semen@mail.com')
    add_user('Артем Артемов', 'Artem@mail.com')
    add_user('Максим Максимович', 'Maksim@mail.com')
 #выводим всех пользователей
    print("Все пользователи:")
    get_all_users()

#получаем пользователя по id и выводим информацию о нем
    print("Пользователь с id = 3:")
    get_user_by_id(3)
 #удаляем пользователя по id
    delete_user_by_id(3)
 #выводим всех пользователей после удаления
    print("Все пользователи после удаления:")
    get_all_users()
    delete_user_by_name('Артем Артемов')
    print("Все пользователи после удаления:")
    get_all_users()



#проверяет, запущен ли скрипт непосредственно (как главный модуль),
#или он был импортирован как модуль в другой скрипт.
#Если скрипт запущен непосредственно (то есть как главный модуль),
#то выполняется функция main().
#Если же скрипт был импортирован как модуль в другой скрипт, то функция main() не выполнится автоматически.
if __name__ == "__main__":
    main()