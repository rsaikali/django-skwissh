# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GraphType'
        db.create_table('skwissh_graphtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('options', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 9, 9, 0, 0), auto_now_add=True, null=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 9, 9, 0, 0), auto_now=True, null=True, blank=True)),
        ))
        db.send_create_signal('skwissh', ['GraphType'])

        # Adding model 'Probe'
        db.create_table('skwissh_probe', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('addon_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('ssh_command', self.gf('django.db.models.fields.TextField')()),
            ('use_sudo', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('python_parse', self.gf('django.db.models.fields.TextField')(default='output = output', null=True, blank=True)),
            ('graph_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['skwissh.GraphType'])),
            ('probe_unit', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('probe_labels', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 9, 9, 0, 0), auto_now_add=True, null=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 9, 9, 0, 0), auto_now=True, null=True, blank=True)),
        ))
        db.send_create_signal('skwissh', ['Probe'])

        # Adding model 'Server'
        db.create_table('skwissh_server', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hostname', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ip', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('state', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_measuring', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('username', self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True)),
            ('password', self.gf('skwissh.fields.EncryptedCharField')(default='', max_length=50, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 9, 9, 0, 0), auto_now_add=True, null=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 9, 9, 0, 0), auto_now=True, null=True, blank=True)),
        ))
        db.send_create_signal('skwissh', ['Server'])

        # Adding M2M table for field probes on 'Server'
        db.create_table('skwissh_server_probes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('server', models.ForeignKey(orm['skwissh.server'], null=False)),
            ('probe', models.ForeignKey(orm['skwissh.probe'], null=False))
        ))
        db.create_unique('skwissh_server_probes', ['server_id', 'probe_id'])

        # Adding model 'ServerGroup'
        db.create_table('skwissh_servergroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 9, 9, 0, 0), auto_now_add=True, null=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 9, 9, 0, 0), auto_now=True, null=True, blank=True)),
        ))
        db.send_create_signal('skwissh', ['ServerGroup'])

        # Adding M2M table for field servers on 'ServerGroup'
        db.create_table('skwissh_servergroup_servers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('servergroup', models.ForeignKey(orm['skwissh.servergroup'], null=False)),
            ('server', models.ForeignKey(orm['skwissh.server'], null=False))
        ))
        db.create_unique('skwissh_servergroup_servers', ['servergroup_id', 'server_id'])

        # Adding model 'Measure'
        db.create_table('skwissh_measure', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['skwissh.Server'])),
            ('probe', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['skwissh.Probe'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=4096)),
        ))
        db.send_create_signal('skwissh', ['Measure'])

        # Adding model 'MeasureDay'
        db.create_table('skwissh_measureday', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['skwissh.Server'])),
            ('probe', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['skwissh.Probe'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=4096)),
        ))
        db.send_create_signal('skwissh', ['MeasureDay'])

        # Adding model 'MeasureWeek'
        db.create_table('skwissh_measureweek', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['skwissh.Server'])),
            ('probe', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['skwissh.Probe'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=4096)),
        ))
        db.send_create_signal('skwissh', ['MeasureWeek'])

        # Adding model 'MeasureMonth'
        db.create_table('skwissh_measuremonth', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['skwissh.Server'])),
            ('probe', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['skwissh.Probe'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=4096)),
        ))
        db.send_create_signal('skwissh', ['MeasureMonth'])

        # Adding model 'CronLog'
        db.create_table('skwissh_cronlog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('action', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['skwissh.Server'], null=True)),
            ('success', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('message', self.gf('django.db.models.fields.TextField')(default='', null=True)),
            ('duration', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal('skwissh', ['CronLog'])


    def backwards(self, orm):
        # Deleting model 'GraphType'
        db.delete_table('skwissh_graphtype')

        # Deleting model 'Probe'
        db.delete_table('skwissh_probe')

        # Deleting model 'Server'
        db.delete_table('skwissh_server')

        # Removing M2M table for field probes on 'Server'
        db.delete_table('skwissh_server_probes')

        # Deleting model 'ServerGroup'
        db.delete_table('skwissh_servergroup')

        # Removing M2M table for field servers on 'ServerGroup'
        db.delete_table('skwissh_servergroup_servers')

        # Deleting model 'Measure'
        db.delete_table('skwissh_measure')

        # Deleting model 'MeasureDay'
        db.delete_table('skwissh_measureday')

        # Deleting model 'MeasureWeek'
        db.delete_table('skwissh_measureweek')

        # Deleting model 'MeasureMonth'
        db.delete_table('skwissh_measuremonth')

        # Deleting model 'CronLog'
        db.delete_table('skwissh_cronlog')


    models = {
        'skwissh.cronlog': {
            'Meta': {'ordering': "['-timestamp', '-server', '-action']", 'object_name': 'CronLog'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'duration': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['skwissh.Server']", 'null': 'True'}),
            'success': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'skwissh.graphtype': {
            'Meta': {'ordering': "['name']", 'object_name': 'GraphType'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 9, 9, 0, 0)', 'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 9, 9, 0, 0)', 'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'options': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'skwissh.measure': {
            'Meta': {'ordering': "['-timestamp', 'server', 'probe']", 'object_name': 'Measure'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'probe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['skwissh.Probe']"}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['skwissh.Server']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '4096'})
        },
        'skwissh.measureday': {
            'Meta': {'ordering': "['-timestamp', 'server', 'probe']", 'object_name': 'MeasureDay'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'probe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['skwissh.Probe']"}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['skwissh.Server']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '4096'})
        },
        'skwissh.measuremonth': {
            'Meta': {'ordering': "['-timestamp', 'server', 'probe']", 'object_name': 'MeasureMonth'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'probe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['skwissh.Probe']"}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['skwissh.Server']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '4096'})
        },
        'skwissh.measureweek': {
            'Meta': {'ordering': "['-timestamp', 'server', 'probe']", 'object_name': 'MeasureWeek'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'probe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['skwissh.Probe']"}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['skwissh.Server']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '4096'})
        },
        'skwissh.probe': {
            'Meta': {'ordering': "['display_name', 'addon_name']", 'object_name': 'Probe'},
            'addon_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 9, 9, 0, 0)', 'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 9, 9, 0, 0)', 'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'graph_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['skwissh.GraphType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'probe_labels': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'probe_unit': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'python_parse': ('django.db.models.fields.TextField', [], {'default': "'output = output'", 'null': 'True', 'blank': 'True'}),
            'ssh_command': ('django.db.models.fields.TextField', [], {}),
            'use_sudo': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'skwissh.server': {
            'Meta': {'ordering': "['hostname', 'ip']", 'object_name': 'Server'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 9, 9, 0, 0)', 'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 9, 9, 0, 0)', 'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'is_measuring': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'password': ('skwissh.fields.EncryptedCharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'probes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['skwissh.Probe']", 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'username': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'})
        },
        'skwissh.servergroup': {
            'Meta': {'ordering': "['name']", 'object_name': 'ServerGroup'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 9, 9, 0, 0)', 'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 9, 9, 0, 0)', 'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'servers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['skwissh.Server']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['skwissh']