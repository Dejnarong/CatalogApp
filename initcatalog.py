from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Categories, Base, CategoriesItem, User

engine = create_engine('sqlite:///catalogitems.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

User1 = User(name="Killumi Zoldick", email="killumi@gmail.com",
             picture='')
session.add(User1)
session.commit()


category1 = Categories(id=1, name="Adidas")

session.add(category1)
session.commit()

categoryitem1 = CategoriesItem(
        id=1, title="NMD", description="NMD", categories_id=1, user_id=1)

session.add(categoryitem1)
session.commit()

categoryitem2 = CategoriesItem(
        id=2, title="Yeezy 350 V2", description="Yeezy by Kanye West",
        categories_id=1, user_id=1)

session.add(categoryitem2)
session.commit()

categoryitem3 = CategoriesItem(
        id=3, title="Yeezy 500", description="Yeezy by Kanye West",
        categories_id=1, user_id=1)

session.add(categoryitem3)
session.commit()

category2 = Categories(id=2, name="Nike")

session.add(category2)
session.commit()

category3 = Categories(id=3, name="Bape")

session.add(category3)
session.commit()

category4 = Categories(id=4, name="OFF-WHITE")

session.add(category4)
session.commit()

category5 = Categories(id=5, name="Supreme")

session.add(category5)
session.commit()

category6 = Categories(id=6, name="Anti Social Social Club")

session.add(category6)
session.commit()


print "added categories completed!"
