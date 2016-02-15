import os.path

LAYOUT_OPTIONS = [
    {
        "_id": "normal",
        "name": "白底深蓝色字体",
        "layout": {
            "text_color": (54,60,76,255),
            "date_color": (54,60,76,255),
            "line_color": (220,220,220,255),
            "qmark_color": (200,200,200,255),
        }
    },
    {
        "_id": "maruko_chan",
        "name": "樱桃小丸子背景",
        "layout": {
            "template": os.path.join(os.path.dirname(__file__), "image_template", "template_tilimer.bmp"),
            "text_color": (54,60,76,255),
            "date_color": (54,60,76,255),
            "line_color": (220,220,220,255),
            "qmark_color": (200,200,200,255),
            "used_width": 580,
        }
    },
]