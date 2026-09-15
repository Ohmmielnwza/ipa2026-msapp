from flask import Flask

from flask import request

from flask import render_template

from flask import redirect

from flask import url_for


from pymongo import MongoClient

client = MongoClient("mongodb://mongo:27017/")

mydb = client["mydatabase"]

mycol = mydb["mycollection"]

app = Flask(__name__)

@app.route("/")

def main():
    data = mycol.find()
    return render_template("index.html", data=data)



@app.route("/add", methods=["POST"])

def add_comment():

    routerId= request.form.get("routerId")

    username = request.form.get("username")

    password = request.form.get("password")

    mycol.insert_one({"routerId" :  routerId , "username" : username , "password" : password})

    return redirect(url_for("main"))



@app.route("/delete", methods=["POST"])

def delete_comment():

    try:

        idx = request.form.get("idx")

        mycol.delete_one( {"routerId" : idx})

    except Exception:

        pass

    return redirect(url_for("main"))



if __name__ == "__main__":

    app.run(host="0.0.0.0", port=8080)