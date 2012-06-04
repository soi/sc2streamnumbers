# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Stream'
        db.create_table('main_stream', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('main', ['Stream'])

        # Adding model 'Interval'
        db.create_table('main_interval', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('main', ['Interval'])

        # Adding model 'StreamNumber'
        db.create_table('main_streamnumber', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('stream', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Stream'])),
            ('interval', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Interval'])),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('main', ['StreamNumber'])


    def backwards(self, orm):
        
        # Deleting model 'Stream'
        db.delete_table('main_stream')

        # Deleting model 'Interval'
        db.delete_table('main_interval')

        # Deleting model 'StreamNumber'
        db.delete_table('main_streamnumber')


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
        }
    }

    complete_apps = ['main']
