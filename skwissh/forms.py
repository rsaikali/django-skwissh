from django import forms
from django.forms.fields import CharField
from django.forms.models import ModelForm
from django.forms.widgets import PasswordInput
from django.utils.translation import ugettext_lazy as _
from skwissh.models import Server, ServerGroup, Probe


class ProbeForm(ModelForm):
    use_sudo = forms.ChoiceField(label=_("Utilise 'sudo' ?"), choices=((True, _('Oui')), (False, _('Non'))), widget=forms.RadioSelect, initial=False)

    class Meta:
        model = Probe
        widgets = {"use_sudo": forms.RadioSelect}


class ServerForm(ModelForm):
    password = CharField(label=_(u'Mot de passe'), widget=PasswordInput(render_value=False), required=False)

    class Meta:
        model = Server
        fields = ('hostname', 'probes', 'ip', 'username', 'password')
        widgets = {"probes": forms.CheckboxSelectMultiple,
                   "password": forms.PasswordInput}


class ServerGroupForm(ModelForm):
    class Meta:
        model = ServerGroup
        fields = ('name', 'servers')
        widgets = {"servers": forms.CheckboxSelectMultiple}
