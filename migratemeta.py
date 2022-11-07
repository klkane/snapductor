from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Comments(Base):
    __tablename__ = "comments"
    username = Column(String)
    comment_id = Column( Integer, primary_key=True, autoincrement=True )
    migrate_request_id = Column( Integer, ForeignKey( "migrate_request.request_id" ) )
    comment_dt = Column( DateTime, default=datetime.datetime.utcnow)
    comment = Column(String)

class MigrateRequest(Base):
    __tablename__ = "migrate_request"
    username = Column(String) 
    request_id = Column( Integer, primary_key=True, autoincrement=True )
    objects = Column(String)
    comments = relationship( "Comments", backref=backref("migrate_request"))
    
