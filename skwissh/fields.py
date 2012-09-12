from django.db import models
from django import forms
from django.conf import settings
import binascii
import random
import string


class EncryptedString(str):
    pass


class BaseEncryptedField(models.Field):
    def __init__(self, *args, **kwargs):
        cipher = kwargs.pop('cipher', 'AES')
        imp = __import__('Crypto.Cipher', globals(), locals(), [cipher], -1)
        self.cipher = getattr(imp, cipher).new(settings.SECRET_KEY[:32])
        models.Field.__init__(self, *args, **kwargs)

    def to_python(self, value):
        try:
            return self.cipher.decrypt(binascii.a2b_hex(str(value))).split('\0')[0]
        except:
            return str(value)

    def get_db_prep_value(self, value, connection, prepared=False):
        if value is not None and not isinstance(value, EncryptedString):
            padding = self.cipher.block_size - len(value) % self.cipher.block_size
            if padding and padding < self.cipher.block_size:
                value += "\0" + ''.join([random.choice(string.printable) for i in range(padding - 1)])  # @UnusedVariable 'i'
            value = EncryptedString(binascii.b2a_hex(self.cipher.encrypt(value)))
        return value


class EncryptedTextField(BaseEncryptedField):
    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return 'TextField'

    def formfield(self, **kwargs):
        defaults = {'widget': forms.Textarea}
        defaults.update(kwargs)
        return super(EncryptedTextField, self).formfield(**defaults)


class EncryptedCharField(BaseEncryptedField):
    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return "CharField"

    def formfield(self, **kwargs):
        defaults = {'max_length': self.max_length}
        defaults.update(kwargs)
        return super(EncryptedCharField, self).formfield(**defaults)

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^skwissh\.fields\.BaseEncryptedField"])
    add_introspection_rules([], ["^skwissh\.fields\.EncryptedCharField"])
    add_introspection_rules([], ["^skwissh\.fields\.EncryptedTextField"])
except ImportError:
    pass

