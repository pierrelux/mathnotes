import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship,sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.sql.expression import func, desc
import settings

engine = sa.engine_from_config(settings.dbconfig, prefix = "")
Base = declarative_base()

engine = sa.engine_from_config(settings.dbconfig, prefix = "")
Session = sessionmaker(bind=engine)
session = Session()
class Tag(Base):
	__tablename__ = 'Tag'
	
	id = Column(Integer, primary_key=True)
	name = Column(String, unique=True)
	
	def __repr__(self):
		return self.name
		
class Note(Base):
	__tablename__ = 'Note'
	
	id = Column(Integer, primary_key=True)
	title = Column(String, nullable = False)
	text = Column(String, nullable = False)
	dtime = Column(DateTime(), nullable = False, server_default=func.now())
	
	tags = relationship("Tag", secondary="Note_Tag", backref="notes")
	citations = relationship("Citation", secondary="Note_Citation", backref="notes")
	
	def __init__(self, title, text, tagnames):
		self.title = title
		self.text = text
		self.tags = []
		
		for tagname in tagnames:
			tag = session.query(Tag).filter(Tag.name == tagname).first()
			if tag == None:
				tag = Tag(name = tagname)
			self.tags.append(tag)
		
	def __repr__(self):
		return self.title + '\n' +self.text

Note_Tag = Table('Note_Tag', Base.metadata,
    Column('note_id', Integer, ForeignKey('Note.id', onupdate="CASCADE", ondelete="CASCADE"), 
					primary_key = True),
    Column('tag_id', Integer, ForeignKey('Tag.id', onupdate="CASCADE", ondelete="CASCADE"), 
					primary_key = True)
)

class Citation(Base):
	__tablename__ = 'Citation'
	
	id = Column(Integer, primary_key=True)
	bibtex = Column(String, nullable = False)
	
	def __repr__(self):
		return self.bibtex
		
Note_Citation = Table('Note_Citation', Base.metadata,	
	Column("note_id", Integer, ForeignKey('Note.id', onupdate="CASCADE", ondelete="CASCADE"), 
					primary_key = True, nullable = False),
	Column("citation_id", Integer, ForeignKey('Citation.id', onupdate="CASCADE", ondelete="CASCADE"), 
					primary_key = True, nullable = False)
)

def getAll():
	return session.query(Note).order_by(desc(Note.id))
	
def save_db(dbinstance):
	session.add(dbinstance)
	session.commit();
	
def init_db():
	Base.metadata.create_all(engine)
	
if __name__ == '__main__':
    if '-i' in sys.argv:
        init_db()