from django import forms

from .models import Air, Nanitozo


class AirCreateByShareTextForm(forms.ModelForm):
    # TODO share_text廃止のためModelFormだとよくないので差し替える
    class Meta:
        model = Air
        # fields = ['share_text']  # シェアラジオのテキストだけ入力してスタート
        fields = ['overview_before']  # share_textの代わりに一時利用


class AirUpdateForm(forms.ModelForm):
    # 放送概要編集
    class Meta:
        model = Air
        fields = (
            'overview_before',
            'overview_after',
        )


class NanitozoUpdateForm(forms.ModelForm):
    # 感想編集
    class Meta:
        model = Nanitozo
        fields = (
            'comment_recommend',
            'comment',
            'comment_negative',
            'comment_open',
        )
