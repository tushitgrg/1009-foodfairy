from flask import Flask, redirect, url_for, render_template, request, session
from werkzeug.utils import secure_filename
import requests
import os
import openai
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
openai.api_key = "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"
app.secret_key = "1234"
app.config['UPLOAD_FOLDER'] = "static"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///foodfairy.sqlite3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class foodfairy(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(100))
  blogtitle = db.Column(db.String(100))
  blogdata = db.Column(db.String(100000000000000))

  def __init__(self, username, blogtitle, blogdata):
    self.username = username
    self.blogtitle = blogtitle
    self.blogdata = blogdata


def getdetails(pname):
  prompt = "Give me Short Description of " + pname + "Also Write Farming methods, or precautions to take while growing this."
  response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                          messages=[
                                            {
                                              "role": "user",
                                              "content": prompt
                                            },
                                          ])
  details = response.choices[0].message.content
  return details


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/scanner', methods=["POST", "GET"])
def scanner():
  if request.method == "POST":

    organ = request.form["organ"]
    files = request.files.getlist('source')
    imagelinks = ""
    for file in files:
      filename = secure_filename(file.filename)

      file.save(
        os.path.join(os.path.abspath(os.path.dirname(__file__)),
                     app.config['UPLOAD_FOLDER'], filename))

      imagelink = f"{request.url_root}static/" + filename
    url = "https://my-api.plantnet.org/v2/identify/all?images=" + imagelink + "&organs=" + organ + "&include-related-images=true&no-reject=false&lang=en&api-key=2b10HbhnHDd56iPFf8aoXcv3e"
    response5 = requests.get(url)
    data5 = response5.json()
    results = data5.get('results')
    score = results[0]['score']
    accuracy = int(score * 100)
    species = results[0]['species']
    img = results[0]['images']
    img2 = img[0]['url']

    pname = species.get('scientificNameWithoutAuthor')
    details = getdetails(pname)
    return render_template('show.html',
                           tname=pname,
                           desc=details,
                           image=imagelink)

  else:
    return redirect("/")


@app.route('/query', methods=["POST", "GET"])
def query():
  if request.method == "POST":
    query = request.form["query"]
    prompt = f"Answer this Question as Food Fairy, '{query}'"
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                            messages=[
                                              {
                                                "role": "user",
                                                "content": prompt
                                              },
                                            ])
    answer = response.choices[0].message.content
    imagelink = "static/fairy.jpeg"
    blogg = foodfairy("Food Fairy", query, answer)
    db.session.add(blogg)
    db.session.commit()
    return render_template('show.html',
                           tname="Fairy's Answer!",
                           desc=answer,
                           image=imagelink)


@app.route('/preserve', methods=["POST", "GET"])
def preserve():
  if request.method == "POST":
    query = request.form["query"]
    prompt = f"Answer this Question as Food Fairy, 'How to Preserve {query}?'"
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                            messages=[
                                              {
                                                "role": "user",
                                                "content": prompt
                                              },
                                            ])
    answer = response.choices[0].message.content
    imagelink = "static/fairy.jpeg"
    blogg = foodfairy("Food Fairy", f"How to Preserve {query}", answer)
    db.session.add(blogg)
    db.session.commit()
    return render_template('show.html',
                           tname="Fairy's Answer!",
                           desc=answer,
                           image=imagelink)


@app.route('/blogs', methods=["POST", "GET"])
def blogs():

  blogss = foodfairy.query.all()

  return render_template("blogs.html", blogss=blogss)


@app.route('/subblogs', methods=["POST", "GET"])
def subblogs():
  if request.method == "POST":
    btitle = request.form["query"]
    uname = request.form["uname"]
    bdata = request.form["blogdata"]
    imagelink = "static/fairy.jpeg"
    blogg = foodfairy(uname, btitle, bdata)
    db.session.add(blogg)
    db.session.commit()
    return redirect('/blogs')


@app.route('/<blogid>')
def blog(blogid):
  bloggg = foodfairy.query.filter_by(id=blogid).first()
  imagelink = "https://plantfairy.tushitgarg.repl.co/static/fairy.jpeg"
  return render_template('show.html',
                         tname=bloggg.blogtitle,
                         desc=bloggg.blogdata,
                         image=imagelink)


with app.app_context():
  db.create_all()
app.run(host='0.0.0.0', port=81)
