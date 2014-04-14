from random import randrange
from os.path import join

from django.conf import settings

def background(request):
    background_img = request.session.get('background_img')
    background_caption = request.session.get('background_caption')
    if not background_img or not background_caption:
        idx = randrange(len(settings.BACKGROUND_IMAGES))
        entry = settings.BACKGROUND_IMAGES[idx]
        background_img = request.session["background_img"] = join(
            settings.BACKGROUND_IMAGES_PREFIX, entry[0])
        background_caption = request.session["background_caption"] = entry[1]
    return {
        "background_img": background_img,
        "background_caption": background_caption
    }
