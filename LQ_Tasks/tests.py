# accounts/tests.py (или tasks/tests.py, в зависимости от структуры проекта)
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import CustomUser
from .models import Task

class TaskTests(APITestCase):
    def setUp(self):
        # Создаем пользователя и авторизуем его
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_create_task(self):
        url = '/api/tasks/'
        data = {'title': 'New Task', 'priority': 5}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Task')
        self.assertEqual(response.data['priority'], 5)

    def test_get_task_list(self):
        # Создаем задачу
        Task.objects.create(title='Sample Task', priority=5, user=self.user)
        url = '/api/tasks/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)  # Убедитесь, что в ответе есть данные

    def test_high_priority_tasks(self):
        # Создаем задачи с различными приоритетами
        Task.objects.create(title='Low Priority Task', priority=5, user=self.user)
        Task.objects.create(title='High Priority Task', priority=8, user=self.user)
        url = '/api/tasks/high_priority/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # В ответе только задачи с приоритетом >= 7
        for task in response.data:
            self.assertGreaterEqual(task['priority'], 7)

    def test_unauthorized_access(self):
        # Проверяем доступ без авторизации
        self.client.logout()
        url = '/api/tasks/'
        response = self.client.post(url, {'title': 'New Task', 'priority': 5}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_task(self):
        # Создаем задачу
        task = Task.objects.create(title='Old Task', priority=5, user=self.user)
        url = f'/api/tasks/{task.id}/'
        data = {'title': 'Updated Task', 'priority': 7}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Task')
        self.assertEqual(response.data['priority'], 7)

    def test_delete_uncompleted_task(self):
        # Создаем задачу
        task = Task.objects.create(title='Task to be deleted', priority=5, user=self.user)
        url = f'/api/tasks/{task.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Проверяем, что задача не была удалена
        self.assertEqual(Task.objects.count(), 1)
    
    def test_delete_completed_task(self):
        task = Task.objects.create(title='Task to be deleted', priority=8, status='COMPLETED', user=self.user)
        url = f'/api/tasks/{task.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Проверяем, что задача удалена
        self.assertEqual(Task.objects.count(), 0)

