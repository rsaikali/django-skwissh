# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core import management
from django.core.serializers import json
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test.testcases import TestCase
from skwissh.models import Probe, GraphType, Server, Measure, MeasureDay, \
    MeasureWeek, MeasureMonth


class SkwisshTest(TestCase):

    def setUp(self):
        self.test_server = Server.objects.get(ip="127.0.0.1")
        self.client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        self.user_password = "unittest_password"
        try:
            self.user = User.objects.get(username='unittest_user')
        except:
            self.user = User.objects.create_user('unittest_user', 'unittest_user@test.com', self.user_password)

    #
    # Count fixtures
    #
    def test_0001_count_fixtures_sensors(self):
        self.assertGreater(Probe.objects.count(), 0, "No default sensors loaded. Check fictures.")

    def test_0002_count_fixtures_graphtypes(self):
        self.assertGreater(GraphType.objects.count(), 0, "No default chart types loaded. Check fixtures.")

    def test_0003_count_fixtures_servers(self):
        self.assertGreater(Server.objects.count(), 0, "No default server loaded. Check fixtures.")

    #
    # Cron Commands
    #
    def test_0100_command_getmeasures(self):
        management.call_command('runtask', 'getMeasures')
        self.assertEqual(Probe.objects.count(), Measure.objects.count(), "Waiting %d measures, got only %d." % (Probe.objects.count(), Measure.objects.count()))

    def test_0101_command_averageday(self):
        management.call_command('runtask', 'averageDay')
        self.assertEqual(MeasureDay.objects.count(), 0, "Waiting 0 daily measures, got %d" % MeasureDay.objects.count())

    def test_0102_command_averageweek(self):
        management.call_command('runtask', 'averageWeek')
        self.assertEqual(MeasureWeek.objects.count(), 0, "Waiting 0 weekly measures, got %d" % MeasureWeek.objects.count())

    def test_0103_command_averagemonth(self):
        management.call_command('runtask', 'averageMonth')
        self.assertEqual(MeasureMonth.objects.count(), 0, "Waiting 0 monthly measures, got %d" % MeasureMonth.objects.count())

    #
    # Security : anonymous user.
    #
    def test_0200_security_index_anonymous(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 302, "Base URL by anonymous user should return a HTTP 302 (redirect).")
        self.assertTrue(response['Location'].find("login") != -1, "Base URL by anonymous user should redirect to login URL.")

    def test_0201_security_serverlist_anonymous(self):
        response = self.client.get(reverse('server-list'))
        self.assertEqual(response.status_code, 302, "Servers list URL by anonymous user should return a HTTP 302 (redirect).")
        self.assertTrue(response['Location'].find("login") != -1, "Servers list URL by anonymous user should redirect to login URL.")

    def test_0202_security_serverdetail_anonymous(self):
        response = self.client.get(reverse('server-detail', args=(self.test_server.id,)))
        self.assertEqual(response.status_code, 302, "Server detail URL by anonymous user should return a HTTP 302 (redirect).")
        self.assertTrue(response['Location'].find("login") != -1, "Server detail URL by anonymous user should redirect to login URL.")

    def test_0203_security_probelist_anonymous(self):
        response = self.client.get(reverse('probe-list'))
        self.assertEqual(response.status_code, 302, "Sensors list URL by anonymous user should return a HTTP 302 (redirect).")
        self.assertTrue(response['Location'].find("login") != -1, "Sensors list URL by anonymous user should redirect to login URL.")

    def test_0204_security_addserver_anonymous(self):
        response = self.client.post(reverse('add-server'))
        self.assertEqual(response.status_code, 302, "POST on add server URL by anonymous user should return a HTTP 302 (redirect).")
        self.assertTrue(response['Location'].find("login") != -1, "POST on add server URL by anonymous user should redirect to login URL.")

    def test_0205_security_addgroup_anonymous(self):
        response = self.client.post(reverse('add-group'))
        self.assertEqual(response.status_code, 302, "POST on add group URL by anonymous user should return a HTTP 302 (redirect).")
        self.assertTrue(response['Location'].find("login") != -1, "POST on add group URL by anonymous user should redirect to login URL.")

    def test_0206_security_addsensor_anonymous(self):
        response = self.client.post(reverse('add-probe'))
        self.assertEqual(response.status_code, 302, "POST on add sensor URL by anonymous user should return a HTTP 302 (redirect).")
        self.assertTrue(response['Location'].find("login") != -1, "POST on add sensor URL by anonymous user should redirect to login URL.")

    def test_0207_security_updateserver_anonymous(self):
        response = self.client.post(reverse('update-server', args=(self.test_server.id,)))
        self.assertEqual(response.status_code, 302, "POST on update server URL by anonymous user should return a HTTP 302 (redirect).")
        self.assertTrue(response['Location'].find("login") != -1, "POST on update server URL by anonymous user should redirect to login URL.")

    def test_0208_security_updategroup_anonymous(self):
        response = self.client.post(reverse('update-group'))
        self.assertEqual(response.status_code, 302, "POST on update group URL by anonymous user should return a HTTP 302 (redirect).")
        self.assertTrue(response['Location'].find("login") != -1, "POST on update group URL by anonymous user should redirect to login URL.")

    def test_0209_security_updatesensor_anonymous(self):
        response = self.client.post(reverse('update-probe'))
        self.assertEqual(response.status_code, 302, "POST on update sensor URL by anonymous user should return a HTTP 302 (redirect).")
        self.assertTrue(response['Location'].find("login") != -1, "POST on update sensor URL by anonymous user should redirect to login URL.")

    def test_0210_security_deleteserver_anonymous(self):
        response = self.client.post(reverse('delete-server', args=(self.test_server.id,)))
        self.assertEqual(response.status_code, 302, "POST on delete server URL by anonymous user should return a HTTP 302 (redirect).")
        self.assertTrue(response['Location'].find("login") != -1, "POST on delete server URL by anonymous user should redirect to login URL.")

    def test_0211_security_deletegroup_anonymous(self):
        response = self.client.post(reverse('delete-group', args=(1,)))
        self.assertEqual(response.status_code, 302, "POST on delete group URL by anonymous user should return a HTTP 302 (redirect).")
        self.assertTrue(response['Location'].find("login") != -1, "POST on delete group URL by anonymous user should redirect to login URL.")

    def test_0212_security_deletesensor_anonymous(self):
        response = self.client.post(reverse('delete-probe', args=(1,)))
        self.assertEqual(response.status_code, 302, "POST on delete sensor URL by anonymous user should return a HTTP 302 (redirect).")
        self.assertTrue(response['Location'].find("login") != -1, "POST on delete sensor URL by anonymous user should redirect to login URL.")

    def test_0213_security_logslist_anonymous(self):
        response = self.client.get(reverse('logs-list'))
        self.assertEqual(response.status_code, 302, "Logs list URL by anonymous user should return a HTTP 302 (redirect).")
        self.assertTrue(response['Location'].find("login") != -1, "Logs list URL by anonymous user should redirect to login URL.")

    #
    # Security : registered user.
    #
    def test_0240_security_login_logout(self):
        self.client.login(username=self.user.username, password=self.user_password)
        self.client.logout()
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 302, "Base URL by registered user should return a HTTP 302 (redirect).")
        self.assertTrue(response['Location'].find("login") != -1, "Base URL by logged in / logged out user should redirect to login URL.")

    def test_0250_security_index_registered(self):
        self.client.login(username=self.user.username, password=self.user_password)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 302, "Base URL by registered user should return a HTTP 302 (redirect).")
        self.assertTrue(response['Location'].find("server-list") != -1, "Base URL by registered user should redirect to servers list URL.")

    def test_0251_security_serverlist_registered(self):
        self.client.login(username=self.user.username, password=self.user_password)
        response = self.client.get(reverse('server-list'))
        self.assertEqual(response.status_code, 200, "Servers list URL by registered user should return a HTTP 200.")

    def test_0252_security_serverdetail_registered(self):
        self.client.login(username=self.user.username, password=self.user_password)
        response = self.client.get(reverse('server-detail', args=(self.test_server.id,)))
        self.assertEqual(response.status_code, 200, "Servers detail URL by registered user should return a HTTP 200.")

    def test_0253_security_serverdetail_registered_unknownid(self):
        self.client.login(username=self.user.username, password=self.user_password)
        response = self.client.get(reverse('server-detail', args=(999,)))
        self.assertEqual(response.status_code, 404, "Servers detail URL by registered user with unknown server ID should return a HTTP 404 (Not Found).")

    def test_0254_security_logslist_registered(self):
        self.client.login(username=self.user.username, password=self.user_password)
        response = self.client.get(reverse('logs-list'))
        self.assertEqual(response.status_code, 200, "Logs list URL by registered user should return a HTTP 200.")

    def test_0280_security_ajax_withoutxhr(self):
        self.client.login(username=self.user.username, password=self.user_password)
        for probe in self.test_server.probes.all():
            response = self.client.get(reverse('mesures', args=(self.test_server.id, probe.id, 'hour')))
            self.assertEqual(response.status_code, 500, "Direct call to Ajax URL should raise a 404.")

    def test_0281_security_ajax_withxhr(self):
        management.call_command('runtask', 'getMeasures')
        self.client.login(username=self.user.username, password=self.user_password)
        for probe in self.test_server.probes.all():
            response = self.client.get(reverse('mesures', args=(self.test_server.id, probe.id, 'hour')), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(response.status_code, 200, "XHR call to Ajax URL should work.")
            self.assertEqual(len(json.simplejson.loads(response.content)), 1, "Ajax call response length should be 1, got %d instead." % len(json.simplejson.loads(response.content)))

    def test_0282_security_ajax_badparameter(self):
        self.client.login(username=self.user.username, password=self.user_password)
        response = self.client.get('/skwissh/mesures/%s/999/hour/' % self.test_server.id, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404, "XHR call to Ajax URL should work.")
