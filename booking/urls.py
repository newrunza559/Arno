from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings


app_name = 'booking'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),  # ให้แน่ใจว่ากำหนดชื่อว่า 'login'
    path('cart/', views.cart_view, name='cart'),
    path('remove_from_cart/<int:food_id>/', views.remove_from_cart, name='remove_from_cart'),  # ลบสินค้าออกจากตะกร้า
    path('checkout/', views.checkout, name='checkout'),  # ไปยังหน้าชำระเงิน
    path('order_confirmation/<int:booking_id>/', views.order_confirmation, name='order_confirmation'),
    path('add_to_cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('room/<int:room_id>/mark-as-available/', views.mark_room_as_available, name='mark_room_as_available'),
    path('rooms/', views.room_list, name='room_list'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('book-room/<int:room_id>/', views.book_room, name='book_room'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
