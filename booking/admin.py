from django.contrib import admin
from .models import Room, Food, Booking, Cart, CartItem

# Register your models here.
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1

class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]

class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'room', 'check_in_date', 'check_out_date', 'total_price']
    search_fields = ['user__username', 'room__room_number']

admin.site.register(Room)
# ลบการลงทะเบียน Food แบบธรรมดา
# admin.site.register(Food)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Cart, CartAdmin)

# FoodAdmin class สำหรับแสดงข้อมูล Food
class FoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'description', 'stock']
    list_editable = ['stock']

# ลงทะเบียน Food ด้วย FoodAdmin
admin.site.register(Food, FoodAdmin)
