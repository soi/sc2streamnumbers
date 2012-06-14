# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Interval.stream_number_type'
        db.add_column('main_interval', 'stream_number_type',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['main.StreamNumberType']),
                      keep_default=False)

        # Adding field 'StreamNumber.stream_number_type'
        db.add_column('main_streamnumber', 'stream_number_type',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['main.StreamNumberType']),
                      keep_default=False)

        # Deleting field 'StreamNumberType.field_count'
        db.delete_column('main_streamnumbertype', 'field_count')

        # Adding field 'StreamNumberType.number_count'
        db.add_column('main_streamnumbertype', 'number_count',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Interval.stream_number_type'
        db.delete_column('main_interval', 'stream_number_type_id')

        # Deleting field 'StreamNumber.stream_number_type'
        db.delete_column('main_streamnumber', 'stream_number_type_id')

        # Adding field 'StreamNumberType.field_count'
        db.add_column('main_streamnumbertype', 'field_count',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Deleting field 'StreamNumberType.number_count'
        db.delete_column('main_streamnumbertype', 'number_count')


    models = {
        'main.interval': {
            'Meta': {'object_name': 'Interval'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stream_number_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.StreamNumberType']"})
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
            'stream_number_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.StreamNumberType']"}),
            'stream_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.StreamType']"})
        },
        'main.streamnumbertype': {
            'Meta': {'object_name': 'StreamNumberType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'number_count': ('django.db.models.fields.IntegerField', [], {})
        },
        'main.streamtype': {
            'Meta': {'object_name': 'StreamType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['main']