from django.db import models
from django.utils import simplejson as json


class JsonStore(models.Model):
    json_data = models.TextField(blank=True)

    # whether to raise AttributeError when asked for missing key or just return None
    raise_attribute_errors = False

    class Meta:
        abstract = True

    def __getattr__(self, name):
        try:
            return super(JsonStore, self).__getattr__(name)
        except AttributeError:
            if name.startswith('_'):
                raise AttributeError(name)
            try:
                return self._get_data()[name]
            except KeyError:
                if self.raise_attribute_errors:
                    raise AttributeError(name)

    def __setattr__(self, name, value):
        if name.startswith('_') or self._is_field(name):
            return super(JsonStore, self).__setattr__(name, value)
        self._get_data()[name] = value

    def __delattr__(self, name):
        if name.startswith('_') or self._is_field(name):
            return super(JsonStore, self).__delattr__(name, value)
        del self._get_data()[name]

    def _is_field(self, name):
        return name in sum([(f.name, f.attname) for f in self._meta.fields], ())

    def _get_data(self):
        if not hasattr(self, '__data'):
            data = (json.loads(self.json_data, encoding='utf-8')
                    if self.json_data else {})
            object.__setattr__(self, '__data', data)
        return object.__getattribute__(self, '__data')

    def get(self, name, default=None):
        return getattr(self, name, default)

    def save(self, *args, **kwargs):
        data = self._get_data()
        self.json_data = json.dumps(data, ensure_ascii=False)
        super(JsonStore, self).save(*args, **kwargs)
