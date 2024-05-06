from keras import models
import numpy as np
import psycopg2
from keras.preprocessing import image
import cv2
import telebot
from PIL import Image
from io import BytesIO
from environs import Env

env = Env()
env.read_env()

bot = telebot.TeleBot(env('BOT_TOKEN'))
IMAGE_SIZE = 256
load_model = models.load_model('model/model')


def get_info(dog_number):
    connection_1 = None
    cursor = None
    try:
        # Подключение к существующей базе данных
        connection_1 = psycopg2.connect(
            user=env('POSTGRES_USER'),
            password=env('POSTGRES_PASSWORD'),
            host=env('POSTGRES_HOST'),
            port=env.int('POSTGRES_PORT'),
            database=env('POSTGRES_DB'),
        )

        # Курсор для выполнения операций с базой данных
        cursor = connection_1.cursor()
    except (Exception, psycopg2.Error) as error:
        print("Ошибка при работе с PostgreSQL", error)

    cursor.execute("SELECT name, description FROM dogs_info WHERE id='{}'".format(dog_number))
    save_pass = cursor.fetchall()
    return save_pass[0][0], save_pass[0][1]


def save_photo(img):
    new_image = img.resize((IMAGE_SIZE, IMAGE_SIZE))
    new_image.save('file1.jpg')


def load_photo():
    img = image.load_img('file1.jpg')
    img_1 = image.img_to_array(img)
    img_1 = cv2.resize(img_1, (IMAGE_SIZE, IMAGE_SIZE), interpolation=cv2.INTER_AREA)
    img_1 = np.expand_dims(img_1, axis=0) / 255.
    return img_1


def get_prediction(img_1):
    y_pred = load_model.predict(img_1)
    return np.argmax(y_pred[0]) + 1


@bot.message_handler(commands=['start'])
def send_start(message):
    bot.reply_to(message, "Я бот, который помогает с определением породы собаки")


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "Я бот, который может помочь вам с определением породы собаки по фотографии.")


@bot.message_handler(content_types=['photo'])
def check_photo(message):
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    img = Image.open(BytesIO(downloaded_file))

    if img.format != 'JPEG':
        bot.reply_to(message, "Измените формат фотографии. Принимается только JPEG.")
    else:
        bot.reply_to(message, "Выбранное фото успешно отправлено.")
        save_photo(img)
        dog_index = get_prediction(load_photo())
        name, info = get_info(dog_index)

        bot.reply_to(message, 'порода называется: {}'.format(name))
        bot.reply_to(message, 'Вот ее описание, взгляните: {}'.format(info))


@bot.message_handler(content_types=['document'])
def check_document(message):
    file_extension = message.document.file_name.split('.')[-1]

    if file_extension == 'txt':
        bot.reply_to(message, "Отправьте фото")
    else:
        bot.reply_to(message, "Отправьте фото собаки для определения породы.")


@bot.message_handler(func=lambda message: True)
def handle_all(message):
    if message.photo:
        return
    else:
        bot.send_message(message.chat.id, 'Отправьте фотографию собаки для определения породы')


if __name__ == '__main__':
    bot.polling()
