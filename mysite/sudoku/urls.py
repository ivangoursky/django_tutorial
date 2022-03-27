from django.urls import path

from . import views

app_name = "sudoku"

urlpatterns = [
    path('', views.index_view, name='index'),
    path('generate_byngiven/<int:ngiven>/', views.generate, name='byngiven'),
    path('saved/<int:sudoku_id>/', views.saved, name='saved'),
    path('save/<int:dim_field>/<int:dim_house>/<str:sudoku_state>/', views.save, name='save'),
]
