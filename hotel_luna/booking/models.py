from django.db import models
from django.contrib.auth.models import User

# Model สำหรับห้องพักในโรงแรม
class Room(models.Model):
    room_number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=100)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    description = models.TextField()
    image = models.ImageField(upload_to='room_images/', blank=True, null=True)  # <<< เพิ่มตรงนี้

    def __str__(self):
        return f"{self.room_number} - {self.room_type}"

# Model สำหรับอาหาร/ขนม
class Food(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='food_images/', null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)  # เพิ่มฟิลด์ stock สำหรับเก็บจำนวนสต็อก

    def __str__(self):
        return self.name

# Model สำหรับการจองห้องพัก
class Booking(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Booking by {self.user.username} for {self.room.room_number if self.room else 'No Room'}"

# Model สำหรับตะกร้าสินค้า
class Cart(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

# Model สำหรับรายการในตะกร้าสินค้า
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, null=False)  # เพิ่ม default=1 และ null=False
    booking = models.ForeignKey('Booking', null=True, blank=True, on_delete=models.SET_NULL)  # เพิ่มการเชื่อมโยงกับ Booking

    def __str__(self):
        return f"{self.food.name} x {self.quantity}"
