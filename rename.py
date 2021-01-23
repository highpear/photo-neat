import os, sys
from exifread import *

# Windowsでファイル名に使用できない文字
NA_CHAR_FOR_FILENAME = ['\\', '/', '*', '?' ,'"', '<', '>', '|', ':']

# リネーム時に置換する文字の対応テーブル
REPLACE_CHAR_FOR_CUSTOM_FILENAME = {' ': '-',}  # ファイル名に空白を非推奨


# リネームを実行
def rename(old_name, new_name):
    try:
        os.rename(old_name, new_name)
        print('[', old_name, '] was renamed to [', new_name, ']')
    except exception as e:
        print('error:', e)
        sys.exit()


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
def rename_by_exif_tag(fpath_list, tag_id):

    file_num = len(fpath_list)
    ren_table = {}                      # リネームテーブル {"old name": "new name", ...} これに従いリネームを実行
    uk_cnt = 0;                          # exif情報不明画像のカウント
    uk_digits = 4                        # デフォルトは4桁でゼロ埋め
    if(uk_digits < len(str(file_num))):
        uk_digits = len(str(file_num))

    for fpath in fpath_list:

        new_name = get_exif(fpath).get(tag_id)   # idに対応するexif情報を取得

        if not new_name:                                          # exif情報が存在しない時
            uk_cnt += 1                                           # exif情報不明の画像をカウント
            new_name = 'Unknown-' + str(uk_cnt).zfill(uk_digits)  # 連番を用いてファイル名を生成
        else:
            new_name = validate_fname(new_name)  # ファイル名のバリデーションを実行

        new_name += '.' + fpath.split('.')[-1]    # 拡張子を追加

        # ディレクトリの親パスを含めて設定
        new_name = os.path.join(os.path.dirname(fpath), new_name)

        # リネームテーブルの更新
        old_name = fpath
        ren_table[old_name] = new_name

    # リネームのプレビューを出力
    ren_preview(ren_table)

    # リネームの実行
    for old_name, new_name in ren_table.items():
        rename(old_name, new_name)


# リネームのプレビューを出力
def ren_preview(ren_table):
    for old_name, new_name in ren_table.items():
        print('[', old_name, '] -> [', new_name, ']')

