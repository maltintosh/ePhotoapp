from django import forms                                                           


class PhotoForm(forms.Form):
    image = forms.ImageField(label='画像')
    title = forms.CharField(label='タイトル')
    # date = forms.CharField(label='日付')
    place = forms.CharField(label='撮影場所')
    comments = forms.CharField(label='コメント')

class EditForm(forms.Form):
    title = forms.CharField(label='タイトル', required=False)
    # date = forms.CharField(label='日付')
    place = forms.CharField(label='撮影場所', required=False)
    comments = forms.CharField(label='コメント', required=False)