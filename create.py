from flask import Flask, render_template, request, redirect
from flask import url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Org, Project, Role, Screen, Function, Functgroup, Base
from sqlalchemy.pool import StaticPool
from flask import session as login_session
import random
import string
import httplib2
import json
from flask import make_response
import requests
from flask import Blueprint

create = Blueprint('create', __name__)

# set shorthand variable for connecting to database
engine = create_engine('sqlite:///project-map-tool.db',
                       connect_args={'check_same_thread': False},
                       poolclass=StaticPool)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@create.route('/blueprint')
def blueprintTest():
    allorgs = session.query(Org).all()
    allprojects = session.query(Project).all()
    return render_template('main.html', allorgs=allorgs,
                            allprojects=allprojects)

# serves new org form for get request, adds form data to db for post
@create.route('/new', methods=['GET', 'POST'])
def newOrg():
    if request.method == 'POST':
        newOrg = Org(title=request.form['orgtitle'],
                     description=request.form['orgdesc'])
        session.add(newOrg)
        session.commit()
        flash("New org created!")
        org = session.query(Org).filter_by(title=request.form['orgtitle']).one()
        return redirect(url_for('orgPage',org_id=org.id))
    else:
        return render_template('create/org.html')
