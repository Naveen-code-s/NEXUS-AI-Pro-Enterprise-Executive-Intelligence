from datetime import datetime
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from sqlalchemy import String,Integer,Text,DateTime
class Base(DeclarativeBase): pass
class Document(Base):
    __tablename__="documents"; id:Mapped[str]=mapped_column(String(64),primary_key=True); filename:Mapped[str]=mapped_column(String(255)); document_type:Mapped[str]=mapped_column(String(20)); source:Mapped[str]=mapped_column(String(100)); page_count:Mapped[int]=mapped_column(Integer,default=0); chunk_count:Mapped[int]=mapped_column(Integer,default=0); checksum:Mapped[str]=mapped_column(String(64),index=True); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class SearchRecord(Base):
    __tablename__="search_records"; id:Mapped[int]=mapped_column(Integer,primary_key=True); query:Mapped[str]=mapped_column(Text); result_count:Mapped[int]=mapped_column(Integer,default=0); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class Dataset(Base):
    __tablename__="datasets"; id:Mapped[str]=mapped_column(String(64),primary_key=True); filename:Mapped[str]=mapped_column(String(255)); rows:Mapped[int]=mapped_column(Integer); columns:Mapped[int]=mapped_column(Integer); path:Mapped[str|None]=mapped_column(Text,nullable=True); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class Report(Base):
    __tablename__="reports"; id:Mapped[str]=mapped_column(String(64),primary_key=True); title:Mapped[str]=mapped_column(String(500)); format:Mapped[str]=mapped_column(String(20)); path:Mapped[str]=mapped_column(Text); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
