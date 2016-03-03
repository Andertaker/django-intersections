# -*- coding: utf-8 -*-
from django import forms



class GroupsForm(forms.Form):
    links = forms.CharField(label=u'Ссылки', required=True,
                            widget=forms.Textarea(attrs={
                                'class': 'form-control',
                                'rows': '5',
                                'style': 'width: 100% !important;',
                                'placeholder': '''
Введите ссылки на группы соц. сетей 
(поддерживаются vkontakte, twitter, instagram)
                                ''',
                                'required': '',
                            }))
