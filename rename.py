import os, sys, collections, datetime
from exifio import *

# Windowsでファイル名に使用できない文字
NA_CHAR_FOR_FILENAME = ['\\', '/', '*', '?' ,'"', '<', '>', '|', ':']

# リネーム時に置換する文字の対応テーブル
REPLACE_CHAR_FOR_CUSTOM_FILENAME = {' ': '-',}  # ファイル名に空白を非推奨


# リネームを実行
def rename(old_name, new_name):
    try:
        os.rename(old_name, new_name)
        print('FILE_RENAMED : file [', old_name, '] was renamed to [', new_name, ']')
    except:
        print(old_name, 'was not renamed at rename()')
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


# ファイルパスから親ディレクトリ，ファイル名，拡張子を取得
def split_fpath(fpath):
    dpath = os.path.dirname(fpath)   # ディレクトリパス
    bname = os.path.basename(fpath)  # ベースネーム取得 (拡張子あり)
    fname = bname.split('.')[0]      # ファイル名取得 (拡張子なし) 
    ext = bname.split('.')[-1]       # 拡張子取得
    return dpath, fname, ext


# fpathと同名のAAEファイルが存在するか判定
def has_aae(fpath):
    dpath, fname, _ = split_fpath(fpath)
    if os.path.exists(os.path.join(dpath, fname + '.AAE')):
        return True
    else:
        False


# fpathをリネームしてリネーム後のパスを返す (親ディレクトリは変更しない, exifを読む処理は行わない)
def get_renamed_fpath(fpath, ren_mode=('REPLACEALL',)):

    dirpath, fname, ext = split_fpath(fpath)

    # モードに応じてリネーム後のファイル名を生成
    if ren_mode[0] == 'REPLACEALL':  # 旧ファイル名を全て置き換える (exif)
        fname = ren_mode[1]
    elif ren_mode[0] == 'REPLACE':   # 旧ファイルの文字列を置き換える (exif)
        fname = fname.replace(ren_mode[1], ren_mode[2])
    elif ren_mode[0] == 'ADDHEAD':   # 旧ファイル名の先頭に追加 (exif)
        fname = ren_mode[1] + fname
    elif ren_mode[0] == 'ADDTAIL':   # 旧ファイル名の末尾に追加 (exif)
        fname += ren_mode[1]
    elif ren_mode[0] == 'REMOVE':    # 旧ファイル名から文字列を除く
        fname = fname.replace(ren_mode[1], '')
    elif ren_mode[0] == 'EXTLOWER':  # 拡張子を小文字に変更
        ext = ext.lower()
    elif ren_mode[0] == 'EXTUPPER':  # 拡張子を大文字に変更
        ext = ext.upper()
    elif ren_mode[0] == 'JPEG2JPG':  # JPEGをJPGに統一
        if ext == 'JPEG':
            ext = 'JPG'
        if ext == 'jpeg':
            ext = 'jpg'
    else:
        print('ERROR: unmatched MDOE [', ren_mode[0], ']')
        sys.exit()

    # 新ファイル名のバリデーション (os禁止文字の除去，空白のリプレイス)
    fname = validate_fname(fname)

    # リネーム後のファイルパスの生成
    bname = fname + '.' + ext 
    fpath_renamed = os.path.join(dirpath, bname)

    return fpath_renamed


#リネームテーブルを作成する
def make_ren_table(fpath_list, ren_mode=['REPLACEALL', ''], tag_name=None, preview=True, dt_fmt='%Y-%m-%d-%H%M%S', uk_custom=('Unknown-', 1, 4 )):

    ren_table = {}

    # リネームにexifタグを用いる場合
    if tag_name:
        uk_fname = uk_custom[0]          # 不明画像に用いる規定のファイル名
        uk_cnt = uk_custom[1]            # exif情報不明画像のカウント開始値
        uk_digits = uk_custom[2]         # デフォルトは4桁でゼロ埋め

        for fpath in fpath_list:
            tags = get_exif(fpath)
            tag_val = get_val_from_tags(tags, tag_name)              # 対応するexif情報を取得 exifreadの独自クラス
            new_fname = str(tag_val)

            if tag_name == 'EXIF DateTimeOriginal' and new_fname != 'None':  # 日時形式の書式をカスタム
                new_fname = custom_datetime_fmt(new_fname, dt_fmt=dt_fmt)

            if new_fname == 'None':                                  # exif情報なし
                new_fname = uk_fname + str(uk_cnt).zfill(uk_digits)  # 連番を用いてファイル名を生成
                uk_cnt += 1                                          # exif情報不明の画像をカウント

            ren_mode[1] = new_fname
            # モードに応じてリネーム後のパスを生成
            fpath_renamed = get_renamed_fpath(fpath, ren_mode=tuple(ren_mode))
            # テーブルに追加
            ren_table[fpath] = fpath_renamed

    # 任意の文字列を用いてリネームを行う場合
    else:
        for fpath in fpath_list:
            fpath_renamed = get_renamed_fpath(fpath, tuple(ren_mode))
            #テーブルに追加
            ren_table[fpath] = fpath_renamed

    # リネームテーブルのバリデーション (重複チェック，リネームの前に必ず実行)
    validate_ren_table(ren_table)

    # リネームのプレビューを出力
    if preview:
        ren_preview(ren_table)

    return ren_table


# リネームテーブルからリネームを実行   
def rename_by_table(ren_table, confirm=True):
    print('all', len(ren_table), 'files will be renamed')

    if confirm:
        print('execute renaming ? (yes or no) >>')
        ans = input()
        if(ans == 'yes'):
            pass
        else:
            print('canceled renaming')
            return

    file_num = len(ren_table)
    cnt = 0

    # リネームを実行
    print('BEGIN RENAMING...')
    for old_name, new_name in ren_table.items():
            rename(old_name, new_name)
            cnt += 1
            print('RENAME IN PROGRESS :', cnt, '/', file_num, 'completed ... (', cnt/file_num*100, '% )')
    
    print(len(ren_table), 'files were renamed ')

    # 終了の確認
    print('do you finish renaming ? (yes or no) >>')
    ans = input()
    if ans == 'yes':
        return
    elif ans == 'no':
        print('undo rename ? (yes or no) >>')
        if ans == 'yes':
            undo_rename_by_table(ren_table)


# リネームのプレビューを出力
def ren_preview(ren_table):
    for old_name, new_name in ren_table.items():
        print('[', old_name, '] ==> [', new_name, ']')
    print(len(ren_table), 'files were selected for renaming')


# リネームテーブルに基づいてリネームをアンドゥ
def undo_rename_by_table(ren_table):
    not_exists = []
    for old_name, new_name in ren_table.items():
            # パスが存在するか確認
            if os.path.exists(new_name):
                rename(new_name, old_name)
            else:  # リネーム後に手動で直接ファイル名を変更した場合などはこれに該当
                not_exists.append(new_name)

    if len(not_exists) == 0:
        print('all', len(ren_table), 'files were renamed to each previous name')
    else:
        print(len(not_exists), 'files were not found, so these files were not renamed')


# リネーム後の名前を検証
def validate_ren_table(ren_table):

    # 重複した際に連番を付ける
    result = collections.Counter(ren_table.values())  # 重複したnew_nameをカウント
    for new_name, cnt in result.items():
        if cnt > 1:                                   # 重複したnew_nameのみファイル名変更を行う
            n = 0;                                    # 重複枚数のカウント
            for k, v in ren_table.items():
                if v == new_name:                     # 重複したnew_nameの時は末尾に連番を付与
                    dirname, fname, ext = split_fpath(new_name)
                    fpath = os.path.join(dirname, fname + '-' + str(n).zfill(4) + '.' + ext)  # 4桁ゼロ埋めの連番を付与
                    ren_table[k] = fpath  
                    n += 1;


# 日付の書式をカスタムしたファイル名を取得
def custom_datetime_fmt(dtstr, dt_fmt='%Y-%m-%d-%H%M%S'):

    if len(dtstr) != 19:  # この文字数でなければデータが正しくない
        return

    src_fmt = '%Y:%m:%d %H:%M:%S'                    # exifreadで得られる日付データの書式
    dt = datetime.datetime.strptime(dtstr, src_fmt)  # src_fmtに応じてdatetime.datetimeを取得
    fname = dt.strftime(dt_fmt)
    return fname


