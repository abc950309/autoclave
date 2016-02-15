import os.path
import autoclave

LAYOUT_OPTIONS = [
    {
        "_id": "normal",
        "name": "白底深蓝色字体",
        "text_color": "#363c4c",
        "date_color": "#363c4c",
        "line_color": "#dcdcdc",
        "qmark_color": "#c8c8c8",
    },
    {
        "_id": "maruko_chan",
        "name": "樱桃小丸子背景",
        "template": os.path.join(os.path.dirname(autoclave.__file__), "image_template", "template_tilimer.bmp"),
        "text_color": "#363c4c",
        "date_color": "#363c4c",
        "line_color": "#dcdcdc",
        "qmark_color": "#c8c8c8",
        "used_width": 580,
    },
]