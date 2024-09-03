from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import CustomUser
from .models import SubTask, Task, Note

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



class SubTaskTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        self.task = Task.objects.create(title='Main Task', priority=5, user=self.user)

    def test_create_subtask(self):
        url = reverse('subtask-list', kwargs={'task_pk': self.task.id})
        data = {
                    'title': 'Subtask 1',
                    'description': 'Description for subtask 1',
                    'priority': 4,
                    'status': 'CREATED',
                    'task': self.task.id
                }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SubTask.objects.count(), 1)
        self.assertEqual(SubTask.objects.get().title, 'Subtask 1')

    def test_get_subtasks(self):
        subtask1 = SubTask.objects.create(task=self.task, title='SubTask 1')
        subtask2 = SubTask.objects.create(task=self.task, title='SubTask 2')

        url = reverse('task-subtasks', args=[self.task.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], subtask1.title)
        self.assertEqual(response.data[1]['title'], subtask2.title)

    def test_update_subtask(self):
        subtask = SubTask.objects.create(task=self.task, title='Old SubTask')
        url = reverse('subtask-detail', args=[self.task.id, subtask.id])
        data = {'title': 'Updated SubTask'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(SubTask.objects.get().title, 'Updated SubTask')

    def test_delete_subtask(self):
        subtask = SubTask.objects.create(task=self.task, title='SubTask to delete')
        url = reverse('subtask-detail', args=[self.task.id, subtask.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(SubTask.objects.count(), 0)

    def test_subtask_belongs_to_task(self):
        subtask = SubTask.objects.create(task=self.task, title='SubTask 1')
        self.assertEqual(subtask.task, self.task)


class NoteTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.task = Task.objects.create(title='Test Task', description='Test description', priority=5, status='CREATED', user=self.user)
        self.subtask = SubTask.objects.create(title='Test SubTask', description='Test subtask description', priority=4, status='CREATED', task=self.task)

    def test_create_note_for_task(self):
        url = reverse('task-note-list',  args=[self.task.id])
        data = {
            'title': 'Test Note for Task',
            'content': 'Test note for task',
            'object_id': self.task.id,
            'content_type': ContentType.objects.get_for_model(Task).id,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(Note.objects.get().title, 'Test Note for Task')

    def test_create_note_for_subtask(self):
        url = reverse('subtask-note-list', args=[self.subtask.id, self.subtask.task.id])
        data = {
            'title': 'Test Note for SubTask',
            'content': 'This is a test note content for a subtask.',
            'content_type': ContentType.objects.get_for_model(SubTask).id,
            'object_id': self.subtask.id,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(Note.objects.get().title, 'Test Note for SubTask')

    def test_read_note(self):
        note = Note.objects.create(
            title='Test Note', 
            content='This is a test note.', 
            content_type=ContentType.objects.get_for_model(Task), 
            object_id=self.task.id,
            content_object=self.task
            )
        url = reverse('task-note-detail', args=[self.task.id, note.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Note')

    def test_update_note(self):
        note = Note.objects.create(
            title='Initial Title', 
            content='Initial content', 
            content_type=ContentType.objects.get_for_model(Task), 
            object_id=self.task.id,
            content_object=self.task
        )
        url = reverse('task-note-detail', kwargs={'task_pk': self.task.id, 'pk': note.id})
        data = {'title': 'Updated Title', 'content': 'Updated content'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Note.objects.get(id=note.id).title, 'Updated Title')

    def test_delete_note(self):
        note = Note.objects.create(
            title='Test Note', 
            content='This is a test note.', 
            content_type=ContentType.objects.get_for_model(Task), 
            object_id=self.task.id,
            content_object=self.task
        )
        url = reverse('task-note-detail', args=[self.task.id, note.id])
        response = self.client.get(url)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Note.objects.count(), 0)

    def test_permission_denied_for_note_creation_on_another_user_task(self):
        another_user = CustomUser.objects.create_user(username='anotheruser', password='anotherpass')
        another_task = Task.objects.create(title='Another Task', description='Test description', priority=5, status='CREATED', user=another_user)
        url = reverse('task-note-list', args=[self.task.id])
        data = {
            'title': 'Unauthorized Note',
            'content': 'Trying to create note on another user\'s task.',
            'content_type': ContentType.objects.get_for_model(Task).id,
            'object_id': another_task.id,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)