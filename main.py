from PIL import Image
import sys, os, glob

from classify import *
from exifread import *
from rename import *

# 処理を行うディレクトリ カレントを指定
DIR = './'
TEST_IMG = 'JPG/pix.jpg'


def im_open(fpath):
    try:
        im = Image.open(fpath)
        return im
    except exception as e:
        print('error: ', e)
        sys.exit()

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


def main():

    TARGET_EXT = ['jpg', 'jpeg', 'png']
    fpath_list = get_all_files('./Original', TARGET_EXT)

    # 拡張子でフォルダ分け (コピー)
    # cls_by_ext(fpath_list, './classified/')

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