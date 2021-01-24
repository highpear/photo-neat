from PIL import Image
import sys, os, glob, shutil, datetime

from classify import *
from exifio import *
from rename import *


# パスから画像をオープン
def im_open(fpath):
    # 画像形式を判定
    ext = fpath.split('.')[-1].lower()
    
    if ext not in COMPAT_EXT:
        print('error: uncompatible file type [', ext, ']')
        sys.exit()

    try:
        if ext == 'heic':
            return read_heif(fpath)
        else:                       # Pillowで読み込む
            return Image.open(fpath)

    except exception as e:
        print('error:', e)
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
def get_all_files(dir, TARGET_EXT=[]):
    # 抽出したパスを格納するリスト
    fpath_list = []
    
    # 末尾の"/"を除去
    if dir[-1] == '/':
        dir = dir[:-1]

    # dir以下全てのファイルのパスを再帰的に取得
    files = glob.glob(dir + '/**', recursive=True)
    
    for file in files:
        # 拡張子を取得
        ext = file.split('.')[-1].lower()
        if os.path.isfile(file) and ext in TARGET_EXT:
            fpath_list.append(file)

    # 結果の出力
    print(len(fpath_list), 'files were extracted from [', dir+'/', '] and below')
    
    return fpath_list


# リスト内のファイルを全て指定のフォルダ以下の現在時刻フォルダへコピーする
def copy_all(fpath_list, dest_dir):

    # dest_dir以下に現在時刻でフォルダを生成する
    dt_now = str(datetime.datetime.now())        # 現在時刻を取得
    dt_now = dt_now.split('.')[0]                # 小数点以下の秒を除去

    dir_name = dt_now.replace(' ', '-')          # フォルダ名を生成
    dir_name = dir_name.replace(':', '')         # コロンを除去
    dest_dir = os.path.join(dest_dir, dir_name)  # パスを生成

    if os.path.exists(dest_dir):                 # 生成するフォルダが既に存在するかチェック
        print('error: directory [', dest_dir, '] is already exists')
        sys.exit()
    else:
        os.mkdir(dest_dir)                       # フォルダを新規作成
        print('directory [', dest_dir ,'] was created')

    # コピーを実行
    cnt = 0
    for fpath in fpath_list:
        base_name = os.path.basename(fpath)
        dest_path = os.path.join(dest_dir, base_name)
        print(dest_path)
        shutil.copy2(fpath, dest_path)
        cnt += 1

    print('{} files were copied to [ {} ]'.format(cnt, dest_dir))

    return dest_dir


def main():

    # 写真をコピーする基底ディレクトリを指定
    SRC_DIR = './TestImg'  # 通常はデバイスのDCIM等を参照

    # コピー先のディレクトリを指定
    DEST_DIR = './Original'

    # 対象とする画像ファイル形式を指定 (小文字)
    TARGET_EXT = ['jpg', 'jpeg', 'png', 'heic']

    # 条件に一致する全画像ファイルのパスをリストで取得
    fpath_list = get_all_files(SRC_DIR, TARGET_EXT)

    # SRC_DIR以下をOriginal以下にコピー
    copied_dir = copy_all(fpath_list, DEST_DIR)
    print(copied_dir)

    # コピーされた全ファイルを取得
    copied = get_all_files(copied_dir, TARGET_EXT)
    for fpath in copied:
        # show_details_by_exif(fpath)  # EXIFを表示
        pass

    # 拡張子でフォルダ分け (コピー)   fix: JPG JPEGが違うフォルダになる
    # cls_by_ext(copied, copied_dir)

    # exif情報でフォルダ分け (ムーブ)
    cls_by_exif(copied, copied_dir, 'Model')

    # 撮影日時でリネーム
    moved = get_all_files(copied_dir, TARGET_EXT)
    rename_by_exif(moved, 'DateTimeOriginal')


    print('finished at main()')


if __name__ == '__main__':
    main()