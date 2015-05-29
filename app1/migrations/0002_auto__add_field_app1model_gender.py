# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'App1Model.gender'
        db.add_column(u'app1_app1model', 'gender',
                      self.gf('django.db.models.fields.CharField')(default='unknown', max_length=255),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'App1Model.gender'
        db.delete_column(u'app1_app1model', 'gender')


    models = {
        u'app1.app1model': {
            'Meta': {'object_name': 'App1Model'},
            'gender': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['app1']