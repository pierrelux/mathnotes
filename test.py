from initdb import Tag,Note
import initdb

session = initdb.Session()

note = Note(title = "t1", text = "text 1111", tags = [Tag(name = "java")])
session.add(note)

t = session.query(Tag).filter(Tag.name == 'java').first()
if t == None:
	t = Tag(name = "java")
	
note2 = Note(title = "t2", text = "text 2222", tags = [t])
session.add(note2)

session.commit()