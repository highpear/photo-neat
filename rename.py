import os
from exif import *

# Windowsでファイル名に使用できない文字
NA_CHAR_FOR_FILENAME = ['\\', '/', '*', '?' ,'"', '<', '>', '|', ':']

# リネーム時に置換する文字の対応テーブル
REPLACE_CHAR_FOR_CUSTOM_FILENAME = {' ': '-',}  # ファイル名に空白を非推奨


# リネームを実行
def rename(old_name, new_name):
    os.rename(old_name, new_name)


# fname文字列から使用不可能な文字を除去 (パスが渡されることは想定していない)
def remove_na_char(fname):
    for ch in NA_CHAR_FOR_FILENAME:
        fname = fname.replace(ch, '')
    return fname


# fname文字列において文字の置換を実行する
def replace_for_custom_fname(fname):
    for ch1, ch2 in REPLACE_CHAR_FOR_CUSTOM_FILENAME.items():
        fname = fname.replace(ch1, ch2)
    return fname


# 使用禁止文字の検証や文字の置換をまとめて行う
def validate_fname(fname):
    fname = remove_na_char(fname)
    fname = replace_for_custom_fname(fname)
    return fname


# 指定のidに対応するexif情報でリネームを実行
def rename_by_exif_tag(fpath, tag_id):

    new_name = get_exif(fpath).get(tag_id)   # idに対応するexif情報を取得
    
    if not new_name:                         # exif情報が存在しない時
        new_name = 'Unknown'
    else:
        new_name = validate_fname(new_name)  # ファイル名のバリデーションを実行 

    '''
      変更点
      fpath_listを引数に変更
      Unknownの際に連番を生成する
      リネームのプレビューを表示して，実行を標準入力から受け付ける
    '''

    if new_name is None:
        new_name = 'UNKNOWN.' + fpath.split('.')[-1]
    else:
        new_name += '.' + fpath.split('.')[-1]

    rename(fpath, new_name)

 
def rename_all_by_exif_tag(fpath_list, tag_id):  # バリデーション済みの画像のパスのリスト
    for fpath in fpath_list:
        rename_by_exif_tag(fpath, tag_id)

def preview_rename():
    pass

