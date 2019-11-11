from django.db import models
from django.utils import timezone
from .class_dict import CLASS_DICT
import django
import json, os, uuid, random
from .errors import *

def _get_image_path(instance, filename):
    """カスタマイズした画像パスを取得する.

    :param instance: インスタンス (models.Model)
    :param filename: 元ファイル名
    :return: カスタマイズしたファイル名を含む画像パス
    """
    name = instance.name
    extension = os.path.splitext(filename)[-1]
    instance.set_extension(extension)
    # if instance.editing == False:
    #     n = Photo.DEFAULT_NUM
    # else:
    #     n = 
    path = instance.PREFIX_PHOTO + name + extension
    # instance.set_id(name)
    return path

class Photo(models.Model):
    image = models.ImageField(upload_to=_get_image_path)
    title = models.CharField(max_length=30)
    # date = models.DateTimeField(max_length=30)
    place = models.CharField(max_length=30)
    comments = models.CharField(max_length=500)
    # id = str(uuid.uuid4()).replace('-', '')
    PREFIX_PHOTO = 'photo/photos/' # settings.pyで特殊に設定してある。
    PREFIX_JSON = 'media/photo/json/' # src/ePhotoAppからのpath
    LIST_PATH = 'media/photo/photo_list.json'
    DEFAULT_NUM = 1

    photo_list = None

    def name_setting(self, is_edit, name=None):
        if is_edit:
            self.name = name
        else:
            self.name = str(uuid.uuid4())

    def set_tag(self, tag):
        self.tag = list(set(tag))
    
    def set_extension(self, ext):
        self.ext = ext
    
    # def set_edit_mode(self, name, ext):
    #     if ext[0] != '.':
    #         raise ValueError("ext は拡張子でセットすること")
    #     path = Photo.PREFIX_PHOTO + name + ext
    #     # if not os.path.exists(path):
    #     #     raise FileNotFoundError(path + "が見つかりません")
    #     self.editing = True
    #     self.edit_path = path

    def _as_dict(self, pre_js=None):
        if pre_js is not None:
            self.title = self.title or pre_js['title']
            self.place = self.place or pre_js['place']
            self.comments = self.comments or pre_js['comments']
            self.tag = pre_js['tag']
            self.ext = pre_js['ext']
        return dict(
            # image=self.image.path,
            name=self.name,
            title=self.title,
            # date=self.date, #.isoformat(),
            place=self.place,
            comments=self.comments,
            tag=self.tag,
            ext=self.ext,
            # edit=self.edit_n
            )

    def image_save(self, is_edit, prev_path=None):
        if is_edit:
            self.editing = True
            # if ext is None or prev_path is None:
            #     raise TypeError("Neither 'ext' nor 'prev_path' should be None as edit_save")
            # self.set_edit_mode(self.name, ext)
            # if os.path.exists(self.edit_path):
            #     print(self.edit_path + " is being rewrriten")
        else:
            self.editing = False
        try: 
            super().save()
        except django.db.utils.OperationalError:
            pass # db errorを潰す
        if is_edit:
            if self.ext != prev_path['ext']:
                os.remove(Photo.photo_path(prev_path['name'], prev_path['ext']))
                print(prev_path + " removed.")
            else:
                print(prev_path + " rewritten.")
            
    
    def json_save(self, is_edit, pre=None):
        js = self._as_dict(pre)
        path = Photo.json_path(self.name)
        if is_edit:
            if not os.path.exists(path):
                raise FileNotFoundError("JSONファイルが存在しません")
            if pre is None:
                raise TypeError("編集時にJSONでセットするときには'pre'を設定してください")
            
            with open(path, 'w') as f:
                json.dump(js, f)
            print(path + " rewritten.")
        else:
            try:      
                with open(path, 'x') as f:
                    json.dump(js, f)
            except FileExistsError:
                raise FileExistsError("すでにJSONファイルが存在します")
        
    def save_list_name(self, is_edit):
        """default: int 1枚目の番号"""
        if self.ext[0] != '.':
            raise ValueError("self.ext は拡張子でセットすること")
        photo_list = Photo.get_all_dict()
        if is_edit:
            photo_list[self.name] += 1
        else:
            photo_list.setdefault(self.name, Photo.DEFAULT_NUM) # 拡張子をjsonで保存
        Photo.save_all_list(photo_list)

    @staticmethod
    def get_all_dict(debug=True):

        if debug:
            with open(Photo.LIST_PATH, 'r') as f:
                photo_list_ = json.load(f)

        else:
            if Photo.photo_list is not None:
                return Photo.photo_list
            else:
                with open(Photo.LIST_PATH, 'r') as f:
                    photo_list_ = json.load(f)
                
        return photo_list_
    
    @staticmethod
    def get_all_uuids():
        return Photo.get_all_dict().keys()

    @staticmethod
    def save_all_list(photo_list):
        Photo.photo_list = photo_list
        with open(Photo.LIST_PATH, 'w') as f:
            json.dump(photo_list, f)
    
    @staticmethod
    def get_json(name):
        """return: dict"""
        with open(Photo.json_path(name), 'r') as f:
            js = json.load(f)
        return js
    
    @staticmethod
    def get_ext(name):
        return Photo.get_json(name)['ext']
        
    @staticmethod
    def photo_path(name, ext=None):
        if ext is None:
            return 'media/' + Photo.PREFIX_PHOTO + name + Photo.get_ext(name)
        else:
            return 'media/' + Photo.PREFIX_PHOTO + name + ext
    
    @staticmethod
    def json_path(name):
        return Photo.PREFIX_JSON + name + '.json'
    

    @staticmethod
    def photos(num, only_path=False, get_title_and_tag=False,shuffle=True): # numはshuffleのときしか使われていない、、
        photo_list = list(Photo.get_all_uuids()) # UUIDのリスト
        if shuffle:
            try:
                photo_list = random.sample(photo_list, num)
            except:
                raise PhotoTooFewError("十分な数の写真が保存されていません")
        if only_path:
            return map(Photo.photo_path, photo_list)
        elif get_title_and_tag:

            def get_json_path_title_tag(uuid):
                js = Photo.get_json(uuid)
                return Photo.photo_path(uuid), uuid, js['title'], Photo.tag_to_j_str(js['tag']) # uuid, title, tag

            return map(get_json_path_title_tag, photo_list)
                       
        else:
            return zip(map(Photo.photo_path, photo_list),
                       photo_list)

    @staticmethod
    def to_jap(eng):
        try:
            j = CLASS_DICT[eng]
        except KeyError:
            raise KeyError(eng +" はtag一覧にありません")
        return j
    
    @staticmethod
    def to_eng(jap):
        l = [k for k, v in CLASS_DICT.items() if v == jap]
        if len(l) == 0:
            raise KeyError(jap +" はtag一覧にありません")
        return l[0]
    
    @staticmethod
    def tag_to_j_str(tags_list):
        japs = map(Photo.to_jap, tags_list)
        s = ''
        for jap in japs:
            s += jap + ', '
        return s[:-2]

    @staticmethod
    def get_random_one_except(tag_almost, n):
        """n: int 間違い探しの数(間違いを含む)
        ChosenTagTooFewErrorとOtherPhotosTooFewErrorを送出
        """
        almost_uuids = Photo.search(tag_almost, None)
        if len(almost_uuids) < n - 1:
            raise ChosenTagTooFewError("十分な数の" + tag_almost + "の写真が見つかりません")
        almost_uuids = random.sample(almost_uuids, n - 1)
        all_uuids = list(Photo.get_all_uuids())
        random.shuffle(all_uuids)
        ex_uuid = None
        for uuid in all_uuids:
            js = Photo.get_json(uuid)
            if not tag_almost in js['tag']:
                ex_uuid = uuid
        if ex_uuid is None:
            raise OtherPhotosTooFewError(tag_almost + "でない写真が見つかりません")
        uuids = almost_uuids
        uuids.append(ex_uuid)
        random.shuffle(uuids)
        return uuids, ex_uuid
                  
    @staticmethod
    def _json_generator():
        # jsons = {}
        for uuid in Photo.get_all_uuids():
            yield uuid, Photo.get_json(uuid)
        #     jsons.setdefault(uuid, Photo.get_json(uuid))
        # return jsons

    @staticmethod
    def search(tag, keywords):
        if tag is not None and tag != '':
            print("A"); print(tag)
            uuids = \
                [uuid for uuid, js in Photo._json_generator() if tag in js['tag'] and _search_item_json(js, keywords)]
        elif keywords != [''] or keywords:
            print("B")
            uuids = \
                [uuid for uuid, js in Photo._json_generator() if _search_item_json(js, keywords)]
        else:
            raise ValueError("tag is None かつ keywords=() 何も探してません")
        print(uuids)
        return uuids

def _search_item_json(js, keywords, keys=('title', 'place', 'comments', 'tag'), mode='and'):
    """keysの順も重要"""
    print(keywords)
    print("WWW")
    if mode != 'and' and mode != 'or':
        raise ValueError("mode must be either 'and' or 'or'")

    if keywords == [''] or not keywords:
        return True
    for keyword in keywords:
        if not _search_item_one_keyword(js, keyword, keys):
            return False
    return True # 全部に見つかって初めてTrue
                
def _search_item_one_keyword(js, keyword, keys):
    print(keyword)
    print("AAA")
    for key in keys:
        if key == 'tag':
            # English
            for tag in js['tag']:
                if tag in keyword:
                    return True

            # Japanese
            for tag in js['tag']:
                j_tag = Photo.to_jap(tag)
                if j_tag in keyword:
                    return True

        else:
            if keyword in js[key]:
                return True
        
    
