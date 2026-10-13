from django.urls import path

from tasks.views import (
    add_task,
    delete_task,
    home_page,
    login_page,
    logout_page,
    register_page,
    task_list,
    update_task,
)

urlpatterns = [
    path('', register_page, name='register_page'),
    path('login/', login_page, name='login_page'),
    path('logout/', logout_page, name='logout_page'),

    path('home/', home_page, name='home_page'),
    path('tasks/', task_list, name='task_list'),
    path('tasks/add/', add_task, name='add_task'),
    path('tasks/<int:t_id>/update/', update_task, name='update_task'),
    path('tasks/<int:t_id>/delete/', delete_task, name='delete_task'),
]
