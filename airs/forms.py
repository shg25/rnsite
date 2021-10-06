from django import forms

from .models import Air


class AirCreateByShareTextForm(forms.ModelForm):
    class Meta:
        model = Air
        fields = ['share_text']  # シェアラジオのテキストだけ入力してスタート
