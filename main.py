from PIL import Image
import sys, os, glob, shutil, datetime, platform
import argparse

from classify import *
from exifio import *
from rename import *
# import pyheif


# パスから画像をオープン
def im_open(fpath):
    # 画像形式を判定
    _, _, ext = split_fpath(fpath)
    ext = ext.lower()
    
    if ext not in COMPAT_EXT:
        print('error: uncompatible file type [', ext, ']')
        sys.exit()

    try:
        if ext == 'heic':
            return # read_heif(fpath)
        else:                       # Pillowで読み込む
            return Image.open(fpath)

    except:
        print('error:')
        sys.exit()


# dir以下の指定拡張子のファイルパスをリストで取得
def get_all_files(dir, TARGET_EXT=[], recursive=True, includeAAE=False):

    if includeAAE:                # 写真編集履歴ファイルを含める場合
        TARGET_EXT.append('aae')
    
    # 抽出したパスを格納するリスト
    fpath_list = []
    
    # 末尾の"/"を除去
    if dir[-1] == '/':
        dir = dir[:-1]

    if recursive:
        # dir以下全てのファイルのパスを再帰的に取得
        files = glob.glob(dir + '/**', recursive=True)
    else:
        files = glob.glob(dir + '/*')
    
    for file in files:
        # 拡張子を取得
        _, _, ext = split_fpath(file)
        ext = ext.lower()
        if os.path.isfile(file) and ext in TARGET_EXT:  # ディレクトリ除外かつ対象拡張子のみ
            fpath_list.append(file)

    # 結果の出力
    print(len(fpath_list), 'files were extracted from [', dir+'/', '] and below')
    
    return fpath_list


# リスト内のファイルを全て指定のフォルダ以下の[Original_現在時刻/]フォルダへコピーする
def import_all(fpath_list, dest_dir):

    # dest_dir以下に現在時刻でフォルダを生成する
    dt_now = str(datetime.datetime.now())          # 現在時刻を文字列で取得 (ex. 2021-01-29 21:15:58.592992)

    dir_name = dt_now.split('.')[0]                # 小数点以下の秒を除去
    dir_name = dir_name.replace(' ', '-')          # 空白を除去
    dir_name = dir_name.replace(':', '')           # コロンを除去
    dest_dir = os.path.join(dest_dir, dir_name)    # コピー先パスを生成

    if os.path.exists(dest_dir):                   # コピー先フォルダが既に存在するかチェック
        print('ERROR : directory [', dest_dir, '] already exists')
        sys.exit()
    else:
        os.mkdir(dest_dir)                       # フォルダを新規作成
        print('DIR_CREATED : new directory [', dest_dir, '] was created')

    # コピーを実行
    cnt = 0
    for fpath in fpath_list:
        bname = os.path.basename(fpath)
        dest_path = os.path.join(dest_dir, bname)
        shutil.copy2(fpath, dest_path)
        print('FILE_COPIED : file [', fpath, '] was copied to [', dest_path, ']')
        cnt += 1

    print('{} files were copied to [ {} ]'.format(cnt, dest_dir))

    return dest_dir  # (コピー先ディレクトリは時刻ごとに生成される為，コピー終了後にそのパスを返す)


def show_fpath_list(fpath_list, include_dir_path=False):  # yieldを使用へ
    cnt = 0;
    ext_cnt = {}
    for fpath in fpath_list:
        cnt += 1
        _, _, ext = split_fpath(fpath)
        ext = ext.lower()

        if ext in ext_cnt.keys():
            ext_cnt[ext] += 1
        else:
            ext_cnt[ext] = 1
        
        if include_dir_path:
            print('[', cnt, ']', fpath)
        else:
            dpath, fname, ext = split_fpath(fpath)
            print('[', cnt, ']', fname + '.' + ext)

    print(cnt, 'files are selected now')

    for k, v in ext_cnt.items():
        print(k, ':', v, '(', round(v/cnt*100, 2), '% )')


def show_dir_info(dpath, recursive=True):

    if not os.path.exists(dpath):
        print('ERROR : directory [', dpath, '] does not exist')
        sys.exit()

    if recursive:
        files = glob.glob(dpath + '/**', recursive=True)
    else:
        files = glob.glob(dpath + '/*')

    file_cnt = 0
    dir_cnt = 0
    ext_cnt = {}

    for file in files:
        if os.path.isfile(file):
            file_cnt += 1
            _, _, ext = split_fpath(file)
            ext = ext.lower()
            if ext in ext_cnt.keys():
                ext_cnt[ext] += 1
            else:
                ext_cnt[ext] = 1
        else:
            dir_cnt += 1

    print(dir_cnt, 'directories')  # 指定したディレクトリも含む
    print(file_cnt, 'files')
    for k, v in ext_cnt.items():
        print(k.upper(), ':', v, 'files (', round(v/file_cnt*100, 2), '% )')


# ファイルの情報を表示する
def show_file_info(fpath, use_mtime_for_birthtime=False):

    result = os.stat(fpath)

    size = result.st_size                                     # ファイルサイズ
    atime = datetime.datetime.fromtimestamp(result.st_atime)  # 最終アクセス日時
    mtime = datetime.datetime.fromtimestamp(result.st_mtime)  # 最終内容更新日時 ( = 撮影日時 )
    ctime = None                                              # メタデータの最終更新日時(UNIX) / 作成日時(Windows)

    # ctimeはOSによって以下の処理で分岐
    if platform.system() == 'Windows':
        ctime = datetime.datetime.fromtimestamp(result.st_ctime)
    else:                                # MacOS含むFreeBSD系など
        try:
            ctime = datetime.datetime.fromtimestamp(result.st_birthtime)  # 存在すればbirthtimeを使う
        except AttributeError:
            if use_mtime_for_birthtime:  # birthtimeの代わりにmtimeを使用するオプション
                ctime = mtime

    # 取得した値を表示
    print('size:', size)
    print('atime', atime)
    print('mtime', mtime)
    print('ctime', ctime)


def main():

    # parser setting
    parser = argparse.ArgumentParser(description='画像や動画ファイルを分類したりリネームしたりするソフトです')
    parser.add_argument('arg1', help='実行する処理を指定します \nファイルの分類: clsby\nファイルのリネーム: renby')
    parser.add_argument('arg2', help='処理に応じて必須項目を入力します')
    # 共通のオプションを設定
    parser.add_argument('--src', help='入力元のフォルダを指定します (デフォルトで現在のフォルダ)' )
    parser.add_argument('--dest', help='出力先のフォルダを指定します (デフォルトで現在のフォルダ)')
    parser.add_argument('--target', help='処理を適用するファイル拡張子を空白区切りで指定します (デフォルトで JPG PNG HEIC)')
    parser.add_argument('--recursive', help='入力元フォルダ直下のファイルのみ処理します (デフォルトで無効)')
    parser.add_argument('--safety', help='入力元フォルダからPC本体へファイルをコピーしてから処理を実行します (デフォルトで有効)')
    # 分類におけるオプション
    parser.add_argument('--exiftagname', help='exifタグの名称を指定します')
    # リネームにおけるオプション
    parser.add_argument('--rentype', help='リネームタイプを指定します')
    parser.add_argument('--altname', help='対象の情報が存在しない場合にファイル名として与える文字列を指定します')
    parser.add_argument('--cntstarts', help='連番の開始番号を指定します')
    parser.add_argument('--renmethod', help='リネーム文字列の配置をカスタマイズします')

    args = parser.parse_args()

    # デフォルト値の設定
    SRC_DIR = '.'                                # コピー元のディレクトリ
    DEST_DIR = '.'                               # 処理後のファイルの保存先ディレクトリ
    TARGET_EXT = ['jpg', 'jpeg', 'png', 'heic']  # 処理の対象とする拡張子
    RECURSIVE = True                             # ファイル検索の際，サブフォルダ以下を含める
    SAFETY = True                                # SRC_DIR から一度コピーして処理を実行

    # オプションに応じてデフォルト値を更新
    if args.src:
        SRC_DIR = args.src
    if args.dest:
        DEST_DIR = args.dest
    if args.target:
        TARGET_EXT = args.target.split(' ')
    if args.recursive != None:
        RECURSIVE = bool(int(args.recursive))
    if args.safety != None:
        SAFETY = bool(int(args.safety))

    # パース結果のテスト
    # print(f"SRC_DIR = {SRC_DIR}")
    # print(f"DEST_DIR = {DEST_DIR}")
    # print(f"TARGET_EXT = {TARGET_EXT}")
    # print(f"RECURSIVE = {RECURSIVE}")

    # パスのチェック
    if not os.path.exists(SRC_DIR):
        print('参照元のディレクトリが存在しません')
        sys.exit()
    if not os.path.exists(DEST_DIR):
        print('出力先のディレクトリが存在しません')
        sys.exit()

    # 対象のファイルパスを取得
    fpath_list = get_all_files(SRC_DIR, TARGET_EXT=TARGET_EXT, recursive=RECURSIVE)
    print(f'{len(fpath_list)}件のファイルが見つかりました')

    # 入力元フォルダからファイルをコピー
    if SAFETY:
        print('一時フォルダにコピーします')
        imported_dir = import_all(fpath_list, DEST_DIR)  # DEST_DIR以下にコピー
        SRC_DIR = imported_dir                           # SRC_DIRを更新

    # 実行する処理ごとに分岐
    mode = args.arg1
    if mode == 'clsby':   # 分類処理
        print('指定された全ファイルを分類します')
        fpath_list = get_all_files(SRC_DIR, TARGET_EXT=TARGET_EXT)
        # 分類オプションで分岐
        cls_mode = args.arg2
        if cls_mode == 'ext':  # 拡張子でフォルダ分け
            cls_by_ext(fpath_list, DEST_DIR)
        elif cls_mode == 'year':
            cls_by_dt_original(fpath_list, DEST_DIR, 'year')
        elif cls_mode == 'month':
            cls_by_dt_original(fpath_list, DEST_DIR, 'month')
        elif cls_mode == 'day':
            cls_by_dt_original(fpath_list, DEST_DIR, 'day')
        elif cls_mode == 'exiftag':  # 非推奨
            if args.exiftagname:
                tag_name = args.exiftagname
            else:
                print('exifタグの名称を指定してください')
                sys.exit()
            cls_by_exif(fpath_list, DEST_DIR, tag_name)
        else:
            print('有効な分類モードを入力してください')
            sys.exit()

    elif mode == 'renby':  # リネーム処理
        print('指定された全ファイルをリネームします')
        fpath_list = get_all_files(SRC_DIR, TARGET_EXT=TARGET_EXT)

        ren_method = ['REPLACEALL', '']
        if args.renmethod:
            ren_method = args.renmethod.split('=')

        # リネームオプションで分岐 (テーブルの作成のみ)
        ren_mode = args.arg2
        if ren_mode == 'datetime_original':  # 撮影日時でリネーム
            ren_table = make_ren_table(fpath_list, tag_name='EXIF DateTimeOriginal', dt_fmt='%Y-%m-%d-%H%M%S', uk_custom=('Unknown-', 1, 4))
        elif ren_mode != None:               # 任意文字列でリネーム
            ren_table = make_ren_table(fpath_list, ren_method=ren_method)
        else:
            print('有効なリネームモードを入力してください')
            sys.exit()
        # テーブルに従ってリネームの実行
        rename_by_table(ren_table)

    else:
        print('第1引数の値が不正です\n有効な引数は [clsby], [renby] のみです')
        sys.exit()

    print('finished at main()')


if __name__ == '__main__':
    main()