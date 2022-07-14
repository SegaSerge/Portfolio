import os
import pytesseract
import requests
import telebot
from telebot import types
import cv2
from bs4 import BeautifulSoup as BS

name = "findbyitembot"
name1 = "find_by_item_bot"
bot = telebot.TeleBot("5512409293:AAFl1naUMAO7wB-yWZK7wdiOkSHJGoEQa5Y")


@bot.message_handler(commands=['start'])
def start(message):
    """Метоод запускает работу бота"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    photo = types.KeyboardButton("/Photo")
    help = types.KeyboardButton("/Help")
    website = types.KeyboardButton("/Website")

    name = message.from_user.first_name
    markup.add(photo, help, website)
    bot.send_message(message.chat.id, f"Привет, {name}", reply_markup=markup)


@bot.message_handler(commands=['Photo'])
def photo(message):
    """Информирует пользователя, чтобы он отправил фото/картинку"""
    bot.send_message(message.chat.id, "Отправьте фото ценника")


class PiterGSM:
    """Класс работы с сайтом : отправляет запрос методом GET и возвращает данные о таваре """

    def __init__(self):
        self.text = None

    @staticmethod
    def info_site_(text: str) -> requests.models.Response:
        """метод запроса get для получения данных с сайта(парсинг)"""
        url = f"https://pitergsm.ru/search/index.php?q={text}&s="

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) "
                          "Version/15.5 Safari/605.1.15",
            "Accept-Language": "ru",
            "Connection": "keep-alive",
            "x-o3-app-version": "release_8-6'-'2022_1e301650",
            "x-o3-app-name": "dweb_client"
        }
        return requests.get(url=url, headers=headers)

    def get_content(self, bts: bytes, name_file: str) -> list:
        """разбираем полученные данные парсинга, и возвращаем их в массиве словарей"""
        catalog = []
        self.text = InfoPhoto().get_text(bts=bts, name_file=name_file)
        if self.text == "NORESULT":
            print("NOO")
            catalog = ["NORESULT"]
            return catalog
        else:
            soup = BS(PiterGSM.info_site_(self.text).content, 'html.parser')
            items = soup.find_all('div', class_='catalog__item')

            for item in items:
                catalog.append({
                    'title': item.find('h3', class_='prod-card__title').get_text(strip=True),
                    'cost': item.find('div', class_='price__now').get_text(strip=True),
                })
            return catalog


class InfoPhoto:
    """Класс работает с фотографией полученной в боте - обрабатывае(сохраняет, удаляет и вытаскивает название товара"""

    Brands = ['IPHONE', 'MACBOOK', 'MAC', 'APPLE', 'WATCH', 'HONOR', 'XIAOMI', 'SAMSUNG', 'HUAWEI', 'REALME',
              'SUUNTO', 'AMAZFIT', 'GARMIN', 'AIRPODS', 'ONEPLUS', 'POCO', 'OPPO', 'SONY', 'SAMSUNG',
              'PLAYSTATION', 'MICROSOFT', 'LEGO', 'OCULUS', 'DYSON', 'XBOX']

    def __init__(self):
        self.name_file = None
        self.bts = None

    def make_photo_(self) -> str:
        """создание и удаление фотографии для библиотеки OpenCV(cv2), преобразуем фото в текст"""
        with open(self.name_file, 'wb') as new_file:
            new_file.write(self.bts)
        image = cv2.imread(f"{self.name_file}")
        os.remove(f"{self.name_file}")
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        text = pytesseract.image_to_string(img, lang="eng")
        return text

    def get_text(self, bts: bytes, name_file: str) -> str:
        """ Обработка полученных данных, поиск брэнда в тексте ценника
                            возвращает найденный брэнд или
                ответ NORESULT - является флагом для дальнейшей обработки"""
        # достаём список брендов
        self.bts = bts
        self.name_file = name_file

        text = InfoPhoto.make_photo_(self)
        text = text.splitlines()

        for i in range(len(text)):
            for brand in InfoPhoto.Brands:
                if text[i].upper().count(brand):
                    # index = text[i].upper().find(brand)
                    return str(text[i])[text[i].upper().find(brand):]
                else:
                    continue
        else:
            return "NORESULT"


@bot.message_handler(content_types=['photo'])
def get_photo(message):
    """Метоод получает фотографию с бота и отправляет на обработку.
    После обработки выводит сообщение с результатом пользователю
    результат - сылки на прямой поиск по названию товара"""
    # Получаем id фотографии в Telegram
    raw = message.photo[-1].file_id
    name_file = raw + ".jpg"
    file_info = bot.get_file(raw)
    # получаем бинарное значение фотографии
    downloaded_file = bot.download_file(file_info.file_path)
    # сохранение фото и чтение необходимо для библиотеки OpenCV
    # т.к библиотека на основе фото создаёт векторы. И сразу удаляем, чтобы не занимало место

    catalog = PiterGSM().get_content(bts=downloaded_file, name_file=name_file)
    markup = types.InlineKeyboardMarkup()
    for item in catalog:
        if item == "NORESULT":
            markup.add(types.InlineKeyboardButton(f"Мы ничего не нашли,\n попробуйте сделать другое фото",
                                                  url="https://pitergsm.ru/search/index.php?q=&s="))
            break
        else:
            markup.add(types.InlineKeyboardButton(f"{item['title']} \n- "
                                                  f"{str(item['cost']).replace('a', ' rub')}",
                                                  url=f"https://pitergsm.ru/search/index.php?q={item['title']}&s="))
    bot.send_message(message.chat.id, "Нашли:", reply_markup=markup)


@bot.message_handler(commands=["Help"])
def help_(message):
    """Метод вывод информацию для пользователя о боте"""
    text_for_help = "Привет! \nЭтот бот позволяет тебе найти товар на сайте PiterGSM(это не реклама, " \
                    "просто так получилось)\n" \
                    "чтобы найти товар(если он есть) - достаточно отправить фотографию ценника товара \nили " \
                    "фотку с названием электроники \nи если он есть на сайте - тебе обязательно покажется его цена\n" \
                    "если не нашли товар - сделайте повторно фотографию, чтобы название было чэтко видно" \
                    "НО может быть и так, что на сайте нет такого товара(это магазин электроники)" \
                    "в результате будет список ссылок на прямой поиск товара на сайте" \
                    "чтобы перейти на сайт по прямой ссылке - нажми кнопку Website"

    bot.send_message(message.chat.id, f"{text_for_help}")


@bot.message_handler(commands=["Website"])
def website(message):
    """Кнопка выводит сообщение для перехода на сайт фирмы"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Посетить главную страницу сайта", url="https://pitergsm.ru/"))
    bot.send_message(message.chat.id, "перейти на сайт?", reply_markup=markup)


if __name__ == '__main__':
    bot.polling(none_stop=True)
