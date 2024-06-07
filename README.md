
# Buffet Telegram Bot

Buffet Telegram Bot is a virtual shopping assistant that allows users to purchase items and receive order details directly through Telegram. This bot is built using `aiogram` and `sqlite3` to manage products, orders, and users efficiently.


<img src="https://github.com/osiriser/Buffet-Telegram-bot/blob/main/photo1.png" width="300"/> , <img src="https://github.com/osiriser/Buffet-Telegram-bot/blob/main/photo2.jpg" width="300"/>


## Features

- **User Registration:** New users can register using the `/start` command.
- **Product Menu:** Browse available products using the `/menu` command.
- **Shopping Cart:** View and manage your shopping cart with the `/cart` command.
- **Help:** Get a list of all available commands using the `/help` command.
- **Admin Panel:** Admins can access additional functionalities through the `/admin` command.
- **Order Management:** Add or remove products from your cart, and complete the purchase. Admins can process orders and notify users when their order is ready.

## Order Process

1. **Purchasing Items:**
   - When a user purchases items, they receive a confirmation message with the order details.
   - Example of an order confirmation message:
     ```
     Successful purchase of 192.0 RUB.
     Your details:
     Order number: 11
     Full Name: Ivanov Ivan I. 
     ID: 5082331736
     Cart: Picnic, Picnic, Picnic
     Total: 192.0 RUB
     Purchase time: 2023-12-08 18:27:11.002223
     ```

2. **Admin Notification:**
   - The user can send this order receipt to the admin by clicking a button.
   - The admin receives the order details and can mark the order as fulfilled by pressing the "Deliver Item" button.

3. **Order Completion:**
   - Once the admin processes the order, the user receives a "Bon appétit" message.

## Bot Commands

- `/start` - Register in the bot
- `/menu` - Display the product menu
- `/cart` - View and manage your shopping cart
- `/help` - List all available bot commands
- `/admin` - Access the admin panel (admin only)

## Database Structure

The bot uses three SQLite3 databases:
1. **Products Database:** Stores information about available products.
2. **Orders Database:** Keeps track of all user orders.
3. **Users Database:** Manages user information and registration details.



## Requirements

- Python 3.6+
- aiogram
- sqlite3

## Example Usage

1. **Register with the bot:**
   ```bash
   /start
   ```

2. **View product menu:**
   ```bash
   /menu
   ```


3. **View and manage your cart:**
   ```bash
   /cart
   ```

4. **Admin processes the order:**
   ```bash
   /admin
   ```

## Contributing

Feel free to fork this repository and submit pull requests. We welcome any improvements or additional features that can make this bot even better!

## License

This project is licensed under the MIT License.
