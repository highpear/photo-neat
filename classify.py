import os, shutil
from exifio import *
from PIL.ExifTags import TAGS


# リストで渡された全ファイルをdest_dir以下に拡張子毎に分類する (デフォルトでムーブ)
def cls_by_ext(fpath_list, dest_dir, move=True, jpeg2jpg=True):

    for fpath in fpath_list:
        ext = fpath.split('.')[-1].upper()     # 拡張子を大文字で取得

        if jpeg2jpg:  # JPGとJPEGを統一する
            if ext == 'JPEG':
                ext = 'JPG'

        ext_dir = os.path.join(dest_dir, ext)  # 各拡張子でフォルダを作成

        if not os.path.exists(ext_dir):        # 拡張子のフォルダが存在しなければ新規作成
            os.mkdir(ext_dir)
            print('DIR_CREATED : new directory [', ext_dir, '] was created')

        fname = fpath.split('/')[-1]              # パスからファイル名のみ取得
        dest_path = os.path.join(ext_dir, fname)  # ムーブ先のパスを生成

        if move:
            shutil.move(fpath, dest_path)                # ムーブを実行
            print('FILE_MOVED : file [', fpath, '] was moved to [', dest_path, ']')
        else:                             
            shutil.copy2(fpath, dest_path)               # コピーを実行
            print('FILE_COPIED : file [', fpath, '] was copied to [', dest_path, ']')



# リストで渡された全ファイルをexif情報ごとにフォルダ分けする (デフォルトでムーブ)
def cls_by_exif(fpath_list, dest_dir, exif_name, move=True):

    for fpath in fpath_list:
        tags = get_exif(fpath)
        tag_val = get_val_from_tags(tags, exif_name)       # タグ情報を取得

        if not tag_val:                                    # 対応するexif情報なし
            tag_val = 'Unknown'
            print('UNKNOWN_VALUE : file [', fpath , '] has no value of', exif_name)

        tag_val_dir = os.path.join(dest_dir, str(tag_val))   # タグ情報をディレクトリ名とする
        
        if not os.path.exists(tag_val_dir):             # タグ情報のフォルダが存在しなければ新規作成
            os.mkdir(tag_val_dir)
            print('DIR_CREATED : new directory [', tag_val_dir, '] was created')

        fname = fpath.split('/')[-1]                     # パスからファイル名のみ取得
        dest_path = os.path.join(tag_val_dir, fname)     # ムーブ先のパスを生成
       
        if move:
            shutil.move(fpath, dest_path)                # ムーブを実行
            print('FILE_MOVED : file [', fpath, '] was moved to [', dest_path, ']')
        else:                             
            shutil.copy2(fpath, dest_path)               # コピーを実行
            print('FILE_COPIED : file [', fpath, '] was copied to [', dest_path, ']')
