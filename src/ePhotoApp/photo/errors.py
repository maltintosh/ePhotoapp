
class PhotoTooFewError(Exception):
    """写真が足りないことを表すエラー"""
    pass

class ChosenTagTooFewError(PhotoTooFewError):
    """選ばれたタグの写真が足りないことを表すエラー"""
    pass

class OtherPhotosTooFewError(PhotoTooFewError):
    """選ばれたタグ以外の写真が足りないことを表すエラー"""
    pass