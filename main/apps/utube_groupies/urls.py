from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('utubegroupies/', views.home),
    path('utubegroupies/signup/', views.regLoginPage),
    path('utubegroupies/signup/processRegister/', views.processRegister),
    path('utubegroupies/signup/processRegister/email/', views.processRegisterEmail),
    path('utubegroupies/signup/processLogin/', views.processLogin),
    path('utubegroupies/signup/processLogin/email/', views.processLoginEmail),
    path('utubegroupies/dashboard/', views.dashboard),
    path('utubegroupies/dashboard/createSesh/', views.createSesh),
    path('utubegroupies/dashboard/createSesh/videoSearch/', views.searchYoutube),
    path('utubegroupies/dashboard/createSesh/videoSearch/videoResults/', views.searchResultsYT),
    path('utubegroupies/dashboard/createSesh/videoSearch/videoResults/addVideo/<slug:vid>', views.addVideoToSesh),
    path('utubegroupies/dashboard/createSesh/usersSearch/', views.searchUsers),
    path('utubegroupies/dashboard/createSesh/usersSearch/usersResults/', views.searchResultsUsers),
    path('utubegroupies/dashboard/createSesh/usersSearch/addUser/<int:uid>/', views.addUserToSesh),
    path('utubegroupies/dashboard/createSesh/submitSesh/', views.submitSesh),
    path('utubegroupies/dashboard/acceptInvitation/<int:id>/', views.acceptInvitation),
    path('utubegroupies/dashboard/sesh/<int:id>/', views.showSesh),
    path('utubegroupies/logout/', views.logout),
]