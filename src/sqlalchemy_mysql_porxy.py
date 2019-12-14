
# MySQL主从配置，SQLAlchemy实现读写分离。
# 
# 配置如下：
#
# 主数据库：
# SQLALCHEMY_DATABASE_URI = 'mysql+cymysql://***:***@host:3306/db'
# 从数据库
# SQLALCHEMY_BINDS = {
#     'slave1': 'mysql+cymysql://***:***@host:3306/db'
#     'slave2': 'mysql+cymysql://***:***@host:3306/db'
# }

from random import choice

from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, \
    SignallingSession as _SignallingSession, SessionBase, get_state, orm


class SignallingSession(_SignallingSession):
    def get_bind(self, mapper=None, clause=None):
        # MySQL-Proxy
        if self.app.config.get('MYSQL_PROXY'):
            try:
                state = get_state(self.app)
            except (AssertionError, AttributeError, TypeError) as err:
                return SessionBase.get_bind(self, mapper, clause)
                # 如果没有设置SQLALCHEMY_BINDS，则默认使用SQLALCHEMY_DATABASE_URI
            if state is None or not self.app.config['SQLALCHEMY_BINDS'] or self._flushing:
                return SessionBase.get_bind(self, mapper, clause)
            else:
                slaves = list(self.app.config['SQLALCHEMY_BINDS'].keys())
                return state.db.get_engine(self.app, bind=choice(slaves))
        else:
            super(SignallingSession, self).get_bind(mapper, clause)


class SQLAlchemy(_SQLAlchemy):
    def create_session(self, options):
        return orm.sessionmaker(class_=SignallingSession, db=self, **options)




