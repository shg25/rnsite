from django import forms

from .models import Air

# TODO share_text廃止のためModelFormだとよくないので差し替える
class AirCreateByShareTextForm(forms.ModelForm):
    class Meta:
        model = Air
        # fields = ['share_text']  # シェアラジオのテキストだけ入力してスタート
        fields = ['overview_before'] # share_textの代わりに一時利用
