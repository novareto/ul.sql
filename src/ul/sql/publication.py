# -*- coding: utf-8 -*-

from cromlech.sqlalchemy import create_and_register_engine, get_session
from sqlalchemy_imageattach.stores.fs import HttpExposedFileSystemStore
from ul.browser.decorators import with_zcml, with_i18n
from ul.browser.publication import Publication
from .decorators import transaction_sql, sql_storage


class SQLPublication(Publication):
    """Publication Mixin
    """

    def setup_database(self, engine):
        raise NotImplementedError

    @classmethod
    @with_zcml('zcml_file')
    @with_i18n('langs', fallback='en')
    def create(cls, gc, session_key='session.key', dsn='sqlite://',
               name=None, base=None, store_root=None, store_prefix=None):

        if name is None:
            name = str(cls.__name__.lower())

        # We register our SQLengine under a given name
        engine = create_and_register_engine(dsn, name)

        # We use a declarative base, if it exists we bind it and create
        if base is not None:
            engine.bind(base)
            metadata = base.metadata
            metadata.create_all(engine.engine, checkfirst=True)

        if store_root is not None:
            fs_store = HttpExposedFileSystemStore(store_root, store_prefix)
            app = cls(session_key, engine, name, fs_store)
            return fs_store.wsgi_middleware(app)
        else:
            fs_store = None
            return cls(session_key, engine, name, fs_store)

    def __init__(self, session_key, engine, name, fs_store=None):
        self.name = name
        self.session_key = session_key
        self.engine = engine
        self.fs_store = fs_store
        self.publish = self.get_publisher()
        self.setup_database(engine)

    def __runner__(self, func):
        @transaction_sql(self.engine)
        @sql_storage(self.fs_store)
        def run(*args):
            return func(*args)
        return run

    def __interact__(self, banner=u'', **namespace):

        @transaction_sql(self.engine)
        @sql_storage(self.fs_store)
        def shell():
            session = get_session(self.name)
            namespace['sql_session'] = session
            return super(SQLPublication, self).__interact__(
                banner=u'', **namespace)

        return shell()

    def __call__(self, environ, start_response):

        @transaction_sql(self.engine)
        @sql_storage(self.fs_store)
        def publish(environ, start_response):
            return super(SQLPublication, self).__call__(
                environ, start_response)

        return publish(environ, start_response)
