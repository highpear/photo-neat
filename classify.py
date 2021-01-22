import os, shutil
from exif import *
from PIL.ExifTags import TAGS


# リストで渡された全ファイルをdest_dir以下に拡張子毎に分類する (コピー)
def cls_by_ext(fpath_list, dest_dir):

    for fpath in fpath_list:
        ext = fpath.split('.')[-1].upper()     # 拡張子を大文字で取得 
        ext_dir = os.path.join(dest_dir, ext)  # 各拡張子でフォルダを作成

        if not os.path.exists(ext_dir):        # 拡張子のフォルダが存在しなければ新規作成
            os.mkdir(ext_dir)
            print('new directory [', ext_dir, '] was created')

        fname = fpath.split('/')[-1]              # パスからファイル名のみ取得
        dest_path = os.path.join(ext_dir, fname)  # コピー先のパスを生成

        shutil.copy2(fpath, dest_path)            # コピーを実行


# リストで渡された全ファイルをtag_idに対応するexifタグごとにフォルダ分けする (ムーブ)
def cls_by_exif_tag(fpath_list, dest_dir, tag_id):

    for fpath in fpath_list:
        tag_name = get_exif(fpath).get(tag_id)  # tag_idからタグ情報を取得

        if not tag_name:                        # 対応するexif情報なし
            tag_name = 'Unknown'

        tag_name_dir = os.path.join(dest_dir, tag_name)  # タグ情報をディレクトリ名とする
        
        if not os.path.exists(tag_name_dir):             # タグ情報のフォルダが存在しなければ新規作成
            os.mkdir(tag_name_dir)
            print('new directory [', tag_name_dir, '] was created')

        fname = fpath.split('/')[-1]                     # パスからファイル名のみ取得
        dest_path = os.path.join(tag_name_dir, fname)    # ムーブ先のパスを生成 
       
        shutil.move(fpath, dest_path)                    # ムーブを実行
