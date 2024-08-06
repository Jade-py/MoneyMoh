from django.contrib import admin
from django.urls import path, register_converter
from base.views import index, post_data, get_today, get_data


class FloatConverter:
    regex = r'\d*\.\d+|\d+'

    def to_python(self, value):
        return float(value)


register_converter(FloatConverter, 'float')

urlpatterns = [
    path('', index),
    path('admin/', admin.site.urls),
    path('post/', post_data),
    path('get/<int:year>/<int:month>/<int:day>', get_data),
    path('get/today/', get_today)
]
