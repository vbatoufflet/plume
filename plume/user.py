# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Vincent Batoufflet.
#
# License: BSD, see LICENSE for more details.
#

import hashlib
import os

from plume import DATA_DIR, PASSWORD_MIN_LENGTH
from plume.exception import PasswordTooShort
from sqlalchemy import *
from sqlalchemy import event
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
Session = sessionmaker()


class User(Base):
    __tablename__ = 'user'

    uid = Column(Integer, nullable=False, primary_key=True)
    login = Column(String(32), nullable=False, unique=True)
    password = Column(String(64))
    fullname = Column(String(128))
    email = Column(String(128))
    locale = Column(String(16))
    timezone = Column(String(32))
    enabled = Column(Boolean, nullable=False, default=True)


class UserBackend:
    def __init__(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        engine = create_engine('sqlite:///' + os.path.join(DATA_DIR, 'users.db'))

        Base.metadata.create_all(engine)
        Session.configure(bind=engine)

        event.listen(engine, 'connect', set_sqlite_pragma)

    def authenticate(self, login, password):
        cursor = Session()

        try:
            user = cursor.query(User).filter(User.login == login,
                User.password == hashlib.sha256(password).hexdigest()).one()

            return user
        except NoResultFound:
            return None
        finally:
            cursor.close()

    def exists(self, login):
        cursor = Session()

        try:
            cursor.query(User.uid).filter(User.login == login).one()
            return True
        except NoResultFound:
            return False
        finally:
            cursor.close()

    def get(self, uid):
        cursor = Session()

        try:
            return cursor.query(User).filter(User.uid == uid).one()
        except NoResultFound:
            return None
        finally:
            cursor.close()

    def list(self):
        result = []
        columns = [x.name for x in User.__table__.columns]

        cursor = Session()

        for user in cursor.query(User).order_by(User.uid):
            result.append(dict((x, getattr(user, x, None)) for x in columns if hasattr(user, x)))

        cursor.close()

        return result

    def set(self, **kwargs):
        cursor = Session()

        if kwargs.get('password'):
            if len(kwargs.get('password')) < PASSWORD_MIN_LENGTH:
                raise PasswordTooShort()

            kwargs['password'] = hashlib.sha256(kwargs.get('password')).hexdigest()

        if kwargs.get('modify'):
            user = cursor.query(User).filter(User.login == kwargs.get('login')).one()
            [setattr(user, x.name, kwargs.get(x.name)) for x in User.__table__.columns if x.name in kwargs]
        else:
            user = User(**kwargs)

        cursor.add(user)
        cursor.commit()

        return user

    def unset(self, login):
        cursor = Session()
        cursor.query(User).filter(User.login == login).delete()
        cursor.commit()

        return True


def set_sqlite_pragma(conn, record):
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()
