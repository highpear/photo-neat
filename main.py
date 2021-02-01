from PIL import Image
import sys, os, glob, shutil, datetime

from classify import *
from exifio import *
from rename import *


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
            return read_heif(fpath)
        else:                       # Pillowで読み込む
            return Image.open(fpath)

    except:
        print('error:')
        sys.exit()


# heic形式の画像を読み込む
def read_heif(fpath):
    im_heif = pyheif.read(fpath)
    im = Image.frombytes(
        im_heif.mode,
        im_heif.size, 
        im_heif.data,
        "raw",
        im_heif.mode,
        im_heif.stride,
        )
    return im


# dir以下の指定拡張子のファイルパスをリストで取得
def get_all_files(dir, TARGET_EXT=[], recursive=True):     # AAEを含めるオプションを追加
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


# リスト内のファイルを全て指定のフォルダ以下の現在時刻フォルダへコピーする
def import_all(fpath_list, dest_dir):

    # dest_dir以下に現在時刻でフォルダを生成する
    dt_now = str(datetime.datetime.now())          # 現在時刻を文字列で取得 (ex. 2021-01-29 21:15:58.592992)

    dir_name = dt_now.split('.')[0]                # 小数点以下の秒を除去
    dir_name = dir_name.replace(' ', '-')          # 空白を除去
    dir_name = dir_name.replace(':', '')           # コロンを除去

    dest_dir = os.path.join(dest_dir, dir_name)    # コピー先パスを生成

    if os.path.exists(dest_dir):                   # 生成するフォルダが既に存在するかチェック (インポート実行毎に新規フォルダを生成するので既存の場合はエラーとする)
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


def show_fpath_list(fpath_list, include_dir=False):
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
        
        if include_dir:
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
def show_file_info(fpath):
    result = os.stat(fpath)
    print('size:', result.st_size)                                    # MB
    print('atime', datetime.datetime.fromtimestamp(result.st_atime))  # 最終アクセス日時
    print('mtime', datetime.datetime.fromtimestamp(result.st_mtime))  # 最終内容更新日時 ( =撮影日時 )
    print('ctime', datetime.datetime.fromtimestamp(result.st_ctime))  # メタデータの最終更新日時 (UNIX) / 作成日時 (Windows)
    try:
        print('birthtime', datetime.datetime.fromtimestamp(result.st_birthtime))  # 作成日時 (macOSを含むFreeBSD系)
    except AttributeError as e:
        return


def main():

    # 写真をコピーする基底ディレクトリを指定
    SRC_DIR = './TestImg'           # 通常はデバイスのDCIM等を参照

    # コピー先のディレクトリを指定
    DEST_DIR = './Original'         # Original以下にインポートされる(SRC_DIRからコピー)

    # 対象とする画像ファイル形式を指定 (小文字)
    TARGET_EXT = ['jpg', 'jpeg', 'png', 'heic']

    # 条件に一致する全画像ファイルのパスをリストで取得
    fpath_list = get_all_files(SRC_DIR, TARGET_EXT)
    
    # SRC_DIR以下をOriginal以下にコピー
    # imported_dir = import_all(fpath_list, DEST_DIR)

    # コピー(インポート)された全ファイルを取得
    # imported_fpath_list = get_all_files(imported_dir, TARGET_EXT)
    show_fpath_list(fpath_list)

    # show_dir_info('../../../Downloads/DCIM') # 思い
    show_file_info('../../../Downloads/DCIM/104APPLE/IMG_4055.MOV')
    



    # 拡張子でフォルダ分け (ムーブ)
    # cls_by_ext(imported_fpath_list, imported_dir)

    # exif情報でフォルダ分け (ムーブ)
    # cls_by_exif(imported_fpath_list, imported_dir, 'Image Model')
    # cls_by_dt_original(imported_fpath_list, imported_dir, 'year')
   


    # 撮影日時でリネーム
    # fpath_list = get_all_files(imported_dir, TARGET_EXT)
    # ren_table = make_ren_table(fpath_list, tag_name='EXIF DateTimeOriginal', dt_fmt='%Y-%m-%d-%H%M%S', uk_custom=('不明-', 1, 3))
    # rename_by_table(ren_table)


    print('finished at main()')


if __name__ == '__main__':
    main()