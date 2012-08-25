# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core import management
from django.core.serializers import json
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test.testcases import TestCase
from skwissh.models import Probe, GraphType, Server, Measure


class SkwisshTest(TestCase):

    def setUp(self):
        self.test_server = Server.objects.get(hostname="localhost")
        self.client = Client()
        self.user_password = "unittest_password"
        try:
            self.user = User.objects.get(username='unittest_user')
        except:
            self.user = User.objects.create_user('unittest_user', 'unittest_user@test.com', self.user_password)

    def test_0001_countSensors(self):
        self.assertTrue(len(Probe.objects.all()) > 0, "No default sensors loaded. Check fictures.")

    def test_0002_countGraphTypes(self):
        self.assertTrue(len(GraphType.objects.all()) > 0, "No default chart types loaded. Check fixtures.")

    def test_0003_getMeasures(self):
        management.call_command('runtask', 'getMeasures')
        self.assertTrue(len(Probe.objects.all()) == len(Measure.objects.all()), "Waiting %d measures, got only %d." % (len(Probe.objects.all()), len(Measure.objects.all())))

    def test_0004_indexAnonymous(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 302, "Base URL by anonymous user should return a HTTP 302 (redirect).")
        self.assertTrue(response['Location'].find("login") != -1, "Base URL by anonymous user should redirect to login URL.")

    def test_0005_indexRegisteredUser(self):
        self.client.login(username=self.user.username, password=self.user_password)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 302, "Base URL by registered user should return a HTTP 302 (redirect).")
        self.assertTrue(response['Location'].find("server-list") != -1, "Base URL by registered user should redirect to servers list URL.")

    def test_0006_ajaxCallWithoutXHR(self):
        self.client.login(username=self.user.username, password=self.user_password)
        for probe in self.test_server.probes.all():
            response = self.client.get(reverse('mesures', args=(self.test_server.id, probe.id, 'hour')))
            self.assertEqual(response.status_code, 404, "Direct call to Ajax URL should raise a 404.")

    def test_0007_ajaxCallWithXHR(self):
        management.call_command('runtask', 'getMeasures')
        self.client.login(username=self.user.username, password=self.user_password)
        for probe in self.test_server.probes.all():
            response = self.client.get(reverse('mesures', args=(self.test_server.id, probe.id, 'hour')), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(response.status_code, 200, "XHR call to Ajax URL should work.")
            self.assertEqual(len(json.simplejson.loads(response.content)), 1, "Ajax call response length should be 1, got %d instead." % len(json.simplejson.loads(response.content)))

    def test_0008_ajaxCallWithBadParameter(self):
        self.client.login(username=self.user.username, password=self.user_password)
        response = self.client.get('/skwissh/mesures/%s/999/hour/' % self.test_server.id, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404, "XHR call to Ajax URL should work.")

    def test_0009_knownServerDetails(self):
        self.client.login(username=self.user.username, password=self.user_password)
        response = self.client.get("/skwissh/server-detail/%s/" % self.test_server.id)
        self.assertEqual(response.status_code, 200, "Server details should work with an existing server.")

    def test_0010_unknownServerDetails(self):
        self.client.login(username=self.user.username, password=self.user_password)
        response = self.client.get("/skwissh/server-detail/999/")
        self.assertEqual(response.status_code, 404, "Server details shouldn't work with an unexisting server.")
