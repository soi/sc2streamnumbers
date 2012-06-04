# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'StreamType'
        db.create_table('main_streamtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('main', ['StreamType'])


    def backwards(self, orm):
        
        # Deleting model 'StreamType'
        db.delete_table('main_streamtype')


    models = {
        'main.interval': {
            'Meta': {'object_name': 'Interval'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'main.stream': {
            'Meta': {'object_name': 'Stream'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'main.streamnumber': {
            'Meta': {'object_name': 'StreamNumber'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interval': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Interval']"}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'stream': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Stream']"})
        },
        'main.streamtype': {
            'Meta': {'object_name': 'StreamType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        }
    }

    complete_apps = ['main']
