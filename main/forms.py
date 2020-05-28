from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import CustomUser, Code, Profile

profile_fields_list = ('first_name',
                       'last_name',
                       'gender',
                       'template')

profile_images_list = ('avatar', 'plate_img_1', 'plate_img_2', 'plate_img_3', 'plate_img_4')


class SignInForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class SignUpForm(UserCreationForm):

    def validate_invitation(value):
        bitcoin_alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz_'
        if len(value) < 8 and len(value) > 0:
            raise ValidationError("Incorrect code length", code="invite_len")
        elif len(value) == 8 and any(symbol not in bitcoin_alphabet for symbol in value):
            raise ValidationError("Incorrect symbols in code", code='incorrect_invite')
        else:
            try:
                Code.objects.get(code=value)
            except Code.DoesNotExist:
                raise ValidationError("%(value) code does not exist!", params={'value': value},
                                      code='invite_dsnt_exist')

    invitation_code = forms.CharField(label='Invitation code',
                                      max_length=8,
                                      required=False,
                                      validators=[validate_invitation],
                                      error_messages={'invite_len': 'Incorrect code length',
                                                      'incorrect_invite': 'Incorrect symbols in code',
                                                      'invite_dsnt_exist': 'This code dode does not exist'})

    def clean_invitation_code(self):
        data = self.cleaned_data
        code = data['invitation_code']
        try:
            return Code.objects.get(code=code)
        except Code.DoesNotExist:
            if not code:
                return None
            else:
                raise ValidationError()

    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2', 'invitation_code')


class ProfileFillForm(forms.ModelForm):

    def __init__(self, *args, images=False, **kwargs):
        super(ProfileFillForm, self).__init__(*args, **kwargs)
        for field in profile_fields_list:
            self.fields[field].required = True
        for field in profile_images_list:
            self.fields[field].required = images

    class Meta:
        model = Profile
        fields = profile_fields_list + profile_images_list
