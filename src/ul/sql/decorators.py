# -*- coding: utf-8 -*-

import transaction
from cromlech.sqlalchemy import SQLAlchemySession


def transaction_sql(engine):
    def sql_wrapped(wrapped):
        def caller(*args):
            with transaction.manager as tm:
                with SQLAlchemySession(engine, transaction_manager=tm):
                    return wrapped(*args)
        return caller
    return sql_wrapped


def sql_storage(fs_store):
    def sql_store(wrapped):
        def caller(*args):
            if fs_store is not None:
                with store.store_context(fs_store):
                    return wrapped(*args)
            return wrapped(*args)
        return caller
    return sql_store
