from django.test import SimpleTestCase, TestCase
from .models import BaseModel


class BaseModelTest(TestCase):

    def setUp(self):
        BaseModel.objects.create(event='test', price=10.00)

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_post_data(self):
        response = self.client.post('/post/', {'event': 'test', 'price':10})
