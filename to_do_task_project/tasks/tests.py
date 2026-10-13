from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from tasks.forms import TaskForm
from tasks.models import TaskModel

User = get_user_model()


class UserModelTests(TestCase):
    """Tests for the CustomUserInfoModel."""

    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            full_name='Test User',
            email='test@example.com',
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.full_name, 'Test User')
        self.assertTrue(user.check_password('testpass123'))

    def test_user_str(self):
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            full_name='Test User',
        )
        self.assertEqual(str(user), 'testuser - Test User')


class TaskModelTests(TestCase):
    """Tests for the TaskModel."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )

    def test_create_task(self):
        task = TaskModel.objects.create(
            user=self.user,
            title='Test Task',
            description='A test task',
            status='Pending',
        )
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.user, self.user)
        self.assertEqual(task.status, 'Pending')

    def test_task_str(self):
        task = TaskModel.objects.create(user=self.user, title='My Task')
        self.assertEqual(str(task), 'My Task')

    def test_task_str_untitled(self):
        task = TaskModel.objects.create(user=self.user, title='')
        self.assertEqual(str(task), '(Untitled)')

    def test_task_default_status(self):
        task = TaskModel.objects.create(user=self.user, title='Task')
        self.assertEqual(task.status, 'Pending')

    def test_task_ordering(self):
        """Tasks should be ordered by -created_at (newest first).
        Since test tasks may share the same timestamp, we verify
        the queryset uses the declared ordering."""
        task1 = TaskModel.objects.create(user=self.user, title='First')
        task2 = TaskModel.objects.create(user=self.user, title='Second')
        tasks = list(TaskModel.objects.all())
        self.assertEqual(len(tasks), 2)
        # Verify the model Meta ordering is set correctly
        self.assertEqual(TaskModel._meta.ordering, ['-created_at'])


class TaskFormTests(TestCase):
    """Tests for the TaskForm."""

    def test_valid_form(self):
        form = TaskForm(data={
            'title': 'Test Task',
            'description': 'A description',
            'status': 'Pending',
        })
        self.assertTrue(form.is_valid())

    def test_empty_title_invalid(self):
        form = TaskForm(data={
            'title': '',
            'description': 'A description',
            'status': 'Pending',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_whitespace_title_invalid(self):
        form = TaskForm(data={
            'title': '   ',
            'status': 'Pending',
        })
        self.assertFalse(form.is_valid())

    def test_form_fields(self):
        form = TaskForm()
        self.assertEqual(
            list(form.fields.keys()),
            ['title', 'description', 'status', 'due_date'],
        )


class RegisterViewTests(TestCase):
    """Tests for registration."""

    def test_register_page_get(self):
        response = self.client.get(reverse('register_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_register_success(self):
        response = self.client.post(reverse('register_page'), {
            'full_name': 'Test User',
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'securepass123',
            'confirm_password': 'securepass123',
        })
        self.assertRedirects(response, reverse('login_page'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_password_mismatch(self):
        response = self.client.post(reverse('register_page'), {
            'username': 'newuser',
            'password': 'password123',
            'confirm_password': 'different123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_register_duplicate_username(self):
        User.objects.create_user(username='existing', password='pass12345')
        response = self.client.post(reverse('register_page'), {
            'username': 'existing',
            'password': 'password123',
            'confirm_password': 'password123',
        })
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_redirected(self):
        user = User.objects.create_user(username='test', password='pass12345')
        self.client.login(username='test', password='pass12345')
        response = self.client.get(reverse('register_page'))
        self.assertRedirects(response, reverse('home_page'))


class LoginViewTests(TestCase):
    """Tests for login."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )

    def test_login_page_get(self):
        response = self.client.get(reverse('login_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_success(self):
        response = self.client.post(reverse('login_page'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertRedirects(response, reverse('home_page'))

    def test_login_invalid_credentials(self):
        response = self.client.post(reverse('login_page'), {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_redirected(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('login_page'))
        self.assertRedirects(response, reverse('home_page'))


class LogoutViewTests(TestCase):
    """Tests for logout."""

    def test_logout_redirects_to_login(self):
        user = User.objects.create_user(username='test', password='pass12345')
        self.client.login(username='test', password='pass12345')
        response = self.client.get(reverse('logout_page'))
        self.assertRedirects(response, reverse('login_page'))

    def test_logout_requires_login(self):
        response = self.client.get(reverse('logout_page'))
        self.assertEqual(response.status_code, 302)


class HomeViewTests(TestCase):
    """Tests for home page."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )

    def test_home_requires_login(self):
        response = self.client.get(reverse('home_page'))
        self.assertEqual(response.status_code, 302)

    def test_home_page_shows_summary(self):
        self.client.login(username='testuser', password='testpass123')
        TaskModel.objects.create(user=self.user, title='T1', status='Pending')
        TaskModel.objects.create(user=self.user, title='T2', status='Completed')
        response = self.client.get(reverse('home_page'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_tasks'], 2)
        self.assertEqual(response.context['pending_tasks'], 1)
        self.assertEqual(response.context['completed_tasks'], 1)


class TaskListViewTests(TestCase):
    """Tests for task list."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser', password='testpass123'
        )

    def test_task_list_requires_login(self):
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 302)

    def test_task_list_shows_own_tasks_only(self):
        TaskModel.objects.create(user=self.user, title='My Task')
        TaskModel.objects.create(user=self.other_user, title='Other Task')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('task_list'))
        self.assertEqual(len(response.context['task_data']), 1)
        self.assertEqual(response.context['task_data'][0].title, 'My Task')


class AddTaskViewTests(TestCase):
    """Tests for adding tasks."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_add_task_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('add_task'))
        self.assertEqual(response.status_code, 302)

    def test_add_task_get(self):
        response = self.client.get(reverse('add_task'))
        self.assertEqual(response.status_code, 200)

    def test_add_task_post_valid(self):
        response = self.client.post(reverse('add_task'), {
            'title': 'New Task',
            'description': 'Description',
            'status': 'Pending',
        })
        self.assertRedirects(response, reverse('task_list'))
        task = TaskModel.objects.get(title='New Task')
        self.assertEqual(task.user, self.user)

    def test_add_task_post_invalid(self):
        response = self.client.post(reverse('add_task'), {
            'title': '',
            'status': 'Pending',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TaskModel.objects.count(), 0)


class UpdateTaskViewTests(TestCase):
    """Tests for updating tasks."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser', password='testpass123'
        )
        self.task = TaskModel.objects.create(
            user=self.user, title='Original', status='Pending'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_update_task_get(self):
        response = self.client.get(
            reverse('update_task', args=[self.task.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_update_task_post(self):
        response = self.client.post(
            reverse('update_task', args=[self.task.id]),
            {'title': 'Updated', 'status': 'Completed'},
        )
        self.assertRedirects(response, reverse('task_list'))
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated')
        self.assertEqual(self.task.status, 'Completed')

    def test_cannot_update_other_users_task(self):
        other_task = TaskModel.objects.create(
            user=self.other_user, title='Other', status='Pending'
        )
        response = self.client.get(
            reverse('update_task', args=[other_task.id])
        )
        self.assertEqual(response.status_code, 404)


class DeleteTaskViewTests(TestCase):
    """Tests for deleting tasks."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser', password='testpass123'
        )
        self.task = TaskModel.objects.create(
            user=self.user, title='To Delete', status='Pending'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_delete_task_post(self):
        response = self.client.post(
            reverse('delete_task', args=[self.task.id])
        )
        self.assertRedirects(response, reverse('task_list'))
        self.assertEqual(TaskModel.objects.count(), 0)

    def test_delete_task_get_not_allowed(self):
        response = self.client.get(
            reverse('delete_task', args=[self.task.id])
        )
        self.assertEqual(response.status_code, 405)

    def test_cannot_delete_other_users_task(self):
        other_task = TaskModel.objects.create(
            user=self.other_user, title='Other', status='Pending'
        )
        response = self.client.post(
            reverse('delete_task', args=[other_task.id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertTrue(TaskModel.objects.filter(id=other_task.id).exists())
