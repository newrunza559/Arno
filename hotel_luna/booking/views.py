from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from .models import Room, Food, Booking, Cart, CartItem
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import Room
from django.shortcuts import render, get_object_or_404, redirect

# ฟังก์ชันสำหรับการลงทะเบียน (Register)
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('booking:login')  # ถ้าสมัครสำเร็จให้กลับไปที่หน้า home
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# ฟังก์ชันสำหรับการเข้าสู่ระบบ (Login)
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('booking:index')  # แทนที่ด้วย URL ที่ต้องการให้ผู้ใช้ไปหลังจากเข้าสู่ระบบ
            else:
                # ถ้าผู้ใช้หรือรหัสผ่านไม่ถูกต้อง ให้แสดงข้อความผิดพลาด
                messages.error(request, "Invalid username or password.")
        else:
            # หากฟอร์มไม่ถูกต้องก็ให้แสดงข้อความผิดพลาด
            messages.error(request, "Please fill in the required fields correctly.")
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})



# ฟังก์ชันสำหรับหน้าหลัก (Home)
def index(request):
    rooms = Room.objects.all()
    foods = Food.objects.all()
    return render(request, 'index.html', {'rooms': rooms, 'foods': foods})

# ในฟังก์ชันการจองห้อง
def book_room(request, room_id):
    room = Room.objects.get(id=room_id)
    
    if request.method == 'POST':
        check_in_date = request.POST['check_in_date']
        check_out_date = request.POST['check_out_date']

        days_stayed = (datetime.strptime(check_out_date, '%Y-%m-%d') - datetime.strptime(check_in_date, '%Y-%m-%d')).days
        total_price = room.price_per_night * days_stayed

        # ทำการสร้างการจองห้อง
        booking = Booking(
            user=request.user,
            room=room,  # ตั้งค่าห้องให้กับการจอง
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            total_price=total_price
        )
        booking.save()
        room.is_available = False  # อัปเดตสถานะห้อง
        room.save()

        return redirect('booking:index')
    else:
        return render(request, 'booking/book_room.html', {'room': room})
    

# ฟังก์ชันแสดงตะกร้า (Cart View)
@login_required
def cart_view(request):
    if request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user)  # หา Cart ของ user
        cart_items = cart.cartitem_set.all()  # ดึงรายการสินค้าในตะกร้า
        return render(request, 'cart.html', {'cart_items': cart_items})
    else:
        return redirect('login')

# ฟังก์ชันการเพิ่มสินค้าในตะกร้า (Add to Cart)
@login_required
def add_to_cart(request, food_id):
    food = Food.objects.get(id=food_id)

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)

        # ตรวจสอบว่ามีสินค้าในตะกร้าหรือไม่
        cart_item, created = CartItem.objects.get_or_create(cart=cart, food=food)

        # ถ้าสินค้านั้นมีอยู่ในตะกร้าแล้วเพิ่มจำนวน
        if not created:
            cart_item.quantity += 1  # เพิ่มจำนวนสินค้าในตะกร้า
            cart_item.save()

        return redirect('booking:cart')  # รีไดเร็กไปที่หน้าตะกร้าใน namespace 'booking'
    else:
        return redirect('login')


# ฟังก์ชันการลบสินค้าออกจากตะกร้า (Remove from Cart)
@login_required
def remove_from_cart(request, food_id):
    if request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user)
        cart_item = CartItem.objects.get(cart=cart, food_id=food_id)
        cart_item.delete()

    return redirect('booking:cart')  # รีไดเร็กไปที่หน้าตะกร้าใน namespace 'booking'

# ฟังก์ชันสำหรับการเช็คเอาท์ (Checkout)
@login_required
def checkout(request):
    # ดึงตะกร้าของผู้ใช้
    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    
    # กำหนดวันที่เช็คอินและเช็คเอาท์ (กำหนดเป็นค่าปัจจุบันหรือที่เหมาะสม)
    check_in_date = timezone.now().date()  # ใช้วันที่ปัจจุบัน
    check_out_date = check_in_date  # ใช้วันที่เดียวกันในกรณีที่ไม่เกี่ยวข้องกับห้องพัก

    # คำนวณราคาทั้งหมด
    total_price = sum(item.food.price * item.quantity for item in cart_items)
    
    # สร้างรายการการจองอาหาร
    booking = Booking.objects.create(
        user=request.user,
        room=None,  # ไม่มีห้องพักสำหรับการจองอาหาร
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        total_price=total_price
    )

    # อัปเดต CartItems เพื่อเชื่อมโยงกับการจองนี้
    for cart_item in cart_items:
        cart_item.booking = booking  # ตั้งค่า booking ให้กับ CartItem
        cart_item.save()
    

    # รีไดเร็กต์ไปยังหน้าการยืนยันการจอง
    return redirect('booking:order_confirmation', booking_id=booking.id)



# ฟังก์ชันยืนยันการจอง (Order Confirmation)
def order_confirmation(request, booking_id):
    # ดึงข้อมูลการจองจาก ID
    booking = Booking.objects.get(id=booking_id)
    
    # ดึงข้อมูลการจองอาหารจาก CartItems ที่เกี่ยวข้องกับการจอง
    cart_items = CartItem.objects.filter(booking=booking)  # ดึง CartItem ของการจองนั้น
    
    # คำนวณราคาของอาหารทั้งหมด
    total_food_price = sum(item.food.price * item.quantity for item in cart_items)

    # ส่งข้อมูลการจองและราคาทั้งหมดไปยังเทมเพลต
    return render(request, 'booking/order_confirmation.html', {
        'booking': booking,
        'cart_items': cart_items,
        'total_food_price': total_food_price,
    })

@login_required
def user_dashboard(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'booking/user_dashboard.html', {'bookings': bookings})


@login_required
def cancel_booking(request, booking_id):
    booking = Booking.objects.get(id=booking_id, user=request.user)

    # ถ้า booking นี้มีห้องที่จองอยู่
    if booking.room:
        booking.room.is_available = True  # ทำให้ห้องว่าง
        booking.room.save()  # บันทึกสถานะห้องใหม่

    booking.delete()  # ลบการจองออก
    return redirect('booking:user_dashboard')



@login_required
def edit_booking(request, booking_id):
    booking = Booking.objects.get(id=booking_id, user=request.user)
    if request.method == 'POST':
        # update booking logic
        booking.save()
        return redirect('user_dashboard')
    return render(request, 'edit_booking.html', {'booking': booking})


def mark_room_as_available(request, room_id):
    try:
        room = Room.objects.get(id=room_id)
        room.is_available = True
        room.save()
        return redirect('booking:index')  # <<< แก้เป็น home ตรงนี้
    except Room.DoesNotExist:
        return render(request, 'error.html', {'message': 'Room not found.'})
    

@login_required
def room_list(request):
    rooms = Room.objects.all()
    return render(request, 'booking/room_list.html', {'rooms': rooms})

