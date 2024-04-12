import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message, LabeledPrice
from config import BOT_TOKEN, PAYMENT_TOKEN, ADMIN_ID
from aiogram.utils import markdown, executor
from functools import partial
from aiogram.types.message import ContentType
from aiogram.types.pre_checkout_query import PreCheckoutQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from io import BytesIO
import time
from datetime import datetime
#from aiogram.fsm.context import FSMContext
#from aiogram.dispatcher.storage import MemoryStorage


storage = MemoryStorage()

# Создаем подключение к базе данных
conn = sqlite3.connect('products.db')
cursor = conn.cursor()


conn_users = sqlite3.connect('users.db')
cursor_users = conn_users.cursor()
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# loop = asyncio.get_event_loop()

conn_orders = sqlite3.connect('orders.db')
cursor_orders = conn_orders.cursor()

# Объект бота
bot = Bot(token=BOT_TOKEN)

# Диспетчер
dp = Dispatcher(bot=bot,storage=storage)


class AdminState(StatesGroup):
    choose_product = State()  # Состояние для выбора товара администратором
    change_quantity = State()  # Состояние для изменения количества товара

class RegisterState(StatesGroup):
    first_name = State()     # Состояние для ввода фамилии
    last_name = State()      # Состояние для ввода имени
    patronymic = State()     # Состояние для ввода отчества (если нужно)

async def get_menu_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    cursor.execute('SELECT id, name FROM products')
    products = cursor.fetchall()
    for product in products:
        product_id, product_name = product
        button = InlineKeyboardButton(product_name, callback_data=str(product_id))
        markup.insert(button)
    return markup














# @dp.callback_query_handler(lambda c: c.data.startswith('decrease'))
# async def decrease_product_quantit(product_id):
#     cursor.execute('UPDATE products SET quantity = quantity - 1 WHERE id = ?', (product_id,))
#     conn.commit()





# async def decrease_kb():
#     markup = InlineKeyboardMarkup(row_width=2)
#     btn_decrease = InlineKeyboardButton('-1', callback_data='decrease')
#     markup.add(btn_decrease)
#     return markup


async def get_fd_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    btn_add_cart = InlineKeyboardButton('Добавить в корзину', callback_data='btn_add_cart')
    markup.add(btn_add_cart)
    return markup









@dp.callback_query_handler(lambda c: c.data.startswith('btn_-1'))
async def btn_callback(callback_query: types.CallbackQuery, state: FSMContext):
    pr_id = int(callback_query.data.split('_')[-1])
    await decrease_product_quantity(pr_id)


@dp.callback_query_handler(lambda c: c.data.startswith('btn_+1'))
async def btn_callback(callback_query: types.CallbackQuery, state: FSMContext):
    pr_id = int(callback_query.data.split('_')[-1])
    await decrease_product_quantity(pr_id)


async def count_kb(product_id):
    markup = InlineKeyboardMarkup(row_width=2)
    btn_minus = InlineKeyboardButton('-1', callback_data=f'btn_-1_{product_id}')
    btn_plus = InlineKeyboardButton('+1', callback_data=f'btn_+1_{product_id}')
    markup.add(btn_plus)
    markup.add(btn_minus)
    return markup















@dp.callback_query_handler(lambda c: c.data.startswith('admin_change_quantity'))
async def process_change_quantity(callback_query: types.CallbackQuery):
    await AdminState.choose_product.set()  # Устанавливаем состояние для выбора товара
    await callback_query.message.edit_text("Выберите товар, для которого нужно изменить количество:")


@dp.callback_query_handler(state=AdminState.choose_product)
async def admin_choose_product(callback_query: types.CallbackQuery, state: FSMContext):
    cursor.execute('SELECT id, name FROM products')
    products = cursor.fetchall()
    product_id = int(callback_query.data)
    markup_product = await count_kb(product_id)
    await bot.send_message(ADMIN_ID, "Можете увеличить или уменьшить количество товара", reply_markup=markup_product)
    async with state.proxy() as data:
        data['product_id'] = product_id
    await AdminState.change_quantity.set()
    await callback_query.message.edit_text("Введите новое количество товара:")


@dp.message_handler(lambda message: message.text.isdigit(), state=AdminState.change_quantity)
async def admin_change_quantity(message: types.Message, state: FSMContext):
    new_quantity = int(message.text)
    async with state.proxy() as data:
        product_id = data['product_id']

    cursor.execute('UPDATE products SET quantity = ? WHERE id = ?', (new_quantity, product_id))
    conn.commit()
    await state.finish()
    await message.answer("Количество товара успешно изменено!")



#@dp.message_handler(Command("start"))
#async def cmd_start(message: types.Message):
 #   await message.answer("Hello!")


@dp.message_handler(commands=['menu'])
async def start(message: types.Message):
    keyboard_menu = await get_menu_keyboard()
    await message.reply('Выберите пункт меню:', reply_markup=keyboard_menu)





@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await message.reply('/start - Регистрация в боте\n '
                        '/menu - Меню товаров\n'
                        '/cart - Моя корзина\n'
                        '/help - Все команды бота\n'
                        '/panel - Панель навигации')






async def decrease_product_quantity(product_id):
    cursor.execute('UPDATE products SET quantity = quantity - 1 WHERE id = ?', (product_id,))
    conn.commit()

@dp.message_handler(commands=['admin'])
async def enter_admin_mode(message: types.Message):
    if str(message.from_user.id) == ADMIN_ID:
        await AdminState.choose_product.set()
        keyboard_menu = await get_menu_keyboard()
        await message.reply('Вход в режим администратора. Выберите товар для редактирования:', reply_markup=keyboard_menu)
    else:
        await message.reply('Вы не имеете доступа к режиму администратора.')






##############

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    user_id = message.from_user.id

    info = cursor_users.execute('SELECT * FROM users WHERE user_id =?', (user_id,))

    if info.fetchone() is None:
        await message.answer(
            "Добро пожаловать! Пожалуйста, укажите свои данные для регистрации.\n\nВведите вашу фамилию:")
        await RegisterState.first_name.set()
    else:
        await message.answer(
            "Добро пожаловать! Вы уже зарегистрированы. Для того узнать ваши данные нажмите команду /profile")






@dp.message_handler(commands=['profile'])
async def cmd_profile(message: types.Message):
    user_id = message.from_user.id
    cursor_users.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    person_id = cursor_users.fetchone()
    if person_id is None:
        await message.answer(
            "Добро пожаловать! Вы еще не зарегистрированы.\n\nДля регистрации выберите команду /start")
    else:

        await message.answer(
            f"Ваши данные:\nФИО: {person_id[1]} {person_id[2]} {person_id[3]}")






@dp.message_handler(lambda message: message.text.isalpha(), state=RegisterState.first_name)
async def process_first_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['first_name'] = message.text
    await RegisterState.last_name.set()
    await message.reply("Теперь введите ваше имя:")


@dp.message_handler(lambda message: message.text.isalpha(), state=RegisterState.last_name)
async def process_last_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['last_name'] = message.text
    await RegisterState.patronymic.set()
    await message.reply("И, наконец, введите ваше отчество:")


@dp.message_handler(lambda message: not message.text.startswith('/skip'), state=RegisterState.patronymic)
async def process_patronymic(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['patronymic'] = message.text
        user_id = message.from_user.id
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        patronymic = data.get('patronymic')
        cursor_users.execute('INSERT INTO users (user_id, first_name, last_name, patronymic) VALUES (?, ?, ?, ?)',
                             (user_id, first_name, last_name, patronymic))
        conn_users.commit()
    await state.finish()
    await message.reply("Спасибо за регистрацию!")


#############################


# ...










class UserState(StatesGroup):
    cart = State()  # State to store the user's cart


# ...






@dp.callback_query_handler(lambda c: c.data.startswith('add_to_cart'))
async def add_to_cart(callback_query: types.CallbackQuery, state: FSMContext):
    product_id = int(callback_query.data.split('_')[-1])

    # Retrieve the user's cart from the state
    async with state.proxy() as data:
        if 'cart' not in data:
            data['cart'] = []
        data['cart'].append(product_id)

    await callback_query.answer("Товар добавлен в корзину!")


@dp.callback_query_handler(lambda c: c.data.startswith('remove_from_cart'))
async def remove_from_cart(callback_query: types.CallbackQuery, state: FSMContext):
    product_id = int(callback_query.data.split('_')[-1])

    # Retrieve the user's cart from the state
    async with state.proxy() as data:
        if 'cart' in data and product_id in data['cart']:
            data['cart'].remove(product_id)

    await callback_query.answer("Товар удален из корзины!")




@dp.message_handler(commands=['cart'])
async def show_cart(message: types.Message, state: FSMContext):
    # Retrieve the user's cart from the state
    async with state.proxy() as data:
        if 'cart' in data and data['cart']:
            cart_items = get_cart_items_info(data['cart'])
            total_amount = calculate_total_amount(data['cart'])
            # Print or log the total amount for debugging
            print(f"Total Amount: {total_amount}")
            await message.reply(f"Ваша корзина:\n{cart_items}\n\nСумма: {total_amount} руб.")

            # Use the total amount in the send_invoice method
            await bot.send_invoice(
                chat_id=message.from_user.id,
                title='Оплата корзины',
                description='Оплата товаров из вашей корзины',
                payload='pay_cart',
                provider_token=PAYMENT_TOKEN,
                currency='rub',
                prices=[
                    LabeledPrice(
                        label='Total Amount',
                        amount=int(total_amount)*100  # Ensure it's an integer
                    )
                ],
                start_parameter='',
                disable_notification=False,
                allow_sending_without_reply=True
            )
        else:
            await message.reply("Ваша корзина пустая!")


# Implement the logic to calculate the total amount and get cart items information

def calculate_total_amount(cart):
    total_amount = 0
    for product_id in cart:
        cursor.execute('SELECT price FROM products WHERE id = ?', (product_id,))
        price = cursor.fetchone()[0]  # Assuming the price is in the first column
        total_amount += price // 100
    return total_amount

def get_cart_items_info(cart):
    cart_items_info = ""
    for product_id in cart:
        cursor.execute('SELECT name, price FROM products WHERE id = ?', (product_id,))
        product_info = cursor.fetchone()
        product_name, product_price = product_info[0], product_info[1]

        cart_items_info += f"{product_name} - {product_price // 100} руб.\n"

    return cart_items_info




async def get_add_to_cart_keyboard(product_id):
    markup = InlineKeyboardMarkup(row_width=1)
    btn_add_to_cart = InlineKeyboardButton('Добавить в корзину', callback_data=f'add_to_cart_{product_id}')
    markup.add(btn_add_to_cart)
    return markup



async def rm_add_cart_keyboard(state, product_id):
    product_ids = await state.get_data()
    product_ids = product_ids.get('cart', [])
    ids = []
    markup = InlineKeyboardMarkup(row_width=2)
    for product_id_cikl in product_ids:
        ids.append(int(product_id_cikl))  # Предполагаем, что стоимость хранится в третьем столбце
    if product_id in ids:
        btn_rm_from_cart = InlineKeyboardButton('Удалить из корзины', callback_data=f'remove_from_cart_{product_id}')
        markup.add(btn_rm_from_cart)
    btn_add_to_cart = InlineKeyboardButton('Добавить в корзину', callback_data=f'add_to_cart_{product_id}')
    markup.add(btn_add_to_cart)
    return markup







# async def rm_from_cart(state, product_id):
#     product_ids = await state.get_data()
#     product_ids = product_ids.get('cart', [])
#     ids = []
#     for product_id_cikl in product_ids:
#         ids.append(int(product_id_cikl))  # Предполагаем, что стоимость хранится в третьем столбце
#     if product_id in ids:
#         markup = InlineKeyboardMarkup(row_width=1)
#         btn_rm_from_cart = InlineKeyboardButton('Удалить из корзины', callback_data=f'remove_from_cart_{product_id}')
#         markup.add(btn_rm_from_cart)
#         return markup














@dp.callback_query_handler(lambda c: c.data.isdigit())
async def process_product_callback(callback_query: types.CallbackQuery):
    product_id = int(callback_query.data)
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    markup_add_rm = await rm_add_cart_keyboard(dp.current_state(), product_id)
    #markup_add = await get_add_to_cart_keyboard(product_id)
    #markup_rm = await rm_from_cart(dp.current_state(), product_id)
    if product[5] > 0:
        await bot.send_invoice(
            chat_id=callback_query.from_user.id,
            title=product[1],
            description=product[2],
            payload=str(product_id),
            provider_token=PAYMENT_TOKEN,
            currency='rub',
            prices=[
                LabeledPrice(
                    label='Стоимость через бота',
                    amount=int(product[3])

                )
            ],
            start_parameter='',
            photo_url=product[4],
            photo_size=100,
            photo_width=800,
            photo_height=450,
            need_name=False,
            disable_notification=False,
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False,
            send_phone_number_to_provider=False,
            send_email_to_provider=False,
            is_flexible=False,
            protect_content=False,
            reply_to_message_id=None,
            allow_sending_without_reply=True,
        )

        await bot.send_message(chat_id=callback_query.from_user.id, text=f'Количество товара: {product[5]}',
                               reply_markup=markup_add_rm)



    else:
        await callback_query.answer("Извините, товара нет в наличии.")


@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


async def update_order_status_get_order(order_id):
    print(f"Attempting to update status_get_order for order_id {order_id}")
    cursor_orders.execute('UPDATE orders SET status_get_order = ? WHERE order_id = ?', (1, order_id,))
    conn_orders.commit()
    print(f"Successfully updated status_get_order for order_id {order_id}")


async def status_send_to_admin(order_id):
    print(f"Attempting to update status_send_to_admin for order_id {order_id}")
    cursor_orders.execute('UPDATE orders SET status_send_to_admin = ? WHERE order_id = ?', (1, order_id,))
    conn_orders.commit()
    print(f"Successfully updated status_send_to_admin for order_id {order_id}")

async def send_to_admin_keyboard(user_id, order2_id):
    markup = InlineKeyboardMarkup(row_width=1)
    btn_send_to_admin = InlineKeyboardButton('Отправить сообщение для получения заказа', callback_data=f'send_to_admin_button_{user_id}_{order2_id}')
    markup.add(btn_send_to_admin)
    return markup



@dp.callback_query_handler(lambda c: c.data.startswith('give_product_button'))
async def send_to_admin_button_func(callback_query: types.CallbackQuery):
    order_id = int(callback_query.data.split('_')[-1])
    cursor_orders.execute('SELECT * FROM orders WHERE order_id = ?',
                          (order_id,))
    order_info = cursor_orders.fetchone()

    if order_info[9] == 0:
        await update_order_status_get_order(order_id)
        await bot.send_message(order_info[1], "Вы получили свой заказ!!!\n Приятного аппетита!")
        print(f"User_id в give_product_button: {order_info[1]}")
    else:
        await bot.send_message(ADMIN_ID, "Вы уже отправили сообщение клиенту")










    # order_id = int(callback_query.data.split('_')[-1])
    # cursor_orders.execute('SELECT * FROM orders WHERE status_get_order = 0 AND order_id = ?',
    #                       (order_id,))
    # order_info = cursor_orders.fetchone()
    # await update_order_status_get_order(order_id)
    # await bot.send_message(order_info[1], "Вы получили свой заказ!!!\n Приятного аппетита!")
    # print(f"User_id в give_product_button: {order_info[1]}")
async def give_product_keyboard(order2_id):
    markup = InlineKeyboardMarkup(row_width=1)
    btn_give_product = InlineKeyboardButton(text="Клиент получил заказ", callback_data=f'give_product_button_{order2_id}')
    markup.add(btn_give_product)
    return markup


@dp.callback_query_handler(lambda c: c.data.startswith('send_to_admin_button'))
async def send_to_admin_button_func(callback_query: types.CallbackQuery):
    user_id = int(callback_query.data.split('_')[-2])
    cursor_users.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    person_id = cursor_users.fetchone()
    order2_id = int(callback_query.data.split('_')[-1])


    cursor_orders.execute('SELECT * FROM orders WHERE user_id = ? AND order_id = ?',
                          (user_id, order2_id,))
    order_id = cursor_orders.fetchone()

    if int(order_id[8]) == 0:
        cursor_orders.execute('SELECT * FROM orders WHERE user_id = ? AND status_get_order = 0 AND order_id = ?',
                              (user_id, order2_id,))
        await status_send_to_admin(order2_id)
        kb_give_product = await give_product_keyboard(order2_id)
        print(f"User_id: {user_id}")
        print(f"админ: {order2_id}")
        await bot.send_message(ADMIN_ID, text=f"Данные заказа\n "
                                              f"Номер заказа: {order2_id}\n"
                                              f"ФИО: {person_id[1]} {person_id[2]} {person_id[3]} "
                                              f"ID покупателя: {person_id[0]}\n"
                                              f"Корзина: {order_id[7]}\n"
                                              f"Сумма: {order_id[5]}\n"
                                              f"Время покупки: {order_id[6]}", reply_markup=kb_give_product)

    else:
        await bot.send_message(user_id, text=f"Ошибка отправки!!!!!!\nВы уже нажали на кнопку отправки")








@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message, state: FSMContext):
    product_id = message.successful_payment.invoice_payload

    if product_id.startswith('pay'):
        # Payment for the entire cart
        await process_cart_payment(message, product_id, state)
    else:
        # Payment for an individual product
        await process_individual_product_payment(message, product_id, state)

    async with state.proxy() as data:
        product_ids = data.get('cart', [])

async def process_cart_payment(message: types.Message, product_ids, state: FSMContext):
    # Extract necessary information from the cart_id and process accordingly
    product_ids = await state.get_data()
    product_ids = product_ids.get('cart', [])
    user_id = int(message.chat.id)
    cursor_users.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    person_id = cursor_users.fetchone()

    # Вычисляем общую стоимость корзины
    total_price = 0
    product_names = []
    for product_id in product_ids:
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        product = cursor.fetchone()
        total_price += product[3]  # Предполагаем, что стоимость хранится в третьем столбце

        # Добавляем название товара в список
        product_names.append(product[1])

        # Уменьшаем количество товара
        await decrease_product_quantity(product_id)

    # Создаем кнопку callback
    order_info = {
        "user_id": user_id,
        "price": total_price / 100,  # В рублях
        "time": str(datetime.now()),  # Текущее время
        "products": ', '.join(product_names),  # Названия купленных товаров (разделенные запятыми)
        "surname": str(person_id[1]),
        "name": str(person_id[2]),
        "patronymic": str(person_id[3])
    }

    # Вставляем данные в таблицу заказов
    cursor_orders.execute(
        'INSERT INTO orders (user_id, surname, name, patronymic, price, time, products, status_get_order, status_send_to_admin) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (
        order_info["user_id"], order_info["surname"], order_info["name"], order_info["patronymic"], order_info["price"],
        order_info["time"], order_info["products"], 0, 0))

    conn_orders.commit()

    # Отправляем сообщение о покупке клиенту
    await bot.send_message(message.chat.id,
                           f"Удачная покупка на {total_price // 100} руб.")

    # Получаем информацию о заказе для отправки администратору
    cursor_orders.execute('SELECT order_id FROM orders WHERE user_id = ? AND status_get_order = 0', (user_id,))
    order_id = cursor_orders.fetchone()
    order2_id = order_id[0]

    # Отправляем информацию о заказе администратору
    kb_send_to_admin = await send_to_admin_keyboard(user_id, order2_id)
    conn_orders.commit()

    await bot.send_message(message.chat.id, text="Ваши данные\n"
                                                 f"Номер заказа: {order2_id}\n"
                                                 f"ФИО: {person_id[1]} {person_id[2]} {person_id[3]}\n"
                                                 f"ID: {person_id[0]}\n"
                                                 f"Корзина: {', '.join(product_names)}\n"
                                                 f"Сумма: {total_price // 100} руб.\n"
                                                 f"Время покупки: {order_info['time']}", reply_markup=kb_send_to_admin)



    await state.update_data(cart=[])



async def process_individual_product_payment(message: types.Message, product_id, state: FSMContext):
    product_id = message.successful_payment.invoice_payload
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    await decrease_product_quantity(product_id)
    user_id = int(message.chat.id)
    cursor_users.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    person_id = cursor_users.fetchone()

    # Создайте кнопку callback
    order_info = {
        "user_id": user_id,
        "price": message.successful_payment.total_amount / 100,  # В рублях
        "time": str(datetime.now()),  # Текущее время
        "products": product[1],  # Название купленного товара (может быть расширено)
        "surname": str({person_id[1]}),
        "name": str({person_id[2]}),
        "patronymic": str({person_id[3]})
    }

    cursor_orders.execute('INSERT INTO orders (user_id, surname, name, patronymic, price, time, products, status_get_order, status_send_to_admin) '
                          'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                          (order_info["user_id"], order_info["surname"], order_info["name"], order_info["patronymic"], order_info["price"], order_info["time"], order_info["products"], 0, 0))

    conn_orders.commit()
    # Отправьте сообщение о покупке клиенту
    await bot.send_message(message.chat.id,
                           f"Удачная покупка на {message.successful_payment.total_amount // 100} руб.")

    cursor_orders.execute('SELECT order_id FROM orders WHERE user_id = ? AND status_get_order = 0', (user_id,))
    order_id = cursor_orders.fetchone()
    order2_id = order_id[0]
    kb_send_to_admin = await send_to_admin_keyboard(user_id, order2_id)
    conn_orders.commit()
    print(f"клиент: {order2_id}")
    print(user_id)
    await bot.send_message(message.chat.id, text="Ваши данные\n"
                                                 f"Номер заказа: {order2_id}\n"
                                                 f"ФИО: {person_id[1]} {person_id[2]} {person_id[3]}\n"
                                                 f"ID: {person_id[0]}\n"
                                                 f"Корзина: {product[1]}\n"
                                                 f"Сумма: {product[3] // 100} руб.\n"
                                                 f"Время покупки: {order_info['time']}", reply_markup=kb_send_to_admin)











if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))

