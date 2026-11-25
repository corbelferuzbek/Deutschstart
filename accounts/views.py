
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate, get_user_model

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import RegisterSerializer
from .authentication import enforce_csrf

User = get_user_model()

SESSION_MAX_AGE = 30 * 24 * 60 * 60


# ==========================================
# REDIRECT URL
# ==========================================

def get_user_redirect_url(user):
    if user.role == User.Role.STUDENT:
        try:
            grade = user.student_profile.grade
            if grade in [2, 3, 4, 5, 6]:
                return f"/student/grade/{grade}/"
        except User.student_profile.RelatedObjectDoesNotExist:
            pass

    # Teacher va admin sahifalari keyingi bosqichda qo‘shiladi.
    return "/"


# ==========================================
# COOKIE SETTINGS
# ==========================================

def cookie_options():
    return {
        "httponly": True,
        "secure": not settings.DEBUG,
        "samesite": "Lax",
    }


def set_auth_cookies(response, refresh):
    access = refresh.access_token
    options = cookie_options()

    response.set_cookie(
        "access_token",
        str(access),
        max_age=SESSION_MAX_AGE,
        path="/",
        **options
    )

    response.set_cookie(
        "refresh_token",
        str(refresh),
        max_age=SESSION_MAX_AGE,
        path="/api/accounts/",
        **options
    )


def clear_auth_cookies(response):
    response.delete_cookie(
        "access_token",
        path="/",
        samesite="Lax"
    )

    response.delete_cookie(
        "refresh_token",
        path="/api/accounts/",
        samesite="Lax"
    )


# ==========================================
# HTML PAGES
# ==========================================

def home_page(request):
    return render(request, "index.html")


@ensure_csrf_cookie
def register_page(request):
    return render(request, "accounts/register.html")


@ensure_csrf_cookie
def login_page(request):
    return render(request, "accounts/login.html")


# ==========================================
# STUDENT GRADE PAGE
# ==========================================

def student_grade_page(request, grade):
    raw_token = request.COOKIES.get("access_token")

    if not raw_token:
        return redirect("/api/accounts/page/login/")

    try:
        token = AccessToken(raw_token)
        user_id = token["user_id"]
        user = User.objects.get(id=user_id, is_active=True)

    except (TokenError, User.DoesNotExist, KeyError, TypeError, ValueError):
        return redirect("/api/accounts/page/login/")

    if user.role != User.Role.STUDENT:
        return redirect("/")

    try:
        actual_grade = user.student_profile.grade
    except User.student_profile.RelatedObjectDoesNotExist:
        return redirect("/")

    if actual_grade not in [2, 3, 4, 5, 6]:
        return redirect("/")

    # URL'dagi sinf profilidagi sinfga mos bo‘lishi shart.
    if grade != actual_grade:
        return redirect(f"/student/grade/{actual_grade}/")

    return render(
        request,
        "students/grade_dashboard.html",
        {
            "student": user,
            "grade": actual_grade,
            "course_group": (
                "Junior Deutsch"
                if actual_grade in [2, 3, 4]
                else "Deutsch Plus"
            ),
        }
    )


# ==========================================
# REGISTER API
# ==========================================

@api_view(["POST"])
@permission_classes([AllowAny])
def register_api(request):
    enforce_csrf(request._request)

    serializer = RegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    user = serializer.save()
    refresh = RefreshToken.for_user(user)

    response = Response(
        {
            "message": "Hisob muvaffaqiyatli yaratildi.",
            "redirect_url": get_user_redirect_url(user),
        },
        status=status.HTTP_201_CREATED
    )

    set_auth_cookies(response, refresh)
    return response


# ==========================================
# LOGIN API
# ==========================================

@api_view(["POST"])
@permission_classes([AllowAny])
def login_api(request):
    enforce_csrf(request._request)

    username = request.data.get("username", "").strip()
    password = request.data.get("password", "")

    if not username or not password:
        return Response(
            {"message": "Login va parolni kiriting."},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(
        request,
        username=username,
        password=password
    )

    if user is None:
        return Response(
            {"message": "Login yoki parol noto‘g‘ri."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {"message": "Hisob faol emas."},
            status=status.HTTP_403_FORBIDDEN
        )

    refresh = RefreshToken.for_user(user)

    response = Response(
        {
            "message": "Muvaffaqiyatli login.",
            "redirect_url": get_user_redirect_url(user),
        },
        status=status.HTTP_200_OK
    )

    set_auth_cookies(response, refresh)
    return response


# ==========================================
# REFRESH TOKEN API
# ==========================================

@api_view(["POST"])
@permission_classes([AllowAny])
def refresh_api(request):
    enforce_csrf(request._request)

    refresh_token = request.COOKIES.get("refresh_token")

    if not refresh_token:
        return Response(
            {"message": "Refresh token topilmadi. Qayta login qiling."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    serializer = TokenRefreshSerializer(
        data={"refresh": refresh_token}
    )

    if not serializer.is_valid():
        response = Response(
            {"message": "Sessiya tugagan. Qayta login qiling."},
            status=status.HTTP_401_UNAUTHORIZED
        )
        clear_auth_cookies(response)
        return response

    new_refresh = serializer.validated_data.get("refresh")

    if not new_refresh:
        response = Response(
            {"message": "Token yangilanmadi. Qayta login qiling."},
            status=status.HTTP_401_UNAUTHORIZED
        )
        clear_auth_cookies(response)
        return response

    refresh = RefreshToken(new_refresh)

    response = Response(
        {"message": "Sessiya muvaffaqiyatli yangilandi."},
        status=status.HTTP_200_OK
    )

    set_auth_cookies(response, refresh)
    return response


# ==========================================
# LOGOUT API
# ==========================================

@api_view(["POST"])
@permission_classes([AllowAny])
def logout_api(request):
    enforce_csrf(request._request)

    refresh_token = request.COOKIES.get("refresh_token")

    if refresh_token:
        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            pass

    response = Response(
        {"message": "Tizimdan chiqildi."},
        status=status.HTTP_200_OK
    )

    clear_auth_cookies(response)
    return response
