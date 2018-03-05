
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
import numpy as np
import pandas as pd
import datetime




def auto_truncate_description(val):
    return val[:1024]
def auto_truncate_title(val):
    return val[:255]


df_ratings = pd.read_csv("data/reviews_amazon_musical_instruments_small.csv")

# Sampling
# df_ratings = df_ratings.sample(frac=0.1, replace=True)


# subsetting dataframe
df_ratings = df_ratings[["reviewerID", "asin", "overall", "unixReviewTime"]]
df_ratings.unixReviewTime = pd.to_datetime(df_ratings["unixReviewTime"],unit = 's')

#changing column names
df_ratings = df_ratings.rename(columns={'reviewerID': 'user_id', 'asin': 'item_id', 'overall': 'rating', 'unixReviewTime': 'timestamp'})




item_filter = pd.DataFrame(df_ratings['item_id'])
item_filter = item_filter.groupby('item_id').size()
item_filter = item_filter.to_frame().reset_index()
item_filter.columns.values[1] = 'count'
item_filter = item_filter.sort_values('count', ascending=False)
item_filter = item_filter.head(n=20)
item_filter = item_filter[['item_id']]

df_ratings = pd.merge(left=df_ratings,right=item_filter, left_on='item_id', right_on='item_id')







# creating keys
df_ratings = df_ratings.sort_values("user_id")

# df_ratings["old_user_id"] = df_ratings["user_id"]




df_ratings.user_id = df_ratings.user_id.astype("category")

df_ratings["userid_key"] = df_ratings["user_id"].cat.codes
df_ratings["userid_key"] = df_ratings["userid_key"] + 1





df_items = pd.read_csv("data/items_amazon_musical_instruments.csv", low_memory= False, converters={'description': auto_truncate_description,'title': auto_truncate_title})


# Sampling
# df_items = df_items.sample(frac=0.1, replace=True)




# extracting specific columns
df_items = df_items[["asin", "title", "description", "imUrl"]]
df_items[["old_id"]] = df_items[['asin']]
# renaming columns
df_items = df_items.rename(columns={'asin': 'id', 'title': 'title', 'description': 'description', 'imUrl': 'imgurl'})


df_items = pd.merge(left=df_items,right=item_filter, left_on='id', right_on='item_id')



import config
from sqlalchemy.ext.declarative import declarative_base

# creating keys
df_items = df_items.sort_values("id")




#creating key for items
df_items['item_key'] = range(len(df_items))

#adding 1 to the range
# df_items['item_key'] = df_items['item_key'] + 1


df_items = df_items[["item_key", "title", "description", "imgurl","old_id"]]
df_items = df_items.rename(columns={'item_key': 'id'})
# df_items['id'] = df_items['id'] + 1


df_items = df_items.sort_values("id")

#removing the top row since its not an item
df_items = df_items.iloc[1:]

# df_items.description.st = df_items.description.astype(str).apply(lambda x: x.str[:2000])
# df_items['description'] = df_items['description'].applymap(lambda x: x[:2000])

df_items_key = df_items[["old_id", "id"]]
df_items_key = df_items_key.rename(columns={'id': 'item_key'})


df_ratings_key = df_ratings[["userid_key", "user_id"]]
# df_ratings_key['userid_key'] = df_ratings_key['userid_key'] + 1

# df_ratings['user_id']=df_ratings['user_id']+1
# df_ratings['item_id'] = df_ratings['item_id']+1

# combining columns with rating ids
df_ratings = pd.merge(df_ratings, df_items_key, left_on = "item_id", right_on="old_id")


#rearrange and rename columns
# df_ratings = df_ratings[["userid_key", "item_key", "rating", "user_id"]]
df_ratings = df_ratings[["userid_key", "item_key", "rating", 'timestamp', "user_id"]]
df_ratings = df_ratings.rename(columns={'user_id': 'old_user_id'})


# df_ratings = df_ratings.rename(columns={'userid_key': 'user_id_new', 'item_key': 'item_id'})
df_ratings = df_ratings.rename(columns={'userid_key': 'user_id', 'item_key': 'item_id'})

df_ratings = df_ratings.sort_values("user_id")



df_users = pd.DataFrame()

df_users["id"] = df_ratings.user_id.unique()
df_users = pd.merge(df_users,df_ratings , left_on="id", right_on= "user_id")

df_users = df_users[['id', 'old_user_id']]
df_users = df_users.drop_duplicates()

df_ratings = df_ratings[['user_id', 'item_id', 'rating']]



engine = create_engine(config.DB_URI, echo=False)
session = scoped_session(sessionmaker(bind=engine,
                                      autocommit = False,
                                      autoflush = False))



# Append users
df_users.to_sql('users',engine,if_exists='append', index=False) #if_exists='append'
session.commit()

#Append items
df_items.to_sql('items',engine,if_exists='append', index=False)#if_exists='append'
session.commit()

# Append ratings
df_ratings.to_sql('ratings',engine,if_exists='append', index=False)#if_exists='append'
session.commit()
