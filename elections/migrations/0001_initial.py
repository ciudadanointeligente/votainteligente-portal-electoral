# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Election'
        db.create_table(u'elections_election', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=50, populate_from='name', unique_with=())),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('can_election', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['candideitorg.Election'], unique=True, null=True)),
            ('searchable', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('highlighted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('popit_api_instance', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['popit.ApiInstance'], unique=True, null=True)),
            ('writeitinstance', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['writeit.WriteItInstance'], unique=True, null=True)),
            ('extra_info_title', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('extra_info_content', self.gf('django.db.models.fields.TextField')(max_length=3000, null=True, blank=True)),
        ))
        db.send_create_signal(u'elections', ['Election'])

        # Adding model 'CandidatePerson'
        db.create_table(u'elections_candidateperson', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.OneToOneField')(related_name='relation', unique=True, to=orm['popit.Person'])),
            ('candidate', self.gf('django.db.models.fields.related.OneToOneField')(related_name='relation', unique=True, to=orm['candideitorg.Candidate'])),
        ))
        db.send_create_signal(u'elections', ['CandidatePerson'])


    def backwards(self, orm):
        # Deleting model 'Election'
        db.delete_table(u'elections_election')

        # Deleting model 'CandidatePerson'
        db.delete_table(u'elections_candidateperson')


    models = {
        u'candideitorg.answer': {
            'Meta': {'object_name': 'Answer'},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['candideitorg.Question']"}),
            'remote_id': ('django.db.models.fields.IntegerField', [], {}),
            'resource_uri': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'candideitorg.candidate': {
            'Meta': {'object_name': 'Candidate'},
            'answers': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['candideitorg.Answer']", 'symmetrical': 'False'}),
            'election': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['candideitorg.Election']"}),
            'has_answered': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'photo': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'remote_id': ('django.db.models.fields.IntegerField', [], {}),
            'resource_uri': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'})
        },
        u'candideitorg.category': {
            'Meta': {'object_name': 'Category'},
            'election': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['candideitorg.Election']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'remote_id': ('django.db.models.fields.IntegerField', [], {}),
            'resource_uri': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'})
        },
        u'candideitorg.election': {
            'Meta': {'object_name': 'Election'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'information_source': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'logo': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'remote_id': ('django.db.models.fields.IntegerField', [], {}),
            'resource_uri': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'use_default_media_naranja_option': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'candideitorg.question': {
            'Meta': {'object_name': 'Question'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['candideitorg.Category']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'remote_id': ('django.db.models.fields.IntegerField', [], {}),
            'resource_uri': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'elections.candidateperson': {
            'Meta': {'object_name': 'CandidatePerson'},
            'candidate': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'relation'", 'unique': 'True', 'to': u"orm['candideitorg.Candidate']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'relation'", 'unique': 'True', 'to': u"orm['popit.Person']"})
        },
        u'elections.election': {
            'Meta': {'object_name': 'Election'},
            'can_election': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['candideitorg.Election']", 'unique': 'True', 'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'extra_info_content': ('django.db.models.fields.TextField', [], {'max_length': '3000', 'null': 'True', 'blank': 'True'}),
            'extra_info_title': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'highlighted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'popit_api_instance': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['popit.ApiInstance']", 'unique': 'True', 'null': 'True'}),
            'searchable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "'name'", 'unique_with': '()'}),
            'writeitinstance': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['writeit.WriteItInstance']", 'unique': 'True', 'null': 'True'})
        },
        u'popit.apiinstance': {
            'Meta': {'object_name': 'ApiInstance'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('popit.fields.ApiInstanceURLField', [], {'unique': 'True', 'max_length': '200'})
        },
        u'popit.person': {
            'Meta': {'object_name': 'Person'},
            'api_instance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['popit.ApiInstance']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'popit_url': ('popit.fields.PopItURLField', [], {'default': "''", 'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_tagged_items'", 'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_items'", 'to': u"orm['taggit.Tag']"})
        },
        u'writeit.writeitapiinstance': {
            'Meta': {'object_name': 'WriteItApiInstance'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'})
        },
        u'writeit.writeitdocument': {
            'Meta': {'object_name': 'WriteItDocument'},
            'api_instance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['writeit.WriteItApiInstance']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'remote_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'writeit.writeitinstance': {
            'Meta': {'object_name': 'WriteItInstance', '_ormbases': [u'writeit.WriteItDocument']},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'writeitdocument_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['writeit.WriteItDocument']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['elections']