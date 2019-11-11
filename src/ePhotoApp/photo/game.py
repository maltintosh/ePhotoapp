from .models import Photo


class Game(object):
    is_playing = False
    ex_uuid = None
    tag_almost = None
    uuids = []

    @classmethod
    def begin(cls, tag_almost, n=28):
        """ChosenTagTooFewErrorとOtherPhotosTooFewErrorを送出
        """
        cls.tag_almost = tag_almost
        cls.uuids, cls.ex_uuid = \
            Photo.get_random_one_except(tag_almost, n)

        cls.is_playing = True

    @classmethod
    def judge(cls, uuid):
        if not cls.is_playing or cls.ex_uuid is None:
            print(cls.is_playing, cls.ex_uuid)
            raise RuntimeError("Not playing")
        return cls.ex_uuid == uuid

    @classmethod
    def forced_end(cls):
        cls.is_playing = False
        cls.ex_uuid = None
        cls.tag_almost = None
        cls.uuids = []

    @classmethod
    def proper_end(cls):
        if not cls.is_playing:
            raise RuntimeError("Not playing")
        cls.is_playing = False
        tag, uuids = cls.tag_almost, cls.uuids
        cls.ex_uuid = None
        cls.tag_almost= None
        cls.uuids = []
        return tag, uuids


    
    @classmethod
    def get_tag_and_uuids(cls):
        if not cls.is_playing or not cls.tag_almost or not cls.uuids:
            print(cls.is_playing, cls.tag_almost, cls.uuids)
            raise RuntimeError("Not playing")
        return cls.tag_almost, cls.uuids
        
