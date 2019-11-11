from django.shortcuts import render, redirect
from .forms import PhotoForm, EditForm
from .models import Photo
from .game import Game
from .class_dict import CLASS_DICT
from .errors import *

#Model preparation
#Variables
# What model to download
from .model.research.object_detection import Object_Detection_Demo

def post_list(req):
    return render(req, 'photo/edit.html', {})

def index(req):
    try:
        photos =  Photo.photos(min(len(Photo.get_all_dict()), 28), get_title_and_tag=True)
    except PhotoTooFewError:
        photos = []
    return render(req, 'photo/index.html', {
        'photos': photos
    })

def gallery(req):
     TAG = req.GET.get('tag_class')
     KEY = req.GET.get('key_word')
     if TAG is None or KEY is None:
        uuids_path = []
     elif TAG=='' and KEY=='':
        uuids_path = []
     else:
        UUIDs = Photo.search(TAG, KEY.split())

        if UUIDs == []:
            uuids_path = []
        else:
            uuids_path = zip(map(Photo.photo_path, UUIDs), UUIDs) ##################

     return render(req, 'photo/gallery.html',  {
        # 'photos': Photo.photos(1, only_path=True), # ###################
         "key": KEY,
         "tag1": TAG,
         "uuids": uuids_path,
     })


def about(req):
     return render(req, 'photo/about.html', {})

def contact(req):
     return render(req, 'photo/contact.html', {})

def preview(req, name):
    name = str(name)
    js = Photo.get_json(name)
    return render(req, 'photo/preview.html', {
        'photo_path' : Photo.photo_path(name),
        'title' : js['title'],
        'place' : js['place'],
        'comments' : js['comments'],
        'id'    : js['name'],
        'tag'   : Photo.tag_to_j_str(js['tag']),
        'json_dict' : zip(['ID','タイトル','場所',"コメント","タグ"], js.values()),
        # 'con_names' : 
    })

def upload(req):
    if req.method == 'GET':
        return render(req, 'photo/upload.html', {
            'form': PhotoForm(),
        })

    elif req.method == 'POST':                                                     
        form = PhotoForm(req.POST, req.FILES)
        if not form.is_valid():
            raise ValueError('invalid form')

        photo = Photo()
        photo.name_setting(is_edit=False)
        photo.image = form.cleaned_data['image']
        photo.title = form.cleaned_data['title']
        photo.place = form.cleaned_data['place']
        photo.comments = form.cleaned_data['comments']

        tags = Object_Detection_Demo.class_detection(photo.image)
        if tags == []:
            tags.append("Other class")
        photo.set_tag(tags)

        #photo.set_tag([])
        photo.image_save(is_edit=False)
        photo.json_save(is_edit=False)
        photo.save_list_name(is_edit=False)


        return redirect('/'+ photo.name)

def edit(req, name):
    name = str(name) # UUID -> str
    js = Photo.get_json(name)

    if req.method == 'GET':
        return render(req, 'photo/edit.html', {
            'form': EditForm(),
            'photo_path': Photo.photo_path(name),
            'title' : js['title'],
            'place' : js['place'],
            'comments' : js['comments'],
            'id'    : js['name'],
            'tag'   : Photo.tag_to_j_str(js['tag']),

        })
    
    elif req.method == 'POST':                                                     
        form = EditForm(req.POST, req.FILES)
        if not form.is_valid():
            raise ValueError('invalid form')

        photo = Photo()
        photo.name_setting(is_edit=True, name=name)
        photo.image = None
        photo.title = form.cleaned_data['title']
        photo.place = form.cleaned_data['place']
        photo.comments = form.cleaned_data['comments']
        photo.json_save(is_edit=True, pre=js)

        photo.save_list_name(is_edit=True)

        return redirect('/'+ photo.name)

def game(req):
    BEGIN = req.GET.get('begin')
    REPLY = req.GET.get('reply')

    if BEGIN is not None:
        if BEGIN not in CLASS_DICT.keys() or BEGIN == 'Other class':
            # beginへredirect
            return _forced_termination(f"予期しないbeginの値: {BEGIN} です")

        try:
            Game.begin(BEGIN)
        except ChosenTagTooFewError:
            # もう一度beginに戻る

            print('選ばれたタグの写真が足りません')
            return render(req, 'photo/begin.html', {
                 'tag': BEGIN,
                 'error': '選ばれたタグの写真が足りません'
            })
        except OtherPhotosTooFewError:
            # もう一度beginに戻る

            print('選ばれたタグ以外の写真が足りません')
            return render(req, 'photo/begin.html', {
                 'tag': BEGIN,
                 'error': '選ばれたタグ以外の写真が足りません'
            })

        try:
            tag, uuids = Game.get_tag_and_uuids()
            if tag != BEGIN:
                raise RuntimeError
        except RuntimeError:
            return _forced_termination()

        return render(req, 'photo/services.html', {
            'tag': tag,
            'uuids': zip(map(Photo.photo_path, uuids), uuids),
        })
    
    else:
        if REPLY is not None:
            if not Game.is_playing:
                return _forced_termination()

                
            try:
                _, uuids = Game.get_tag_and_uuids()
            except RuntimeError:
                return _forced_termination()
                
            if not REPLY in uuids:
                # beginへredirect
                return _forced_termination(f"無効なUUID {REPLY}\nを受け取りました")
               
            try:
                is_right = Game.judge(REPLY) # 正しい回答かを返す
            except RuntimeError: 
                # Gameのクラスフィールドが異常な値の時, beginへredirect
                return _forced_termination()

                
            if not is_right: # 間違えた時ページを移動しない
                print(f"{REPLY} は間違い")
                try:
                    tag, uuids = Game.get_tag_and_uuids()
                except RuntimeError:
                    return _forced_termination()

                return render(req, 'photo/services.html', {
                    'tag': tag,
                    'uuids': zip(map(Photo.photo_path, uuids), uuids),

                    # 'prev_reply': REPLY, 
                })
            else: # 答えが正しいときの処理
                try:
                    tag, _ = Game.proper_end()
                except RuntimeError:
                    return _forced_termination("クリア時にエラーが出ました")

                print("ゲームクリア")

                return render(req, 'photo/results.html', {
                    'tag': tag
                })
        else:
            # BEGIN, REPLY が空なのでbeginページへ
            return render(req, 'photo/begin.html', {})

    
def _forced_termination(message="ゲームが異常終了しました"):
    Game.forced_end()
    print(message)
    return redirect('/game')
