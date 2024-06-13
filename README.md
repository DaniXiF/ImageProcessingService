# Image BalaBot by Danchik

Image Balabot is a Telegram bot for image processing.

## Features

- Accepts images from users and performs various image processing operations.
- Supports commands for blur, rotate, salt and pepper noise, contour detection, and concatenation of images.

## Getting Started

1. Clone this repository.
2. Install the dependencies by running `pip install -r requirements.txt`.
3. Create a Bot in Telegram using `BotFather` bot on Telegram. For additional help to create Bot and Token visit link https://core.telegram.org/bots.
4. Obtain a Telegram Bot token from BotFather and replace `YOUR_BOT_TOKEN`.  
5. Add your 'AuthToken' from Telegram to your server configuration, example ngrok `ngrok config add-authtoken <your-authtoken>`
6. Run the bot by executing `python main.py`.

## Usage

1. Start the bot by sending the `/start` command.
2. Send an image to the bot and choose an operation by providing the appropriate caption. Options are `Blur, Salt and Pepper, Contour, Concat or Rotate`
3. Receive the processed image from the bot.
4. For Help type in `help`.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes. 
Thank you !

