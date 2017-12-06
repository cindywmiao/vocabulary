import urllib2
from bs4 import BeautifulSoup
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from random import *
import numpy

_x = 20
_y = 50


def download(url, user_agent='wswp', num_retries=2):
    request = urllib2.Request(url)
    try:
        html = urllib2.urlopen(request).read()
    except urllib2.URLError as e:
        print 'Download error:', e.reason
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                return download(url, user_agent, num_retries - 1)
    return html

def strQ2B(ustring):
  rstring = ""
  for uchar in ustring:
    inside_code=ord(uchar)
    if inside_code==0x3000:
        inside_code=0x0020
    else:
        inside_code-=0xfee0

    if inside_code<0x0020 or inside_code>0x7e:
        rstring += uchar
    else:
        rstring += unichr(inside_code)
  return rstring


def translate_word(word):
    url = 'http://dict.cn/' + word
    soup = BeautifulSoup(download(url), 'html.parser')
    information = soup.find('ul', attrs={'class': 'dict-basic-ul'}).find_all('li')
    result = []
    for item in information:
        span = item.find('span')
        strong = item.find('strong')
        if(span != None and strong != None):
            meanings = strQ2B(strong.text)
            if len(meanings.split(";")) < 4:
                result.append(span.text + " " + meanings)
            else:
                items = meanings.split(";")
                result.append(span.text + " " + ';'.join(items[:3]))
    return result

def random_x_y(map, meaning):
    width = len(map)
    height = len(map[0])
    x_index = randint(1, width - 1) * 10
    y_index = randint(1, height - 1) * 10
    x_len = max([len(item) for item in meaning])
    y_len = len(meaning)

    for i in range(x_index * 1, x_index + _x * x_len, 10):
        for j in range(y_index, y_index + _y * y_len, 10):
            if i/10 >= width or j/10 >= height or map[i/10][j/10] == 1:
                return random_x_y(map, meaning)

    for i in range(x_index, x_index + _x * (x_len + 1) , 10):
        for j in range(y_index, y_index + _y * (y_len + 1), 10):
            map[i/10][j/10] = 1
    return (x_index, y_index)

def random_ttf():
    ttf_list = ['fonts/Arial-Unicode-Bold.ttf', 'fonts/Arial-Unicode-Italic.ttf', 'fonts/Arial-Unicode-Regular.ttf']
    index = randint(0, 2)
    font_size = randint(17, 25)
    return ImageFont.truetype(ttf_list[index], font_size)


if __name__ == '__main__':
    file = 'word-list.txt'

    # get an image
    base = Image.open('background.jpg').convert('RGBA')
    map = numpy.zeros((base.size[0]/10, base.size[1]/10))

    # make a blank image for the text, initialized to transparent text color
    txt = Image.new('RGBA', base.size, (255, 255, 255, 0))


    # get a drawing context
    d = ImageDraw.Draw(txt)

    x = 10
    y = 10
    last = ""
    with open(file, 'r') as f:
        context = []
        for line in f.readlines():
            word = line[:-1] if line[-1] == '\n' else line
            meanings = translate_word(word)
            context.append((word, meanings))

        current = []
        fnt = random_ttf()
        for (word, meanings) in context:
            # draw text, half opacity
            (x, y) = random_x_y(map, meanings)
            d.text((x, y), word, font=fnt, fill=(255, 255, 255, 255))
            # draw text, full opacity
            for meaning in meanings:
                d.text((x, y + _y), meaning, font=fnt, fill=(255, 255, 255, 128))
                y += _y

    out = Image.alpha_composite(base, txt)

    out.show()