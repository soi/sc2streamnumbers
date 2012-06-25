# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'StreamingPlatform.url_format'
        db.delete_column('main_streamingplatform', 'url_format')


    def backwards(self, orm):
        # Adding field 'StreamingPlatform.url_format'
        db.add_column('main_streamingplatform', 'url_format',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255),
                      keep_default=False)


    models = {
        'main.interval': {
            'Meta': {'object_name': 'Interval'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stream_number_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.StreamNumberType']"})
        },
        'main.rating': {
            'Meta': {'object_name': 'Rating'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'main.stream': {
            'Meta': {'object_name': 'Stream'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'rating': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Rating']"}),
            'streaming_platform': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.StreamingPlatform']"}),
            'streaming_platform_ident': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tl_stream_link': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'main.streamingplatform': {
            'Meta': {'object_name': 'StreamingPlatform'},
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