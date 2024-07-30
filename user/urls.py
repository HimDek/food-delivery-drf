from django.urls import path
from .views import CreateUsers, GetPhoneOTP, GetEmailOTP, RetrieveSelfUser, RetrieveUpdateSelfUserProfile

app_name = "user"

urlpatterns = [
    path("", CreateUsers.as_view(), name="createUsers"),
    path("phoneotp/", GetPhoneOTP.as_view(), name="getPhoneOTP"),
    path("emailotp/", GetEmailOTP.as_view(), name="getEmailOTP"),
    path("self/", RetrieveSelfUser.as_view(), name="retrieveSelfUser"),
    path(
        "profile/",
        RetrieveUpdateSelfUserProfile.as_view(),
        name="retrieveUpdateSelfUserProfile",
    ),
]
