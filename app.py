from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()
app = Flask(__name__)

class TodoList(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50),nullable=False,default="My Todo List")
	items = db.relationship('TodoItem',backref='list',lazy='dynamic')

class TodoItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listID = db.Column(db.Integer, db.ForeignKey('todo_list.id'))
    description = db.Column(db.String(100),nullable=False,default="")
    completed = db.Column(db.Boolean,nullable=False,default=False)

@app.route('/')
def showLists():
	lists = TodoList.query.all()
	return render_template("showlists.html",todolists=lists)

@app.route('/list/<listid>')
def viewList(listid):
	if(listid is None):
		return ('', 204)
	list = TodoList.query.filter_by(id=listid).first()
	if(list is None):
		return ('', 204)
	return render_template("viewlist.html",todolist=list)

@app.route("/addlist", methods=['POST'])
def addList():
    item = request.form['newlist']
    if(item is None or item == ""):
        return ('', 204)
    newList = TodoList()
    newList.name = item
    db.session.add(newList)
    db.session.commit()
    return redirect(url_for('showLists'))

@app.route('/addItem/<listid>', methods=['POST'])
def addItem(listid):
    item = request.form['newitem']
    if(listid is None or item is None or item == ""):
        return ('', 204)
    list = TodoList.query.filter_by(id=listid).first()
    if(list is None):
        return ('', 204)
    newItem = TodoItem(list=list,description=item)
    db.session.add(newItem)
    db.session.commit()
    return redirect(url_for("viewList",listid=listid))

@app.route('/completeItem/<listid>/<itemID>/', methods=['POST'])
def completeItem(listid,itemID):
    if(itemID is None):
        return jsonify(success=False)
    item = TodoItem.query.filter_by(id=itemID).first()
    if(item is None):
        return jsonify(success=False)
    item.completed = True
    db.session.commit()
    return redirect(url_for("viewList",listid=listid))

@app.route('/removeItem/<listid>/<itemID>/', methods=['POST'])
def removeItem(listid,itemID):
    if(itemID is None):
        return jsonify(success=False)
    print("Going to remove: ", itemID)
    item = TodoItem.query.filter_by(id=itemID).first()
    if(item is None):
        return jsonify(success=False)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("viewList",listid=listid))

@app.route('/removeList/<listid>', methods=['POST'])
def removeList(listid):
    list = TodoList.query.filter_by(id=listid).first()
    if(list is None):
        return jsonify(success=False)
    db.session.delete(list)
    delete_items = TodoItem.__table__.delete().where(TodoItem.listID == listid)
    db.session.execute(delete_items)
    db.session.commit()
    return redirect(url_for("showLists"))


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['TODO_SQL_URI']
	
db.init_app(app)

with app.app_context():	
    db.create_all()

app.run(host="0.0.0.0", port=5000)
