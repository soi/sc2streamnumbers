# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'StreamingPlatform'
        db.create_table('main_streamingplatform', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('main', ['StreamingPlatform'])

        # Adding model 'Rating'
        db.create_table('main_rating', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('main', ['Rating'])

        # Adding field 'StreamNumber.streaming_platform_ident'
        db.add_column('main_streamnumber', 'streaming_platform_ident',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255),
                      keep_default=False)

        # Adding field 'StreamNumber.tl_stream_link'
        db.add_column('main_streamnumber', 'tl_stream_link',
                      self.gf('django.db.models.fields.CharField')(default='http://www.teamliquid.net', max_length=255),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'StreamingPlatform'
        db.delete_table('main_streamingplatform')

        # Deleting model 'Rating'
        db.delete_table('main_rating')

        # Deleting field 'StreamNumber.streaming_platform_ident'
        db.delete_column('main_streamnumber', 'streaming_platform_ident')

        # Deleting field 'StreamNumber.tl_stream_link'
        db.delete_column('main_streamnumber', 'tl_stream_link')


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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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
            'stream_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.StreamType']"}),
            'streaming_platform_ident': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tl_stream_link': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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