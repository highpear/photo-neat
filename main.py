from PIL import Image
import sys, os, glob, shutil

from classify import *
from exifread import *
from rename import *


# パスから画像をオープン
def im_open(fpath):
    try:
        im = Image.open(fpath)
        return im
    except exception as e:
        print('error:', e)
        sys.exit()


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


# リスト内のファイルを全て指定のフォルダ以下にコピーする
def copy_all_files(fpath_list, dest_dir):
    cnt = 0
    for fpath in fpath_list:
        base_name = os.path.basename(fpath)
        dest_path = os.path.join(dest_dir, base_name)
        print(dest_path)
        shutil.copy2(fpath, dest_path)
        cnt += 1

    print('{} files were copied to [ {} ]'.format(cnt, dest_dir))


def main():

    # 写真をコピーする基底ディレクトリを指定
    SRC_DIR = '.'

    # コピー先のディレクトリを指定
    DEST_DIR = './Original'

    # 対象とする画像ファイル形式を指定 (小文字)
    TARGET_EXT = ['jpg', 'jpeg', 'png']

    # 条件に一致する全画像ファイルのパスをリストで取得
    fpath_list = get_all_files(SRC_DIR, TARGET_EXT)

    # SRC_DIR以下をOriginal以下にコピー
    # copy_all_files(fpath_list, DEST_DIR)


    # 拡張子でフォルダ分け (コピー)
    # cls_by_ext(fpath_list, DEST_DIR)

    # exif情報でフォルダ分け (ムーブ)
    # cls_by_exif_tag(get_all_files('./classified/JPG', TARGET_EXT), './classified/JPG', 272)

    # exif情報が同じか判定
    # print(has_same_exif('./20210108-130337.jpg', './20210108-195647.jpg'))

    # 撮影日時でリネーム
    rename_by_exif_tag(fpath_list, 36867)  # DatetimeOriginal



    # print(len(TAGS.keys())) # 260
    print('finished at main()')


if __name__ == '__main__':
    main()