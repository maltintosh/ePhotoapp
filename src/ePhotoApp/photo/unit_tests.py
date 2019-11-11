"""
本当はtests.pyでテストをすべきだが
DBを使わないとエラーが出るので
こちらで我慢する。
としようとしたが
django.core.exceptions.ImproperlyConfigured: Requested setting INSTALLED_APPS, but settings are not configured. You must either define the environment variable DJANGO_SETTINGS_MODULE or call settings.configure() before accessing settings.
というエラーが出たのでこちらも実行できず。
"""
import unittest as ut
import sys, os
sys.path.append('../ePhotoApp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
from django.conf import settings

django.setup()

settings.configure(
    DEBUG=True,
    # DATABASES={"default": {
    #     "ENGINE": "django.db.backends.sqlite3",
    #     "NAME": ":memory:"
    # }},
    INSTALLED_APPS=[__name__]
)

from models import Photo, _get_image_path

class TestPhotoModel(ut.TestCase):

    def setUp(self):
        self.photo = Photo()
        self.photo.id_setting()

    def test_id_not_None(self):
        self.assertIsNotNone(self.photo.id)

    def test_randomness_of_id(self):
        self.photo2 = Photo()
        self.photo2.id_setting()
        self.assertNotEqual(self.photo.id, self.photo2.id)
    
    def test_image_path(self):
        path = _get_image_path(self.photo, 'sample.jpg')
        self.assertEqual(path, 'photo/photos/' + self.photo.id + '.jpg')

if __name__ == "__main__":
    # s.configure() 
    ut.main()
