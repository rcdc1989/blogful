from flask import render_template
from flask import request, redirect, url_for
from . import app
from .database import session, Entry


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
    
    #to handle case where id numbers are not contiguous (because of deletions)
    has_prev = position > 0 #check entry is not first in the list
    has_next = position < count - 2 #check entry is not last in the list
    
    try:
        next_id = entries_id[position + 1]#get id for next entry
        prev_id = entries_id[position - 1]
    
    except IndexError:
        
        next_id = ID
        prev_id = ID
        
    return render_template("single_entry.html",
        entry=entry,
        ID=ID,
        has_next=has_next,
        has_prev=has_prev,
        next_id = next_id,
        prev_id = prev_id
    )

#view for "add entry" form
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