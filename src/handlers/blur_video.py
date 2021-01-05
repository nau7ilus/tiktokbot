import sys
import json
import asyncio
import requests
from os import listdir
from millify import millify
from PIL import Image, ImageEnhance, ImageFilter, ImageFont, ImageDraw, ImageOps


def background(fn):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, fn, *args, **kwargs)

    return wrapped

def cover_img(can, img):
    img_w, img_h = img.size
    img_ratio = img_h / img_w

    can_w, can_h = can.size
    can_ratio = can_h / can_w

    if img_ratio > can_ratio:
        h = can_w * img_ratio
        img = img.resize((can_w, int(h)))
        can.paste(img, (0, int((can_h - img.size[1]) / 2)))


def download_image(url):
    try:
        res = requests.get(url, stream=True).raw
    except requests.exceptions.RequestException as err:
        sys.exit(1)

    try:
        img = Image.open(res)
    except IOError:
        print('Ошибка при открытии изображения')
        sys.exit(1)

    return img


@background
def edit_frame(frame_name, video_data):
    # Создаём холст
    canvas = Image.new('RGBA', (1920, 1080))

    # Открываем изображение
    frame = Image.open('temp/' + video_data["id"] + '/raw-frames/' + frame_name)

    # Размытое изображение на фон
    cover_img(canvas, frame)

    # Размытие фона и уменьшение яркости
    canvas = canvas.filter(ImageFilter.GaussianBlur(8))
    canvas = ImageEnhance.Brightness(canvas).enhance(0.8)

    # Установка главного кадра в центр
    canvas.paste(frame.resize((592, 1080)), (664, 0))
    draw = ImageDraw.Draw(canvas)

    # Регистрируем шрифты
    semibold_font = ImageFont.truetype('src/assets/fonts/ProximaNova-Semibold.ttf', 47)
    regular_font = ImageFont.truetype('src/assets/fonts/ProximaNova-Regular.ttf', 38)

    # Добавление никнейма автора. Если верифицирован, добавить галочку
    draw.text((1505, 167), video_data['author']['nickName'], fill='white', font=semibold_font)

    if video_data['author']['verified'] is True:
        margin = 10
        text_width = draw.textsize(video_data['author']['nickName'], font=semibold_font)[0]
        tick = Image.open('src/assets/images/tick.png')
        canvas.paste(tick, (1505 + margin + text_width, 182), tick)

    # Добавление логина пользователя
    draw.text((1505, 220), '@' + video_data['author']['name'], fill='white', font=regular_font)

    regular_font = ImageFont.truetype('src/assets/fonts/ProximaNova-Regular.ttf', 47)

    # Пишем статистику по лайкам
    like_icon = Image.open('src/assets/images/heart.png').resize((105 - 15, 97 - 15))
    canvas.paste(like_icon, (1340, 378), like_icon)
    draw.text((1340 + 100, 378 + 3), millify(video_data['diggCount'], precision=1), fill='white', font=regular_font)

    # Пишем статистику по комментариям
    message_icon = Image.open('src/assets/images/message.png').resize((106 - 15, 100 - 15))
    canvas.paste(message_icon, (1340, 502), message_icon)
    draw.text((1340 + 100, 502 + 3), millify(video_data['commentCount'], precision=1), fill='white', font=regular_font)

    # Пишем статистику по share
    share_icon = Image.open('src/assets/images/share.png').resize((102 - 15, 81 - 15))
    canvas.paste(share_icon, (1340, 636), share_icon)
    draw.text((1340 + 100, 636 + 3), millify(video_data['shareCount'], precision=1), fill='white', font=regular_font)

    # Рисуем обводку для аватарки
    draw.ellipse((1330, 142) + (1330 + 154, 142 + 154), fill='white')

    # Рисуем аватарку пользователя
    avatar = download_image(video_data['author']['avatar']).resize((144, 144))

    mask = Image.new('L', avatar.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + avatar.size, fill=255, outline=255)
    mask = mask.resize(avatar.size, Image.ANTIALIAS)
    avatar.putalpha(mask)

    rounded_avatar = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
    rounded_avatar.putalpha(mask)

    canvas.paste(rounded_avatar, (1335, 147), rounded_avatar)

    # Сохранение фото
    canvas.save('temp/' + video_data['id'] + '/edited-frames/' + frame_name)


video_data = json.loads(sys.argv[1])

raw_frames = listdir('temp/' + video_data['id'] + '/raw-frames')
for frame_name in raw_frames:
    edit_frame(frame_name, video_data)
