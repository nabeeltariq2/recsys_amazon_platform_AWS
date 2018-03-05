
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime,Sequence, Numeric, Float
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
import config
from sqlalchemy import text
# import recommender1
# import recommender2
from planout.experiment import SimpleExperiment
from planout.ops.random import *
from sqlalchemy_utils import database_exists, create_database
import datetime
from sqlalchemy.sql import func




engine = create_engine(config.DB_URI, echo=False)
if not database_exists(engine.url):
    create_database(engine.url)
session = scoped_session(sessionmaker(bind=engine,
                                      autocommit = False,
                                      autoflush = False))



Base = declarative_base()
Base.query = session.query_property()


### Class declarations go here
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True)
    first_name = Column(String(64), nullable = True)
    last_name = Column(String(64), nullable = True)
    email = Column(String(64), nullable = True)
    password = Column(String(64), nullable = True)
    age = Column(Integer, nullable = True)
    gender = Column(String(64), nullable = True)
    occupation = Column(String(128), nullable = True)
    city = Column(String(64), nullable = True)
    state = Column(String(64), nullable = True)
    country = Column(String(64), nullable = True)
    zipcode = Column(String(15), nullable = True)
    old_user_id = Column(String(64), nullable = True)
    user_add_time = Column(DateTime, server_default=func.now())

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key = True)
    title = Column(String(256))
    description = Column(String(1280))
    imgurl = Column(String(512))
    old_id = Column(String(64), nullable = True)
    item_time = Column(DateTime, server_default=func.now())



class Rating(Base):
### Association object
    __tablename__= "ratings"

    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('users.id'))
    item_id = Column(Integer, ForeignKey('items.id'))
    rating = Column(Integer,nullable=True)
    rating_time = Column(DateTime, server_default=func.now())

    user = relationship("User", backref=backref("ratings", order_by=id))
    item = relationship("Item", backref=backref("ratings", order_by=id))


# class Recommendations(Base):
# ### Association object
#     __tablename__= "recommendations"
#
#     id = Column(Integer, ForeignKey('users.id'),primary_key = True)
#     pred_1 = Column(String(128), nullable=True)
#     pred_2 = Column(String(128), nullable=True)
#     pred_3 = Column(String(128), nullable=True)
#     pred_4 = Column(String(128), nullable=True)
#     pred_5 = Column(String(128), nullable=True)
#     pred_6 = Column(String(128), nullable=True)
#     pred_7 = Column(String(128), nullable=True)
#     pred_8 = Column(String(128), nullable=True)
#     pred_9 = Column(String(128), nullable=True)
#     pred_10 = Column(String(128), nullable=True)
#
#     user = relationship("User", backref=backref("recommendations", order_by=id))
#


class Recommendations(Base):
### Association object
    __tablename__= "recommendations"

    id = Column(Integer, ForeignKey('users.id'),primary_key = True)
    pred_1 = Column(Integer, nullable=True)
    pred_2 = Column(Integer, nullable=True)
    pred_3 = Column(Integer, nullable=True)
    pred_4 = Column(Integer, nullable=True)
    pred_5 = Column(Integer, nullable=True)
    pred_6 = Column(Integer, nullable=True)
    pred_7 = Column(Integer, nullable=True)
    pred_8 = Column(Integer, nullable=True)
    pred_9 = Column(Integer, nullable=True)
    pred_10= Column(Integer, nullable=True)

    user = relationship("User", backref=backref("recommendations", order_by=id))
    # item = relationship("Item", backref=backref("recommendations", order_by=id))











class Recrating(Base):
### Association object
    __tablename__= "recrating"

    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user_rating_1 = Column(Integer, nullable = True)
    user_rating_2 = Column(Integer, nullable = True)
    user_rating_3 = Column(Integer, nullable = True)
    user_rating_4 = Column(Integer, nullable = True)
    user_rating_5 = Column(Integer, nullable = True)
    user_rating_6 = Column(Integer, nullable = True)
    user_rating_7 = Column(Integer, nullable = True)
    user_rating_8 = Column(Integer, nullable = True)
    user_rating_9 = Column(Integer, nullable = True)
    user_rating_10 = Column(Integer, nullable = True)
    rec_rating_time = Column(DateTime, server_default=func.now())

    user = relationship("User", backref=backref("recrating", order_by=id))



class Feedback(Base):
### Association object
    __tablename__= "feedback"

    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('users.id'))
    novelty = Column(Integer, nullable = True)
    unexpectedness = Column(Integer, nullable = True)
    feedback_time = Column(DateTime, server_default=func.now())

    user = relationship("User", backref=backref("feedback", order_by=id))


class Algo(Base):
    __tablename__ = "algo"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    algorithm = Column(String(128))
    mae = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)
    algo_time = Column(DateTime, server_default=func.now())

    user = relationship("User", backref=backref("algo", order_by=id))


class PredictionLog(Base):
### Association object
    __tablename__= "predictionlogs"

    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('users.id'))
    pred_1 = Column(String(128), nullable=True)
    pred_2 = Column(String(128), nullable=True)
    pred_3 = Column(String(128), nullable=True)
    pred_4 = Column(String(128), nullable=True)
    pred_5 = Column(String(128), nullable=True)
    pred_6 = Column(String(128), nullable=True)
    pred_7 = Column(String(128), nullable=True)
    pred_8 = Column(String(128), nullable=True)
    pred_9 = Column(String(128), nullable=True)
    pred_10 = Column(String(128), nullable=True)
    algorithm = Column(String(64), nullable=True)
    pred_time = Column(DateTime, server_default=func.now())

    user = relationship("User", backref=backref("predictionlogs", order_by=id))


class ShoppingCart(Base):
### Association object
    __tablename__= "shoppingcart"

    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('users.id'))
    item_id = Column(Integer, ForeignKey('items.id'))
    cart_time = Column(DateTime, server_default=func.now())

    user = relationship("User", backref=backref("shoppingcart", order_by=id))
    item = relationship("Item", backref=backref("shoppingcart", order_by=id))


class PageviewLog(Base):
    __tablename__ = "pageview"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable = True)
    item_id = Column(Integer, nullable = True)
    page = Column(String(128), nullable=True)
    activity_type = Column(String(128), nullable=True)
    rating = Column(Integer, nullable=True)

    activity_time = Column(DateTime, server_default=func.now())


### End class declarations
#start function declarations


def add_pageview(user_id, item_id, page, activity_type,rating):
    page_activity = PageviewLog(user_id=user_id,item_id=item_id, page=page, activity_type=activity_type,rating=rating)
    session.add(page_activity)
    session.commit()


def add_algo(user_id, algorithm, mae, rmse):
    new_algo_usage = Algo(user_id=user_id, algorithm=algorithm, mae=mae, rmse=rmse)
    session.add(new_algo_usage)
    session.commit()

def get_user_from_email(email):
    user = User.query.filter_by(email=email).first()
    return user

def get_user_from_id(id):
    user = User.query.filter_by(id=id).first()
    return user

def get_item_from_id(id):
    item = Item.query.filter_by(id=id).first()
    return item

def create_user(first_name, last_name, email, password, age, gender, occupation, city, state, country, zipcode):
    user = User(first_name=first_name, last_name=last_name, email=email, password=password, age=age, occupation=occupation, city=city, state=state, country=country, gender=gender, zipcode=zipcode)
    session.add(user)
    session.commit()
    added_user = User.query.filter_by(first_name=first_name, last_name=last_name, email=email, password=password, age=age, occupation=occupation, city=city, state=state, country=country, gender=gender, zipcode=zipcode).first()
    new_user_id = added_user.id
    session.execute("INSERT INTO ratings SELECT null as id,u.id as user_id, i.id as item_id, null as rating, NOW() as user_add_time FROM items as i CROSS JOIN users as u WHERE u.id = {user}".format(user = new_user_id))
    session.commit()

def show_item_details(id):
    item = Rating.query.filter_by(item_id=id).all()
    return item

def add_rating(item_id, user_id, rating):
    rating = Rating(item_id=item_id, user_id=user_id, rating=rating)
    session.add(rating)
    session.commit()

def is_rating(user_id, item_id):
    rating = Rating.query.filter_by(user_id=user_id, item_id=item_id).first()
    return rating

def update_rating(user_id, item_id, new_rating):
    old_rating = Rating.query.filter_by(user_id=user_id, item_id=item_id).first()
    old_rating.rating = new_rating
    session.commit()

def add_new_item(user_id, item_id, rating):
    new_rating = Rating(user_id=user_id, item_id=item_id, rating=rating)
    session.add(new_rating)
    session.commit()

def delete_recommendations():
    session.execute("DELETE FROM recommendations")
    session.commit()

# def calculate_recommendations_rec_1():
    # compute_recommendations1()
    # session.commit()

# def calculate_recommendations_rec_2():
    # compute_recommendations2()
    # session.commit()

def show_recommendations(id):
    rec = Recommendations.query.filter_by(id=id).first()
    pred_1=Item.query.filter_by(id=rec.pred_1).first()
    pred_2=Item.query.filter_by(id=rec.pred_2).first()
    pred_3=Item.query.filter_by(id=rec.pred_3).first()
    pred_4=Item.query.filter_by(id=rec.pred_4).first()
    pred_5=Item.query.filter_by(id=rec.pred_5).first()
    pred_6=Item.query.filter_by(id=rec.pred_6).first()
    pred_7=Item.query.filter_by(id=rec.pred_7).first()
    pred_8=Item.query.filter_by(id=rec.pred_8).first()
    pred_9=Item.query.filter_by(id=rec.pred_9).first()
    pred_10=Item.query.filter_by(id=rec.pred_10).first()
    return rec, pred_1, pred_2, pred_3, pred_4, pred_5, pred_6,pred_7, pred_8, pred_9,pred_10





def add_rec_rating(user_id,user_rating_1,user_rating_2,user_rating_3,user_rating_4,user_rating_5,user_rating_6,user_rating_7,user_rating_8,user_rating_9,user_rating_10):
    rec_rating = Recrating(user_id=user_id,user_rating_1=user_rating_1,user_rating_2=user_rating_2,user_rating_3=user_rating_3,user_rating_4=user_rating_4,user_rating_5=user_rating_5,user_rating_6=user_rating_6,user_rating_7=user_rating_7,user_rating_8=user_rating_8,user_rating_9=user_rating_9,user_rating_10=user_rating_10)
    session.add(rec_rating)
    session.commit()

def add_feedback(user_id,novelty,unexpectedness):
    new_feedback = Feedback(user_id=user_id,novelty=novelty, unexpectedness=unexpectedness)
    session.add(new_feedback)
    session.commit()

def add_cart(user_id, item_id):
    cart = ShoppingCart(user_id=user_id, item_id=item_id)
    session.add(cart)
    session.commit()


def delete_cart(user_id, item_id):
    del_cart = ShoppingCart(user_id=user_id, item_id=item_id)
    session.expunge(del_cart)
    session.commit()


# def view_cart(user_id, item_id):
#     viewer = ShoppingCart.query.filter_by(user_id=user_id, item_id=item_id).first()
#     return viewer

def view_shoppingcart(id):
    cart = ShoppingCart.query.filter_by(id=id).first()
    # cart = ShoppingCart.query.filter_by(id=id).first()
    return cart



# only to create Database
def create_tables():
    Base.metadata.create_all(engine)

def main():
    create_tables()

if __name__ == "__main__":
    main()
