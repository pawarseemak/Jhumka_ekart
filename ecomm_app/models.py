from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Product(models.Model):
    CAT=((1,'Jhumkas'),(2, 'Necklaces'),(3, 'Braclets'))
    name=models.CharField(max_length=50, verbose_name='Product Name')
    price=models.FloatField()
    pdetails=models.CharField(max_length=200, verbose_name="Product Details")
    cat=models.IntegerField(verbose_name="Category", choices=CAT)
    is_active=models.BooleanField(default=True, verbose_name="Available")
    pimage=models.ImageField(upload_to='image')

    #def __str__(self):
       # return self.name

class Cart(models.Model):
    uid=models.ForeignKey(User,on_delete=models.CASCADE,db_column="uid")
    pid=models.ForeignKey(Product,on_delete=models.CASCADE,db_column="pid")
    qty=models.IntegerField(default=1)

class Order(models.Model):
    order_id=models.CharField(max_length=50)
    uid=models.ForeignKey(User,on_delete=models.CASCADE,db_column="uid")
    pid=models.ForeignKey(Product,on_delete=models.CASCADE,db_column="pid")
    qty=models.IntegerField(default=1)

class Query(models.Model):
    name=models.CharField(max_length=50)
    mobile=models.IntegerField()
    query=models.CharField(max_length=200)


