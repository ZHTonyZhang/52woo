#coding=utf-8
'''
Created on 2013-4-4

@author: fengclient
'''
import time
from gluon.dal import DAL, Field

db = DAL('mysql://test:123456@localhost/wantu', pool_size=10, db_codec='latin1')#, migrate=False, migrate_enabled=False)

db.define_table('urlresource',
    Field('id', 'id'),
    Field('url', 'string'),
    Field('pagetype', 'integer'),
    Field('referrerurl', 'string'),
    Field('description', 'string'),
    Field('savedpath', 'string'),
    Field('createtime', 'integer'),
    Field('lastmodtime', 'integer'),
    Field('isfinished', 'integer', default=0),
    Field('ispublished', 'integer', default=0))#,
    #migrate=False)

db.executesql("set autocommit=True")

def refresh_context(db):
    '''
    change isolation mode to load recent changes
    '''
    #end current active transaction
    #db.executesql("commit")
    #change isolation mode to read-committed
    #db.executesql("set @@tx_isolation='read-uncommitted'")
    pass
    
def save_url(url, **fields):
    db.executesql("set autocommit=True")
    row = db(db.urlresource.url == url).select().first()
    fields.pop('createtime', None)
    fields.pop('lastmodtime', None)
    fields.pop('ispublished', None)
    now = int(time.time())
    for k in fields.keys():
        if isinstance(fields[k], unicode):
            fields[k] = fields[k].encode('utf8')
    if row:
        if row.isfinished == 1:
            fields.pop('isfinished', None) # never roll back to init status
        row.update_record(lastmodtime=now, **fields)
        row_id = row.id
    else:
        row_id = db.urlresource.insert(url=url, createtime=now, lastmodtime=now, **fields)
    refresh_context(db)
    return row_id

def is_processed(url):
    db.executesql("set autocommit=True")
    return True if db((db.urlresource.url == url) & (db.urlresource.isfinished == 1)).select() else False

def get_available_rows(count):
    db.executesql("set autocommit=True")
    rows = db((db.urlresource.pagetype == PageType.PicturePage) & 
              (db.urlresource.isfinished == 1) & 
              (db.urlresource.ispublished == 0)).select(limitby=(0, count))
    return rows
    
def get_unfinished_rows(count):
    db.executesql("set autocommit=True")
    rows = db((db.urlresource.isfinished == 0) & 
              (db.urlresource.ispublished == 0)).select(limitby=(0, count))
    return rows

def set_published(url):
    db.executesql("set autocommit=True")
    row = db((db.urlresource.url == url) & (db.urlresource.isfinished == 1)).select().first()
    row.update_record(lastmodtime=int(time.time()), ispublished=1)
    refresh_context(db)

class PageType(object):
    AlbumIndex = 0
    AlbumPage = 1
    DetailPage = 2
    PicturePage = 3
