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


# db dump pages for testing
@app.route('/orgdump')
def orgs():
    orgs = session.query(Org).all()
    output = '<br><br>'
    for i in orgs:
        output += 'org id: ' + str(i.id) + '<br>'
        output += 'username: ' + i.title + '<br>'
        output += 'email: ' + i.description + '<br></br>'
    return output

@app.route('/projectdump')
def projects():
    projects = session.query(Project).all()
    output = '<br><br>'
    for i in projects:
        output += 'org: ' + str(i.org_id) + '<br>'
        output += 'project id: ' + str(i.id) + '<br>'
        output += 'title: ' + i.title + '<br>'
        output += 'description: ' + i.description + '<br>'
        output += 'stage: ' + i.stage + '<br></br>'
    return output

@app.route('/roledump')
def roles():
    roles = session.query(Role).all()
    output = '<br><br>'
    for i in roles:
        output += 'org: ' + str(i.org_id) + '<br>'
        output += 'project id: ' + str(i.project_id) + '<br>'
        output += 'role id: ' + str(i.id) + '<br>'
        output += 'title: ' + i.title + '<br>'
        output += 'description: ' + i.description + '<br>'
        output += 'authRequired: ' + i.authRequired + '<br></br>'
    return output

@app.route('/screendump')
def screens():
    screens = session.query(Screen).all()
    output = '<br><br>'
    for i in screens:
        output += 'org: ' + str(i.org_id) + '<br>'
        output += 'project id: ' + str(i.project_id) + '<br>'
        output += 'role id: ' + str(i.id) + '<br>'
        output += 'title: ' + i.title + '<br>'
        output += 'description: ' + i.description + '<br>'
        output += 'authRequired: ' + i.authRequired + '<br>'
        output += "associated role_id's: " + i.roles + '<br><br>'
    return output

@app.route('/functdump')
def funct():
    funct = session.query(Function).all()
    output = '<br><br>'
    for i in funct:
        output += 'org: ' + str(i.org_id) + '<br>'
        output += 'project id: ' + str(i.project_id) + '<br>'
        output += 'function id: ' + str(i.id) + '<br>'
        output += "associated screen_id's: " + str(i.screen_id) + '<br>'
        output += 'title: ' + i.title + '<br>'
        output += 'description: ' + i.description + '<br>'
        output += 'authRequired: ' + i.authRequired + '<br>'
        output += "associated role_id's: " + i.roles + '<br><br>'
    return output

@app.route('/fgdump')
def fgdump():
    fg = session.query(Functgroup).all()
    output = '<br><br>'
    for i in fg:
        output += 'org: ' + str(i.org_id) + '<br>'
        output += 'project id: ' + str(i.project_id) + '<br>'
        output += 'function group id: ' + str(i.id) + '<br>'
        output += 'title: ' + i.title + '<br>'
        output += 'description: ' + i.description + '<br>'
        output += "associated function_id's: " + i.functions + '<br><br>'
    return output


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
                           functions=functions, projects=projects)


@app.route('/<int:org_id>/')
def orgPage(org_id):
    org = session.query(Org).filter_by(id=org_id).one()
    projects = session.query(Project).filter_by(org_id=org.id).all()
    return render_template('org.html', org=org, projects=projects)


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

@app.route('/')
def mainPage():
    orgs = session.query(Org).all()
    projects = session.query(Project).all()
    return render_template('main.html', orgs=orgs, projects=projects)


if __name__ == '__main__':
    app.secret_key = 'supersecretkey'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
