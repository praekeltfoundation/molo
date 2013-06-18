# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'App1Model'
        db.create_table(u'app1_app1model', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'app1', ['App1Model'])


    def backwards(self, orm):
        # Deleting model 'App1Model'
        db.delete_table(u'app1_app1model')


    models = {
        u'app1.app1model': {
            'Meta': {'object_name': 'App1Model'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['app1']