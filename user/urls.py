from django.urls import path
from .views import CreateUsers, GetOTP, RetrieveSelfUser, RetrieveUpdateSelfUserProfile

app_name = "user"

urlpatterns = [
    path("", CreateUsers.as_view(), name="createUsers"),
    path("otp/", GetOTP.as_view(), name="getOTP"),
    path("self/", RetrieveSelfUser.as_view(), name="retrieveSelfUser"),
    path(
        "profile/",
        RetrieveUpdateSelfUserProfile.as_view(),
        name="retrieveUpdateSelfUserProfile",
    ),
]
