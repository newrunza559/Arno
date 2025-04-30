from django.contrib import admin
from django.urls import path, include  # include ต้องนำเข้า
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('booking.urls')),  # ไปเรียก urls ของแอป booking
        # ส่วนของ URL ที่เกี่ยวข้องกับการจอง
    path('booking/', include('booking.urls', namespace='booking')),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
# ให้ Django เสิร์ฟไฟล์มีเดียในโหมดพัฒนา
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)