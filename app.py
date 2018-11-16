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

app = Flask(__name__)

# set shorthand variable for connecting to database
engine = create_engine('sqlite:///project-map-tool.db',
                       connect_args={'check_same_thread': False},
                       poolclass=StaticPool)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
allorgs = session.query(Org).all()
allprojects = session.query(Project).all()

@app.route('/')
def mainPage():
    return render_template('main.html', allorgs=allorgs,
                            allprojects=allprojects)


# query specified org object & all project objects associated with org
# serves objects to org page template
@app.route('/<int:org_id>/')
def orgPage(org_id):
    org = session.query(Org).filter_by(id=org_id).one()
    projects = session.query(Project).filter_by(org_id=org.id).all()
    return render_template('org.html', org=org, projects=projects,
                            allorgs=allorgs, allproject=allprojects)


# query specified org & project objects
# query projects objects associated with org
# query function groups, screens, functions & role objects for specified project
# pass objects to project page template
@app.route('/<int:org_id>/<int:project_id>/')
def projectPage(org_id, project_id):
    org = session.query(Org).filter_by(id=org_id).one()
    project = session.query(Project).filter_by(id=project_id).one()
    projects = session.query(Project).filter_by(org_id=org.id).all()
    roles = session.query(Role).filter_by(org_id=org.id).all()
    screens = session.query(Screen).filter_by(project_id=project.id).all()
    fgs = session.query(Functgroup).filter_by(project_id=project.id).all()
    functions = session.query(Function).filter_by(project_id=project.id).all()
    return render_template('project.html', org=org,
                           project=project, roles=roles,
                           screens=screens, fgs=fgs,
                           functions=functions, projects=projects,
                           allorgs=allorgs, allprojects=allprojects)


# serves new org form for get request, adds form data to db for post
@app.route('/new', methods=['GET', 'POST'])
def newOrg():
    if request.method == 'POST':
        newOrg = Org(title=request.form['orgtitle'],
                     description=request.form['orgdesc'])
        session.add(newOrg)
        session.commit()
        flash("New org created!")
        org = session.query(Org).filter_by(title=request.form['orgtitle']).one()
        if request.form['projtitle'] is not None:
            newProj = Project(title=request.form['projtitle'],
                              description=request.form['projdesc'],
                              stage="Not Started",
                              org_id=org.id)
            session.add(newProj)
            session.commit()
            flash("New project created!")
        return redirect(url_for('orgPage',org_id=org.id))
    else:
        return render_template('newOrg.html')


# query specified org, serve edit org page for get, update form data for post
@app.route('/<int:org_id>/edit', methods=['GET', 'POST'])
def editOrg(org_id):
    editOrg=session.query(Org).filter_by(id=org_id).one()
    if request.method == 'POST':
        if request.form['orgtitle']:
            editOrg.title = request.form['orgtitle']
            editOrg.description = request.form['orgdesc']
        session.add(editOrg)
        session.commit()
        flash("Org Edited!")
        return redirect(url_for('orgPage',org_id=editOrg.id))
    else:
        return render_template('editOrg.html', org=editOrg)


# query specified org, serve delete form for get
# on post, cycle-delete all projects in db, then org
@app.route('/<int:org_id>/del', methods=['GET', 'POST'])
def delOrg(org_id):
    delOrg = session.query(Org).filter_by(id=org_id).one()
    delProjects = session.query(Project).filter_by(org_id=org_id).all()
    if request.method == 'POST':
        for i in delProjects:
            session.delete(i)
        session.delete(delOrg)
        session.commit()
        flash("Org & Associated Projects Removed")
        return redirect(url_for('mainPage'))
    else:
        return render_template('delOrg.html', i=delOrg)


# query specified project, org; serve delete form for get, delete db for post
@app.route('/<int:org_id>/<int:project_id>/del', methods=['GET', 'POST'])
def delProject(org_id, project_id):
    delOrg = session.query(Org).filter_by(id=org_id).one()
    delProject = session.query(Project).filter_by(id=project_id).one()
    if request.method == 'POST':
        session.delete(delProject)
        session.commit()
        flash("Project Removed")
        return redirect(url_for('mainPage'))
    else:
        return render_template('delProject.html', i=delProject, o=delOrg)


if __name__ == '__main__':
    app.secret_key = 'supersecretkey'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
