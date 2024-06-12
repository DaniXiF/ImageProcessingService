import telebot
from loguru import logger
import os
import time
from telebot.types import InputFile
from polybot.img_proc import Img


class Bot:

    def __init__(self, token, telegram_chat_url):
        # create a new instance of the TeleBot class.
        # all communication with Telegram servers are done using self.telegram_bot_client
        self.telegram_bot_client = telebot.TeleBot(token)

        # remove any existing webhooks configured in Telegram servers
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)

        # set the webhook URL
        self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', timeout=60)

        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)

    def is_current_msg_photo(self, msg):
        return 'photo' in msg

    def is_current_msg_text(self, msg):
        return 'text' in msg

    def download_user_photo(self, msg):
        """
        Downloads the photos that sent to the Bot to `photos` directory (should be existed)
        :return:
        """
        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')

        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)

        return file_info.file_path

    def send_photo(self, chat_id, img_path):
        if not os.path.exists(img_path):
            raise RuntimeError("Image path doesn't exist")

        self.telegram_bot_client.send_photo(
            chat_id,
            InputFile(img_path)
        )


    def handle_message(self, msg):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {msg}')
        self.send_text(msg['chat']['id'], f'Your original message: {msg["text"]}')



class QuoteBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        if msg["text"] != 'Please don\'t quote me':
            self.send_text_with_quote(msg['chat']['id'], msg["text"], quoted_msg_id=msg["message_id"])



class ImageProcessingBot(Bot):

    def __init__(self, token, telegram_chat_url):
        super().__init__(token, telegram_chat_url)
        self.msg_cache = {}


    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')
        command_list = ['yakov','help','/start']
        if 'text' in msg and msg['text'].lower().strip() == 'help':
            self.send_text(msg['chat']['id'], 'Welcome to Helpy! \nEdit options are:\n'
                                              'Blur, Salt and Pepper, Contour, Concat or Rotate')
            return
        elif 'text' in msg and msg['text'].lower().strip() == 'yakov':
            self.send_text(msg['chat']['id'], 'Que Pasta Yakof! \nEdit options are:\n'
                                              'Blur, Salt and Pepper, Contour, Concat or Rotate')
            return
        elif 'text' in msg and msg['text'].lower().strip() == '/start':
            self.send_text(msg['chat']['id'], "Welcome to Image Balabot by Danchik.\nSend a photo with one of description:\nBlur, Salt and Pepper, Contour, Concat or Rotate")
            return
        elif 'text' in msg and msg['text'].lower().strip() == 'helpy':
            self.send_text(msg['chat']['id'], "What's next?! \nYou gonna ask for ServiceDesk too ?")
            return
        elif 'text' in msg and msg['text'].lower().strip() not in command_list:
            self.send_text(msg['chat']['id'], "Sorry, I'm not familiar with this term, try typing 'help' to see options.")
            return




        # If the message sent is an image
        if self.is_current_msg_photo(msg):
            snp_list = ['salt and pepper','snp', 'salt n pepper']
            #For a pic download it 
            photo_path = self.download_user_photo(msg)
            #if there is a caption
            if ('media_group_id' in msg
                    and msg['media_group_id'] in self.msg_cache
                    and 'caption' in self.msg_cache[msg['media_group_id']]
                    and self.msg_cache[msg['media_group_id']]['caption'].lower().strip() == 'concat'):
                first_path = self.download_user_photo(self.msg_cache[msg['media_group_id']])
                first_image = Img(first_path)
                sec_image = Img(photo_path)
                first_image.concat(sec_image)
                final_pic = first_image.save_img()
                self.send_photo(msg['chat']['id'], final_pic)
            #Check for caption in sent message
            elif 'caption' in msg:
                if msg['caption'].lower().strip() == 'help':
                    self.send_text(msg['chat']['id'],'Helpy is here, you can select from options.')
                    self.send_text(msg['chat']['id'],'Blur, Salt and Pepper, Contour, Concat or Rotate')
                #Instance for Blur input
                elif msg['caption'].lower().strip() == 'blur':
                    blur_p = Img(photo_path)
                    blur_p.blur()
                    blur_image = blur_p.save_img()
                    self.send_photo(msg['chat']['id'], blur_image)
                #Instance for Rotate input
                elif msg['caption'].lower().strip() == 'rotate':
                    rot_p = Img(photo_path)
                    rot_p.rotate()
                    rot_img = rot_p.save_img()
                    self.send_photo(msg['chat']['id'], rot_img)
                #Instance for Rotate 2 input
                elif msg['caption'].lower().strip() == 'rotate 2':
                    rot_p = Img(photo_path)
                    rot_p.rotate()
                    rot_p.rotate()
                    rot_img_twice = rot_p.save_img()
                    self.send_photo(msg['chat']['id'], rot_img_twice)
                #Instance for Concat input
                elif msg['caption'].lower().strip() == 'concat':
                    #Telegram sends every picture in a different message
                    #in order to keep track with the different messages
                    #Telegram creates a unique 'media_group_id', we can use this id
                    #to link these messages

                    #Here we check for a id, if it's missing
                    if 'media_group_id' in msg:
                        self.msg_cache[msg['media_group_id']] = msg
                    else:
                        self.send_text(msg['chat']['id'], 'Only one picture sent, please send 2 picture together.')
                elif msg['caption'].lower().strip() in snp_list:
                # elif msg['caption'].lower().strip() == "salt and pepper" or " snp" or "salt n pepper":
                    snp_p = Img(photo_path)
                    snp_p.salt_n_pepper()
                    salted_pic = snp_p.save_img()
                    self.send_photo(msg['chat']['id'], salted_pic)
                elif msg['caption'].lower().strip() == 'contour':
                    cont_p = Img(photo_path)
                    cont_p.contour()
                    cont_img = cont_p.save_img()
                    self.send_photo(msg['chat']['id'], cont_img)
                elif msg['caption'].lower().strip() not in snp_list:
                    self.send_text(msg['chat']['id'],'Not familiar with this term, try help to see options.')
            elif 'captions' not in msg:
                    self.send_text(msg['chat']['id'],"Caption is empty, please input option:")
                    self.send_text(msg['chat']['id'],"Blur, Salt and Pepper, Contour, Concat or Rotate")
