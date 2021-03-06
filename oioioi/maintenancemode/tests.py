from django.core.urlresolvers import reverse

from oioioi.base.tests import TestCase
from oioioi.maintenancemode.models import set_maintenance_mode, \
                                          get_maintenance_mode


class TestMaintenanceMode(TestCase):
    fixtures = ['test_users']

    def test_set_maintenance(self):
        set_maintenance_mode(True, 'test')
        info = get_maintenance_mode()
        self.assertEquals('test', info['message'])
        self.assertEquals(True, info['state'])
        set_maintenance_mode(False)
        info = get_maintenance_mode()
        self.assertEquals('', info['message'])
        self.assertEquals(False, info['state'])

    def test_not_logged_redirect(self):
        set_maintenance_mode(True, 'test message')
        response = self.client.get('/', follow=True)
        self.assertRedirects(response, reverse('maintenance'))
        self.assertEquals(response.context['message'], 'test message')
        self.assertContains(response, 'test message')
        response = self.client.post(reverse('login'))
        self.assertEquals(response.status_code, 200)

    def test_logged_user_redirect(self):
        set_maintenance_mode(True, 'test message')
        self.client.login(username='test_user')
        response = self.client.get('/', follow=True)
        self.assertRedirects(response, reverse('maintenance'))
        self.assertContains(response, 'test message')
        response = self.client.post(reverse('logout'), {
            'user': 'test_user',
            'backend': 'django.contrib.auth.backends.ModelBackend',
        })
        self.assertIn('been logged out', response.content)

    def test_logged_admin_no_redirect(self):
        set_maintenance_mode(True, 'test message')
        self.client.login(username='test_admin')
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)

    def test_maintenance_off(self):
        set_maintenance_mode(False)
        response = self.client.get(reverse('maintenance'))
        self.assertRedirects(response, '/')

    def test_su_no_redirect(self):
        set_maintenance_mode(True, 'test message')
        self.client.login(username='test_admin')
        self.client.post(reverse('su'), {
            'user': 'test_user',
            'backend': 'django.contrib.auth.backends.ModelBackend',
        })
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)

    def test_admin_change_message(self):
        set_maintenance_mode(False)
        self.client.login(username='test_admin')
        self.client.post(reverse('set_maintenance_mode'), {
            'message': 'new test message',
            'set_button': 1,
        })
        info = get_maintenance_mode()
        self.assertEquals('new test message', info['message'])
        self.assertEquals(True, info['state'])
        self.client.post(reverse('set_maintenance_mode'), {
            'turn_off_button': 1,
        })
        info = get_maintenance_mode()
        self.assertEquals(False, info['state'])
