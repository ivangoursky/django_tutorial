from django.urls import path

from . import views

app_name = "sudoku"

urlpatterns = [
    path('', views.index_view, name='index'),
    path('generate_byngiven/<int:ngiven>/', views.generate, name='byngiven'),
    path('saved/<int:sudoku_id>/', views.saved, name='saved'),
    path('save/<int:dim_field>/<int:dim_house>/<str:sudoku_state>/', views.save, name='save'),
    path('leave_a_comment/<int:sudoku_id>/', views.leave_a_comment, name='leave_a_comment'),
    path('login/', views.login_form, name='login_form'),
    path('login_user/', views.login_user, name='login_user'),
    path('register/', views.register_form, name='register_form'),
    path('register_user/', views.register_user, name='register_user'),
    path('logout', views.logout_user, name='logout'),
]
