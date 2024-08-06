from django.db import models

# Create your models here.


class BaseModel(models.Model):
    event = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.event
