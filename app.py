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
    roles = session.query(Role).filter_by(org_id=org.id).all()
    screens = session.query(Screen).filter_by(project_id=project.id).all()
    fgs = session.query(Functgroup).filter_by(project_id=project.id).all()
    functions = session.query(Function).filter_by(project_id=project.id).all()
    return render_template('project.html', org=org,
                           project=project, roles=roles,
                           screens=screens, fgs=fgs,
                           functions=functions)


@app.route('/<int:org_id>/')
def orgPage(org_id):
    org = session.query(Org).filter_by(id=org_id).one()
    sprojects = session.query(Project).filter_by(
        org_id=org.id,stage="Started").all()
    nsprojects = session.query(Project).filter_by(
        org_id=org.id,stage="Not Started").all()
    return render_template('org.html', org=org,
        sprojects=sprojects, nsprojects=nsprojects)


@app.route('/')
def mainPage():
    orgs = session.query(Org).all()
    projects = session.query(Project).all()
    return render_template('main.html', orgs=orgs, projects=projects)


if __name__ == '__main__':
    # app.secret_key = CLIENT_SECRET
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
