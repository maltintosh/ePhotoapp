# from django.db import models
# from django.utils import timezone
# import json, os, uuid

# class Photo(object):

#     prefix_photo = 'media/photo/photos/' # settings.pyで特殊に設定してある。
#     prefix_json = 'media/photo/json/' # src/ePhotoAppからのpath

#     def __init__(self):
#         self.image = models.ImageField(upload_to=_get_image_path)
#         self.title = models.CharField(max_length=30)
#         self.date = models.DateTimeField(max_length=30)
#         self.place = models.CharField(max_length=30)
#         self.comments = models.CharField(max_length=500)
#         self.id = str(uuid.uuid4()).replace('-', '')
        
#     def set_tag(self, tag):
#         self.tag = tag

#     def as_json(self):
#         return dict(
#             # image=self.image.path,
#             name=self.name,
#             tag=self.tag,
#             title=self.title,
#             date=self.date, #.isoformat(), 
#             place=self.place,
#             comments=self.comments)
    
#     def photo_save(self):
#         extension = os.path.splitext(self.image.name)[-1]
#         with open(prefix_photo + self.name + extension) as pic:
#             pic