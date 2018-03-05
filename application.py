

from flask import Flask, render_template, redirect, request, flash, session, url_for
import model
from sqlalchemy.orm import joinedload
from sqlalchemy import text
from planout.experiment import SimpleExperiment
from planout.ops.random import *
from random import randint, choice
import random


import recommender1
import recommender2


application = Flask(__name__)
app = application
app.secret_key = '23987ETFSDDF345560DFSASF45DFDF567'

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def show_login():
    model.add_pageview(user_id=None, item_id=None, page="login", activity_type="enter login page",rating=None) #pageview
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def process_login():
    email = request.form.get("email")
    password = request.form.get("password")
    user = model.get_user_from_email(email)

    if user == None:
        flash ("This user is not registered yet")
        model.add_pageview(user_id=None, item_id=None, page="login", activity_type="non-registered id / incorrect details",rating=None) #pageview
        return redirect('signup')
    else:
        session['user'] = user.id
        model.add_pageview(user_id=user.id, item_id=None, page="login", activity_type="successful login",rating=None) #pageview
        return redirect(url_for('show_user_details', id=user.id))


@app.route("/signup")
def show_signup():
    return render_template("signup.html")


@app.route("/signup", methods=["POST"])
def make_new_account():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    password = request.form.get("password")
    age = request.form.get("age")
    gender = request.form.get("gender")
    occupation = request.form.get("occupation")
    city = request.form.get("city")
    state = request.form.get("state")
    country = request.form.get("country")
    zipcode = request.form.get("zipcode")
    model.create_user(first_name, last_name, email, password, age, gender,occupation, city, state, country, zipcode)
    model.add_pageview(user_id=None, item_id=None, page="signup", activity_type="successful signup",rating=None) #pageview
    flash ("You're registered! Now please log in")
    return redirect('/login')


@app.route("/user_list/", defaults={"page":1})
@app.route("/user_list/<int:page>")
def user_list(page):
    perpage = 50
    pages = (model.session.query(model.User).count()) / perpage
    back_one = page - 1
    forward_one = page + 1
    user_list = model.session.query(model.User).limit(perpage).offset((page*perpage) -perpage).all()
    return render_template("user_list.html", users=user_list, pages=pages, back=back_one, forward=forward_one)


@app.route("/view_user/<int:id>")
def show_user_details(id):
    user_id = session["user"]
    model.add_pageview(user_id=user_id, item_id=None, page="marketplace", activity_type="enter marketplace",rating=None) #pageview
    user = model.session.query(model.User).filter_by(id=id).join(model.Rating).join(model.Item).first()
    ratings = model.session.query(model.Rating).options(joinedload(model.Rating.item)).filter_by(user_id=id).all()
    return render_template("view_user.html", user=user, ratings=ratings)


@app.route("/view_item/<int:id>")
def view_item_details(id):
    item_ratings = model.show_item_details(id)
    item = item_ratings[0].item
    model.add_pageview(user_id=session["user"], item_id=item.id, page="item", activity_type="start item view",rating=None) #pageview
    return render_template("view_item.html", item=item) #prediction_items=prediction_items,


@app.route("/update_rating", methods=["POST"])
def update_rating():
    new_rating = request.form.get("rating")
    item_id = request.form.get("item")
    user_id = session['user']
    model.update_rating(user_id, item_id, new_rating)
    model.add_pageview(user_id=session["user"], item_id=item_id, page="item", activity_type="rate item",rating=new_rating) #pageview
    model.add_pageview(user_id=session["user"], item_id=item_id, page="item", activity_type="end item view",rating=None) #pageview
    flash ("You've changed your rating for this item")
    return redirect(url_for('show_user_details', id=user_id))


@app.route("/add_cart", methods=["POST"])
def cart_update():
    user_id = session['user']
    item_id = request.form.get("item")
    model.add_cart(user_id, item_id)
    model.add_pageview(user_id=session["user"], item_id=item_id, page="cart", activity_type="add to cart",rating=None) #pageview
    flash ("You've added to your shopping cart!")
    return redirect(url_for('show_user_details', id=user_id))


#
# @app.route("/delete_cart", methods=["POST"])
# def cart_delete():
#     user_id = session['user']
#     item_id = request.form.get("item")
#     model.delete_cart(user_id, item_id)
#     flash ("You've deleted from your shopping cart!")
#     return redirect(url_for('show_user_details', id=user_id))




class AnchoringExperiment(SimpleExperiment):
  def setup(self):
    self.set_log_file('anchoring_webapp.log')

  def assign(self, params, userid):
    params.model_select = UniformChoice(choices=[1,2], unit=userid)
    if params.model_select == 1:
        params.var = 1
    else:
        params.var = 2



@app.route("/recommend_compute/<int:id>")
def recsys_compute(id):
    user_id = session['user']
    model.add_pageview(user_id=session["user"], item_id=None, page="recommender_algorithm", activity_type="initialize recommender", rating=None) #pageview
    model.delete_recommendations()
    anchoring_exp = AnchoringExperiment(userid=random.random())
    selector = anchoring_exp.get("var")
    if selector == 1:
        recommender1.compute_recommendations()
        model.add_algo(user_id=user_id, algorithm="KNNBasic", mae=recommender1.mae1, rmse=recommender1.rmse1)
        model.add_pageview(user_id=session["user"], item_id=None, page="recommender_algorithm", activity_type="used recommender 1", rating=None) #pageview
    else:
        recommender2.compute_recommendations()
        model.add_algo(user_id=user_id, algorithm="NMF", mae=recommender2.mae2, rmse=recommender2.rmse2)
        model.add_pageview(user_id=session["user"], item_id=None, page="recommender_algorithm", activity_type="used recommender 2", rating=None) #pageview

    model.add_pageview(user_id=session["user"], item_id=None, page="recommender_algorithm", activity_type="finish recommender computation", rating=None) #pageview
    flash ("You've computed Recommendations! Please dont re-run until new recommendations are required!!")
    # return render_template("recommendations.html", id=id)
    return redirect(url_for('view_recommendations', id=id))

@app.route("/view_recommendations/<int:id>")
def view_recommendations(id):
    rec,pred_1, pred_2, pred_3, pred_4, pred_5, pred_6,pred_7, pred_8, pred_9,pred_10 = model.show_recommendations(id)
    model.add_pageview(user_id=session["user"], item_id=None, page="recommendations", activity_type="start viewing recommendations", rating=None) #pageview
    return render_template("recommendations.html", id=id, rec=rec, pred_1=pred_1, pred_2=pred_2,pred_3=pred_3, pred_4=pred_4,pred_5=pred_5, pred_6=pred_6, pred_7=pred_7, pred_8=pred_8, pred_9=pred_9, pred_10=pred_10)


@app.route("/rate_recommendations", methods=["POST"])
def add_rec_rating():
    user_id = session['user']
    user_rating_1 = request.form.get("user_rating_1")
    user_rating_2 = request.form.get("user_rating_2")
    user_rating_3 = request.form.get("user_rating_3")
    user_rating_4 = request.form.get("user_rating_4")
    user_rating_5 = request.form.get("user_rating_5")
    user_rating_6 = request.form.get("user_rating_6")
    user_rating_7 = request.form.get("user_rating_7")
    user_rating_8 = request.form.get("user_rating_8")
    user_rating_9 = request.form.get("user_rating_9")
    user_rating_10 = request.form.get("user_rating_10")
    model.add_rec_rating(user_id,user_rating_1,user_rating_2,user_rating_3,user_rating_4,user_rating_5,user_rating_6,user_rating_7,user_rating_8,user_rating_9,user_rating_10)
    model.add_pageview(user_id=session["user"], item_id=None, page="recommendations", activity_type="rate recommendations and finish view", rating=None) #pageview
    flash ("You've rated your recommendations!Thank you for the feedback!")
    return redirect(url_for('to_overall_feedback', id=user_id))


@app.route("/overall_feedback")
def to_overall_feedback():
    model.add_pageview(user_id=session["user"], item_id=None, page="feedback", activity_type="start viewing feedback", rating=None) #pageview
    return render_template("feedback.html")


@app.route("/overall_feedback", methods=["POST"])
def overall_feedback():
    user_id = session['user']
    novelty = request.form.get("novelty")
    unexpectedness = request.form.get("unexpectedness")
    model.add_feedback(user_id,novelty,unexpectedness)
    model.add_pageview(user_id=session["user"], item_id=None, page="feedback", activity_type="finish viewing and giving feedback", rating=None) #pageview
    flash ("Thank you for the overall feedback!")
    return redirect(url_for('show_user_details', id=user_id))

@app.route("/view_cart/<int:id>")
def show_cart_details(id):
    user = model.session.query(model.User).filter_by(id=id).join(model.ShoppingCart).join(model.Item).first()
    shopitem = model.session.query(model.ShoppingCart).options(joinedload(model.ShoppingCart.item)).filter_by(user_id=id).all()
    # ratings = model.session.query(model.Rating).options(joinedload(model.Rating.item)).filter_by(user_id=id).all()
    # return render_template("view_user.html", user=user, ratings=ratings)
    model.add_pageview(user_id=session["user"], item_id=None, page="cart", activity_type="view cart", rating=None) #pageview
    return render_template("shoppercart.html", user=user, shopitem=shopitem)


# @app.route("/delete_cart", methods=["POST"])
# def cart_delete():
#     user_id = session['user']
#     item_id = request.form.get("item")
#     model.delete_cart(user_id, item_id)
#     flash ("You've deleted from your shopping cart!")
#     return redirect(url_for('show_cart_details', id=user_id))





@app.route("/logout")
def process_logout():
    model.add_pageview(user_id=session["user"], item_id=None, page="logout", activity_type="user logout", rating=None) #pageview
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug = True)
