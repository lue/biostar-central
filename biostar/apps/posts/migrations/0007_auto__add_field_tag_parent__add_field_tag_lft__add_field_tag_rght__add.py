# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Tag.parent'
        db.add_column(u'posts_tag', 'parent',
                      self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name=u'children', null=True, to=orm['posts.Tag']),
                      keep_default=False)

        # Adding field 'Tag.lft'
        db.add_column(u'posts_tag', u'lft',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=1, db_index=True),
                      keep_default=False)

        # Adding field 'Tag.rght'
        db.add_column(u'posts_tag', u'rght',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=1, db_index=True),
                      keep_default=False)

        # Adding field 'Tag.tree_id'
        db.add_column(u'posts_tag', u'tree_id',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=1, db_index=True),
                      keep_default=False)

        # Adding field 'Tag.level'
        db.add_column(u'posts_tag', u'level',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=1, db_index=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Tag.parent'
        db.delete_column(u'posts_tag', 'parent_id')

        # Deleting field 'Tag.lft'
        db.delete_column(u'posts_tag', u'lft')

        # Deleting field 'Tag.rght'
        db.delete_column(u'posts_tag', u'rght')

        # Deleting field 'Tag.tree_id'
        db.delete_column(u'posts_tag', u'tree_id')

        # Deleting field 'Tag.level'
        db.delete_column(u'posts_tag', u'level')


    models = {
        u'posts.emailentry': {
            'Meta': {'object_name': 'EmailEntry'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['posts.Post']", 'null': 'True'}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {'default': "u''"})
        },
        u'posts.emailsub': {
            'Meta': {'object_name': 'EmailSub'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {})
        },
        u'posts.post': {
            'Meta': {'object_name': 'Post'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']"}),
            'book_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'changed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'comment_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'has_accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'html': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastedit_date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'lastedit_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'editor'", 'to': u"orm['users.User']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'children'", 'null': 'True', 'to': u"orm['posts.Post']"}),
            'rank': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'related': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'similar'", 'to': u"orm['posts.Post']", 'through': u"orm['posts.RelatedPosts']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'reply_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'descendants'", 'null': 'True', 'to': u"orm['posts.Post']"}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sites.Site']", 'null': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'sticky': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'subs_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tag_set': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['posts.Tag']", 'symmetrical': 'False', 'blank': 'True'}),
            'tag_val': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '100', 'blank': 'True'}),
            'thread_score': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'type': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'view_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'vote_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True', 'blank': 'True'})
        },
        u'posts.postview': {
            'Meta': {'object_name': 'PostView'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.GenericIPAddressField', [], {'default': "u''", 'max_length': '39', 'null': 'True', 'blank': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'post_views'", 'to': u"orm['posts.Post']"})
        },
        u'posts.relatedposts': {
            'Meta': {'unique_together': "((u'post', u'similar_post'),)", 'object_name': 'RelatedPosts'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'related_post'", 'to': u"orm['posts.Post']"}),
            'similar_post': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'similar_post'", 'to': u"orm['posts.Post']"}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        u'posts.replytoken': {
            'Meta': {'object_name': 'ReplyToken'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['posts.Post']"}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']"})
        },
        u'posts.subscription': {
            'Meta': {'unique_together': "((u'user', u'post'),)", 'object_name': 'Subscription'},
            'date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'subs'", 'to': u"orm['posts.Post']"}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']"})
        },
        u'posts.tag': {
            'Meta': {'object_name': 'Tag'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'max_length': '50', 'db_index': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'children'", 'null': 'True', 'to': u"orm['posts.Tag']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'posts.vote': {
            'Meta': {'object_name': 'Vote'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'votes'", 'to': u"orm['posts.Post']"}),
            'type': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'})
        },
        u'sites.site': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'users.user': {
            'Meta': {'object_name': 'User'},
            'activity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'badges': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'flair': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '15'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255'}),
            'new_messages': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sites.Site']", 'null': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['posts']