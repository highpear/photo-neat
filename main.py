from PIL import Image
import sys, os, glob

from classify import *
from exif import *
from rename import *

# 処理を行うディレクトリ カレントを指定
DIR = './'
TEST_IMG = 'JPG/pix.jpg'
# TEST_IMG = 'JPG/test.jpg'
# TEST_IMG = 'JPG/line.jpg'

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
    
    # cls_by_ext(get_all_files('./Original', ['jpg', 'jpeg', 'png']), './classified/')
    # cls_by_exif_tag(get_all_files('./classified/JPG', ['jpg', 'jpeg', 'png']), './classified/JPG', 272)

    
    # 試しに各ファイルの情報を表示
    # for fpath in fpath_list:
    #     im = im_open(fpath)
    #     print(im.size)

    print(has_same_exif('./20210108-130337.jpg', './20210108-195647.jpg'))  # exif情報が同じか判定


    # rename_all_by_exif_tag('./JPG/iPhone SE (2nd generation)/', 36867) # DatetimeOriginal



    # print(len(TAGS.keys())) # 260
    print('finished at main()')


if __name__ == '__main__':
    main()