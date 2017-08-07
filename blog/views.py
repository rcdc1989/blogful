from flask import render_template
from flask import request, redirect, url_for
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
    # Zero-indexed page
    page_index = page - 1

    count = session.query(Entry).count()

    start = page_index * PAGINATE_BY
    end = start + PAGINATE_BY

    total_pages = (count - 1) // PAGINATE_BY + 1
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
        total_pages=total_pages
    )

#view for displaying a single entry
@app.route("/entry/<int:ID>")
def view_entry(ID=1):
    
    #In the database, ID is indexed at 1. 
    #This is OK, here we assume that the user knows the ID number from database
    entry = session.query(Entry).get(ID)
    query_list = session.query(Entry.id).order_by(Entry.id).all()
    entries_id = [i[0] for i in query_list]
    
    #we increment the index number to get position that is aligned with "ID"
    position = entries_id.index(ID) 
    count = session.query(Entry).count()
    print(position)
    print(count)
    
    #to handle case where id numbers are not contiguous (because of deletions)
    
    has_prev = position > 0 #check entry is not first in the list
    has_next = position < count - 1 #check entry is not last in the list
    
    #we use "try" to handle cases where there is no
    try:
        next_id = entries_id[position + 1]#get id for next entry
    except IndexError:
        next_id = ID
    try:
        prev_id = entries_id[position - 1]
    except IndexError:
        prev_id = ID
        
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
def add_entry_get():
    return render_template("add_entry.html")

#view for handling "POST" output
@app.route("/entry/add", methods=["POST"])
def add_entry_post():
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
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
def edit_entry_get(ID=1):
    
    content = session.query(Entry.content).filter(Entry.id==ID).first()[0]
    title = session.query(Entry.title).filter(Entry.id==ID).first()[0]
    
    return render_template("edit_entry.html",
        ID=ID,
        content=content,
        title=title
        )

#EDIT: view for handling "POST" output
@app.route("/entry/<int:ID>/edit", methods=["POST"])
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

#view for displaying a single entry
@app.route("/delete/<int:ID>/confirm", methods = ["GET"])
def delete_entry(ID=1):
    
    entry = session.query(Entry).get(ID)

    return render_template("delete_entry.html",
        entry=entry,
        ID=ID,
        )
        

#EDIT: view for handling "POST" output
@app.route("/delete/<int:ID>/confirm", methods=["POST"])
def delete_entry_post(ID=1):
    confirmed = request.form["confirm"]
    if confirmed:
        entry = session.query(Entry).get(ID)
        session.delete(entry)
        session.commit()
    return redirect(url_for("entries"))