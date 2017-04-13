# -*- coding: utf-8 -*-

from collections import namedtuple
from cromlech.sqlalchemy import create_engine, get_session
from sqlalchemy_imageattach.stores.fs import HttpExposedFileSystemStore
from ul.browser.decorators import with_zcml, with_i18n
from ul.browser.publication import Publication
from .decorators import transaction_sql, sql_storage


class SQLPublication(Publication):
    """Publication Mixin
    """
    check_configuration = None  # None or list of Interface

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
        engine = create_engine(dsn, name)

        # We use a declarative base, if it exists we bind it and create
        if base is not None:
            engine.bind(base)
            metadata = base.metadata
            metadata.create_all(engine.engine, checkfirst=True)

        if store_root is not None:
            fs_store = HttpExposedFileSystemStore(store_root, store_prefix)
        else:
            fs_store = None

        # Configuration object
        factory = namedtuple('Configuration', ('session_key', 'engine', 'name', 'fs_store'))
        configuration = factory(session_key, engine, name, fs_store)
        if cls.check_configuration is not None:
            errors = []
            for iface in cls.check_configuration:
                errors.extends(getValidationErrors(iface, configuration))
            if errors:
                raise RuntimeError('Errors occured: %s' % ', '.join(errors))

        app = cls(configuration)

        if store_root is not None:
            return fs_store.wsgi_middleware(app)
        return app

    def __init__(self, configuration):
        self.publish = self.get_publisher()
        self.configuration = configuration

    def __runner__(self, func):
        @transaction_sql(self.configuration.engine)
        @sql_storage(self.configuration.fs_store)
        def run(*args):
            return func(*args)
        return run

    def __interact__(self, banner=u'', **namespace):

        @transaction_sql(self.configuration.engine)
        @sql_storage(self.configuration.fs_store)
        def shell():
            session = get_session(self.configuration.name)
            namespace['sql_session'] = session
            return super(SQLPublication, self).__interact__(
                banner=u'', **namespace)

        return shell()

    def __call__(self, environ, start_response):

        @transaction_sql(self.configuration.engine)
        @sql_storage(self.configuration.fs_store)
        def publish(environ, start_response):
            return super(SQLPublication, self).__call__(
                environ, start_response)

        return publish(environ, start_response)
