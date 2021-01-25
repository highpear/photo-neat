import os, sys, collections
from exifio import *

# Windowsでファイル名に使用できない文字
NA_CHAR_FOR_FILENAME = ['\\', '/', '*', '?' ,'"', '<', '>', '|', ':']

# リネーム時に置換する文字の対応テーブル
REPLACE_CHAR_FOR_CUSTOM_FILENAME = {' ': '_',}  # ファイル名に空白を非推奨


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


# fpathをリネームしてリネーム後のパスを返す (親ディレクトリは変更しない)
def get_renamed_fpath(fpath, ren_mode=('REPLACEALL',)):

    bname = os.path.basename(fpath)   # 拡張子含む

    fname = bname.split('.')[0]       # 拡張子含まないファイル名
    ext = bname.split('.')[-1]        # ピリオド含まない拡張子
    dirpath = os.path.dirname(fpath)  # 親ディレクトリのパス

    # モードに応じてリネーム後のファイル名を生成
    if mode == 'REPLACEALL':  # 旧ファイル名を全て置き換える
        fname = ren_mode[1]
    elif mode == 'REPLACE':   # 旧ファイルの文字列を置き換える
        fname = fname.replace(ren_mode[1], ren_mode[2])
    elif mode == 'ADDHEAD':   # 旧ファイル名の先頭に追加
        fname = ren_mode[1] + fname
    elif mode == 'ADDTAIL':   # 旧ファイル名の末尾に追加
        fname += ren_mode[1]
    elif mode == 'REMOVE':    # 旧ファイル名から文字列を除く
        fname = fname.replace(ren_mode[1], '')
    elif mode == 'EXTLOWER':  # 拡張子を小文字に変更
        ext = ext.lower()
    elif mode == 'EXTUPPER':  # 拡張子を大文字に変更
        ext = ext.upper()
    else:
        print('error: unmatched MDOE [', mode, ']')
        sys.exit()

    # 新ファイル名のバリデーション
    fname = validate_fname(fname)

    # リネーム後のファイルパスの生成
    fname = fname + '.' + ext 
    fpath_renamed = os.path.join(dirpath, fname)

    return fpath_renamed


# 指定のidに対応するexif情報でリネームを実行
def rename_by_exif(fpath_list, exif_name):

    file_num = len(fpath_list)
    ren_table = {}                       # リネームテーブル {"old name": "new name", ...} これに従いリネームを実行
    uk_cnt = 0;                          # exif情報不明画像のカウント
    uk_digits = 4                        # デフォルトは4桁でゼロ埋め
    if(uk_digits < len(str(file_num))):
        uk_digits = len(str(file_num))

    for fpath in fpath_list:

        tags = get_exif(fpath)
        new_name = get_val_from_tags(tags, exif_name)             # 対応するexif情報を取得

        # exif_nameに応じて分岐



        if not new_name:                                          # exif情報が存在しない時
            uk_cnt += 1                                           # exif情報不明の画像をカウント
            new_name = 'Unknown-' + str(uk_cnt).zfill(uk_digits)  # 連番を用いてファイル名を生成
        else:
            new_name = str(new_name)
            new_name = validate_fname(new_name)  # ファイル名のバリデーションを実行

        new_name += '.' + fpath.split('.')[-1]    # 拡張子を追加

        # ディレクトリの親パスを含めて設定
        new_name = os.path.join(os.path.dirname(fpath), new_name)

        # リネームテーブルの更新
        old_name = fpath
        ren_table[old_name] = new_name

    # リネームテーブルのバリデーション (リネームの前に必ず実行)
    ren_valid(ren_table)

    # リネームのプレビューを出力
    ren_preview(ren_table)

    # リネームの実行を確認
    print('execute renaming ? (yes or no) >>')
    ans = input()

    # リネームの実行
    if(ans == 'yes'):
        for old_name, new_name in ren_table.items():
            rename(old_name, new_name)


# リネームのプレビューを出力
def ren_preview(ren_table):
    for old_name, new_name in ren_table.items():
        print('[', old_name, '] -> [', new_name, ']')


# リネーム後の名前を検証
def ren_valid(ren_table):

    # 重複した際に連番を付ける
    result = collections.Counter(ren_table.values())  # 重複したnew_nameをカウント
    for new_name, cnt in result.items():
        if cnt > 1:                                   # 重複したnew_nameのみファイル名変更を行う
            i = 0;                                    # 重複枚数のカウント
            for k, v in ren_table.items():
                if v == new_name:                                           # 重複したnew_nameの時は末尾に連番を付与
                    base_name = os.path.basename(new_name).split('.')[0]    # 拡張子を除いたファイル名を取得
                    ext = '.' + new_name.split('.')[-1]                     # 拡張子を取得
                    parent_dir = os.path.dirname(new_name)                  # 親ディレクトリのパスを取得
                    fpath = os.path.join(parent_dir, base_name + '-' + str(i).zfill(4) + ext)  # 4桁ゼロ埋めの連番を付与
                    ren_table[k] = fpath  
                    i += 1;



            

