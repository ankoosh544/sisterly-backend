from django import forms


class EmailResetForm(forms.Form):
    email = forms.EmailField(label='New email', max_length=60)
