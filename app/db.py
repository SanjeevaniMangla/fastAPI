# app/db.py

# import databases
# import ormar
# import sqlalchemy

# from .config import settings

# database = databases.Database(settings.db_url)
# metadata = sqlalchemy.MetaData()


# class BaseMeta(ormar.ModelMeta):
#     metadata = metadata
#     database = database


# class User(ormar.Model):
#     class Meta(BaseMeta):
#         tablename = "users"

#     id: int = ormar.Integer(primary_key=True)
#     email: str = ormar.String(max_length=128, unique=True, nullable=False)
#     active: bool = ormar.Boolean(default=True, nullable=False)


# engine = sqlalchemy.create_engine(settings.db_url)
# metadata.create_all(engine)

import sqlalchemy as _sql
import sqlalchemy.ext.declarative as _declarative
import sqlalchemy.orm as _orm
 
DATABASE_URL = "sqlite:///./database.db"
 
engine = _sql.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
 
SessionLocal = _orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
 
Base = _declarative.declarative_base()