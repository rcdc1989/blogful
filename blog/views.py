from flask import render_template
from flask import request, redirect, url_for
from flask import current_user
from flask_login import login_required
from . import app
from .database import session, Entry

"""
 __   ___              ___     _       _        
 \ \ / (_)_____ __ __ | __|_ _| |_ _ _(_)___ ___
  \ V /| / -_) V  V / | _|| ' \  _| '_| / -_|_-<
   \_/ |_\___|\_/\_/  |___|_||_\__|_| |_\___/__/
                                                
"""
#Default paginated view
PAGINATE_BY = 10

@app.route("/")
@app.route("/page/<int:page>")
def entries(page=1):
    count = session.query(Entry).count()
 
    paginate_by = int(request.args.get("limit", PAGINATE_BY))
    
    total_pages = (count - 1) // paginate_by + 1
    page_index = page - 1
    
    # just reset if we are out of bounds with new limit
    if paginate_by != PAGINATE_BY:
        if page_index > total_pages - 1:
            page_index = 0
        
    start = page_index * paginate_by
    end = start + paginate_by

    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())
    entries = entries[start:end]

    return render_template("entries.html",
        entries=entries,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages,
        show_delete=True,
        PAGINATE_BY = PAGINATE_BY
    )

@app.route("/", methods=["POST"])    
@app.route("/page/<int:page>?limit=<PAGINATE_BY>", methods=["POST"])
def entries_post(page=1,PAGINATE_BY=10):
    
    return redirect(url_for("entries", page=1))

#view for displaying a single entry
@app.route("/entry/<int:ID>")
def view_entry(ID=1):
    
    entry = session.query(Entry).get(ID)
    query_list = session.query(Entry.id).order_by(Entry.id).all()
    
    prev_id = session.query(Entry.id).order_by(Entry.id.desc()).filter(Entry.id < ID).first()
    next_id = session.query(Entry.id).order_by(Entry.id.desc()).filter(Entry.id > ID).first()
    
    if prev_id == None:
        has_prev = False
    else:
        has_prev = True
        prev_id = prev_id[0] #get prev_id out of tuple
    
    if next_id == None:
        has_next = False
    else:
        has_next = True
        next_id = next_id[0]
        
    return render_template("single_entry.html",
        entry=entry,
        ID=ID,
        has_next=has_next,
        has_prev=has_prev,
        next_id = next_id,
        prev_id = prev_id
        )

"""        
      _      _    _   ___     _       _        
     /_\  __| |__| | | __|_ _| |_ _ _(_)___ ___
    / _ \/ _` / _` | | _|| ' \  _| '_| / -_|_-<
   /_/ \_\__,_\__,_| |___|_||_\__|_| |_\___/__/
                                               
"""

#ADD: view for "add entry" form
@app.route("/entry/add", methods=["GET"])
@login_required
def add_entry_get():
    return render_template("add_entry.html")

#view for handling "POST" output
@app.route("/entry/add", methods=["POST"])
@login_required
def add_entry_post():
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
        author=current_user
    )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))
    
"""
  ___    _ _ _     ___     _       _        
 | __|__| (_) |_  | __|_ _| |_ _ _(_)___ ___
 | _|/ _` | |  _| | _|| ' \  _| '_| / -_|_-<
 |___\__,_|_|\__| |___|_||_\__|_| |_\___/__/
                                            
"""

#EDIT: view for "edit entry" form
@app.route("/entry/<int:ID>/edit", methods=["GET"])
@login_required
def edit_entry_get(ID=1):
    
    entry = session.query(Entry).get(ID)
    
    return render_template("edit_entry.html",
        ID=ID,
        content=entry.content,
        title=entry.title,
        show_delete=False
        )

#EDIT: view for handling "POST" output
@app.route("/entry/<int:ID>/edit", methods=["POST"])
@login_required
def edit_entry_post(ID=1):
    entry = session.query(Entry).get(ID)
    entry.title = request.form["title"]
    entry.content = request.form["content"]
    session.commit()
    return redirect(url_for("view_entry", ID=ID))
    
"""
  ___      _     _         ___     _       _        
 |   \ ___| |___| |_ ___  | __|_ _| |_ _ _(_)___ ___
 | |) / -_) / -_)  _/ -_) | _|| ' \  _| '_| / -_|_-<
 |___/\___|_\___|\__\___| |___|_||_\__|_| |_\___/__/
                                                    
"""
@app.route("/delete/<int:ID>/confirm", methods=["GET"])
@login_required
def delete_entry_get(ID=1):
    
    entry = session.query(Entry).get(ID)
    
    do_not_delete = True # some fun check_can_delete()
    
    return render_template("delete_entry.html",
        entry=entry,
        ID=ID,
        show_delete=False
        )

@app.route("/delete/<int:ID>/confirm", methods=["POST"])
@login_required
def delete_entry_post(ID=1):

    entry = session.query(Entry).get(ID)
    session.delete(entry)
    session.commit()
    
    return redirect(url_for("entries"))

"""
  _              _      
 | |   ___  __ _(_)_ _  
 | |__/ _ \/ _` | | ' \ 
 |____\___/\__, |_|_||_|
           |___/       
"""

from flask import flash
from flask_login import login_user
from werkzeug.security import check_password_hash
from .database import User

@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")    

@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))

    login_user(user)
    return redirect(request.args.get('next') or url_for("entries"))