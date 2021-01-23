from PIL import Image
from PIL.ExifTags import TAGS


# 対応するEXIF情報を定義
COMPAT＿EXIF＿TABLE = {272: 'Device', }


# idに対応するexifの名称を取得
def get_TAGS_info_by_id(id):
    return TAGS.get(id)


# exifを取得
def get_exif(fpath):
    try:
        im = Image.open(fpath)
        return im._getexif()
    except exception as e:
        print('error: ', e)
        sys.exit()


# idに対応する指定ファイルのexif情報を取得
def get_data_by_exif_id(fpath, id):
    exif = get_exif(fpath)    
    return exif.get(id)  # 存在しないexifはNoneが返る


# 取得可能な全てのexif情報を表示する
def show_details_by_exif(fpath):

    exif = get_exif(fpath)    
    for id, val in exif.items(): # [id, 名称, 値] の順で出力 
        print(id, '(', get_TAGS_info_by_id(id), ') : ', val)
    print(len(exif.keys()), 'values were extructed from EXIF')


# 同一のexif情報を持つか判定
def has_same_exif(fpath1, fpath2):
    exif1 = get_exif(fpath1)
    exif2 = get_exif(fpath2)
    return exif1 == exif2
