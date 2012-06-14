# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'StreamNumberType'
        db.create_table('main_streamnumbertype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('field_count', self.gf('django.db.models.fields.IntegerField')()),
            ('start_interval', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Interval'])),
        ))
        db.send_create_signal('main', ['StreamNumberType'])


        # Changing field 'Interval.date'
        db.alter_column('main_interval', 'date', self.gf('django.db.models.fields.DateTimeField')())

    def backwards(self, orm):
        # Deleting model 'StreamNumberType'
        db.delete_table('main_streamnumbertype')


        # Changing field 'Interval.date'
        db.alter_column('main_interval', 'date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

    models = {
        'main.interval': {
            'Meta': {'object_name': 'Interval'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'main.stream': {
            'Meta': {'object_name': 'Stream'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'main.streamnumber': {
            'Meta': {'object_name': 'StreamNumber'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interval': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Interval']"}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'stream': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Stream']"}),
            'stream_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.StreamType']"})
        },
        'main.streamnumbertype': {
            'Meta': {'object_name': 'StreamNumberType'},
            'field_count': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'start_interval': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Interval']"})
        },
        'main.streamtype': {
            'Meta': {'object_name': 'StreamType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['main']