from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import datetime
import os

init_param_list = [
    "template",
    "width",
    "height",
    "fill",
    "line_h",
    "text_size",
    "text_color",
    "used_width",
    "text_mid",
    "date_size",
    "date_margin",
    "date_color",
    "line_color",
    "line_width",
    "qmark_size",
    "qmark_margin",
    "qmark_top_shift",
    "qmark_bottom_shift",
    "qmark_color",
    "text_font",
    "date_font",
    "qmark_font",
    "says_font",
]

init_param_default = {
    "template": None,
    "width": 750,
    "height": 320,
    "fill": (255,255,255,255),
    "line_h": 50,
    "text_size": 36,
    "text_color": (0,0,0,255),
    "used_width": None,
    "text_mid": 200,
    "date_size": 20,
    "date_margin": 20,
    "date_color": None,
    "line_color": None,
    "line_width": 5,
    "qmark_size": 60,
    "qmark_margin": 30,
    "qmark_top_shift": 15,
    "qmark_bottom_shift": 50,
    "qmark_color": None,
    "text_font": None,
    "date_font": None,
    "qmark_font": None,
    "says_font": None,
}

class ImageGenerator:

    nobr_list = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÁÉÍÓÚÝÀÈÌÒÙÂÊÎÔÛÄËÏÖÜŸáéíóúýàèìòùâêîôûäëïöüÿÇŞÃÕÑĄĘĮŲÆŒØĲÞçşãõñąęįųæœøĳßþ"
    marks_list = "，。！…,.!—"

    def __init__(
        self,
        setting = None,
        template = None,
        width = None,
        height = None,
        fill = None,
        line_h = None,
        text_size = None,
        text_color = None,
        used_width = None,
        text_mid = None,
        date_size = None,
        date_margin = None,
        date_color = None,
        line_color = None,
        line_width = None,
        qmark_size = None,
        qmark_margin = None,
        qmark_top_shift = None,
        qmark_bottom_shift = None,
        qmark_color = None,
        text_font = None,
        date_font = None,
        qmark_font = None,
        says_font = None,
    ):
        
        """
        建立对象，传入各项所需数据。
        """
        
        for line in init_param_list:
            if locals()[line]:
                setting[line] = locals()[line]
            if line not in setting or not setting[line]:
                setting[line] = init_param_default[line]

        if setting['template']:
            self.image = Image.open(setting['template'])
            self.width, self.height = self.image.size
        else:
            self.image = Image.new("RGB", (setting['width'], setting['height']), color = setting['fill'])
            self.width, self.height = setting['width'], setting['height']
        
        self.line_h = setting['line_h']

        self.text_color = setting['text_color']
        
        if setting['used_width']:
            self.used_width = setting['used_width']
        else:
            self.used_width = self.width
        
        self.text_mid = setting['text_mid']
        self.date_margin = setting['date_margin']
        if not setting['date_color']:
            setting['date_color'] = setting['text_color']
        self.date_color = setting['date_color']

        if not setting['line_color']:
            setting['line_color'] = setting['date_color']
        self.line_color = setting['line_color']
        self.line_width = setting['line_width']
        
        self.qmark_margin = setting['qmark_margin']
        self.qmark_top_shift = setting['qmark_top_shift']
        self.qmark_bottom_shift = setting['qmark_bottom_shift']
        if not setting['qmark_color']:
            setting['qmark_color'] = setting['line_color']
        self.qmark_color = setting['qmark_color']

        self.wrap_width = self.used_width - 140
        self.margin = (self.used_width * 1.02 - self.wrap_width) / 2
        
        if not setting['text_font']:
            setting['text_font'] = os.path.join(os.path.dirname(__file__), "font", "font.ttf")
        if not setting['date_font']:
            setting['date_font'] = os.path.join(os.path.dirname(__file__), "font", "date.ttf")
        if not setting['qmark_font']:
            setting['qmark_font'] = os.path.join(os.path.dirname(__file__), "font", "qmark.ttf")
        if not setting['says_font']:
            setting['says_font'] = os.path.join(os.path.dirname(__file__), "font", "says.otf")
                
        self.text_font = ImageFont.truetype(setting['text_font'], setting['text_size'])
        self.date_font = ImageFont.truetype(setting['date_font'], setting['date_size'])
        self.qmark_font = ImageFont.truetype(setting['qmark_font'], setting['qmark_size'])
        self.says_font = ImageFont.truetype(setting['says_font'], setting['date_size'])

    def text_wraper(self, text, font, width):
        start = end = 0
        wraped_list = []
        while end < len(text):
            if font.getsize(text[start:(end + 1)])[0] > width:
                while (text[end - 1] in self.nobr_list and text[end] in self.nobr_list) or text[end] in self.marks_list:
                    end = end - 1
                wraped_list.append((text[start:end]).strip())
                start = end
            end = end + 1
        
        wraped_list.append(text[start:end+1])
        return wraped_list

    def generate(self, text, says, date = None):
        
        if not date:
            date = datetime.datetime.now()
        date = date.strftime("%Y.%m.%d %a")

        draw = ImageDraw.Draw(self.image)

        wraped_list = self.text_wraper(text, self.text_font, self.wrap_width)
        text_top = self.text_mid - len(wraped_list) / 2 * 50

        line_top = text_top - (45 if len(wraped_list) <= 2 else 20)
        date_top = line_top - 45

        date_left = self.used_width - self.date_margin - self.date_font.getsize(date)[0]
        draw.text( (date_left, date_top), date, font = self.date_font, fill = self.date_color)
        draw.text( (self.date_margin, date_top), says, font = self.says_font, fill = self.date_color)

        bottom_qmark_left = self.used_width - self.qmark_margin - self.qmark_font.getsize("”")[0]
        draw.text( (self.qmark_margin, text_top - self.qmark_top_shift), "“", font = self.qmark_font, fill = self.qmark_color)
        draw.text( (bottom_qmark_left, text_top + 50 * len(wraped_list) - self.qmark_bottom_shift), "”", font = self.qmark_font, fill = self.qmark_color)

        draw.line([(self.date_margin, line_top), (self.used_width - self.date_margin, line_top)], fill = self.line_color, width = self.line_width)

        current_h = text_top
        for line in wraped_list:
            draw.text( (self.margin, current_h), line, font = self.text_font, fill = self.text_color)
            current_h = current_h + self.line_h

        del draw
        
    def get_image():
        return self.image
    
    def generate2save(self, text, says, date = None):
        if not date:
            date = datetime.datetime.now()
        self.generate(text, says, date)
        name = date.strftime("%Y-%m-%d")
        self.image.save(os.path.join(os.path.dirname(__file__), "static", "output", (says.lower().replace(' ', '-') + '-' + name + ".png")), "PNG")