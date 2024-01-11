from django.urls import path
from djoser.views import UserViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from apps.account.views import CustomUserViewSet

urlpatterns = [
    path('register/', CustomUserViewSet.as_view({'post': 'create'}), name="register"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('activate/', UserViewSet.as_view({'post': 'activation'}), name='user-activate'),
    path('reset_password/', UserViewSet.as_view({'post': 'reset_password'}), name='user-reset_password'),
    path('reset_password_confirm/', UserViewSet.as_view({'post': 'reset_password_confirm'}),
         name='reset_password_confirm'),
]
