import sys

from PIL import Image
from PIL.ExifTags import TAGS
import exifread

# 対応する画像形式を定義
COMPAT_EXT = ('jpg', 'jpeg', 'png', 'tiff', 'heic')


# idに対応するexifの名称を取得 (Pillow)
def get_TAGS_info_by_id(id):
    return TAGS.get(id)


# exifを取得
def get_exif(fpath):
    tags = exifread.process_file(open(fpath, 'rb'))
    return tags


# exifの略称から対応する値を取得
def get_val_from_tags(tags, name):
    for k, v in tags.items():
        if name == k:
            return v
    return None


# 取得可能な全てのexif情報を表示する
def show_details_by_exif(fpath):

    exif = get_exif(fpath)    
    for k, v in exif.items():
        print(k, ':', v)
    print(len(exif.keys()), 'values were extructed from EXIF')


# 同一のexif情報を持つか判定
def has_same_exif(fpath1, fpath2):
    tags1 = get_exif(fpath1)
    tags2 = get_exif(fpath2)
    return tags1 == tags2
