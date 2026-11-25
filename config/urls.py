
from django.contrib import admin
from django.urls import path, include
from accounts.views import home_page, student_grade_page
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_page, name="home"),
    path("api/accounts/", include("accounts.urls")),
    path(
        "student/grade/<int:grade>/",
        student_grade_page,
        name="student-grade"
    ),
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
