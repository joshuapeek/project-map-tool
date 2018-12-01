from flask import Flask, render_template, request, redirect
from flask import url_for, flash, jsonify
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from database_setup import Org, Project, Role, Screen, Function, Functgroup, Action, Story, Section, Element, roleScreen, roleSection, storyScreen, user, userProject, userOrg, super, Base
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

# @app.route('_getscreen/<int:screen_id>')
# def screen(screen_id):
#     screen = session.query(Screen).filter_by(id=screen_id).one()
#     try:
#         lang = request.args.get('proglang')
#         if str(lang).lower() == 'python':
#             return jsonify(result='You are wise!')
#         else:
#             return jsonify(result='Try again')
#     except Exception, e:
#         return(str(e))


@app.route('/')
def mainPage():
    allorgs = session.query(Org).all()
    allprojects = session.query(Project).all()
    userOrgs = session.query(userOrg).all()
    return render_template('main.html', allorgs=allorgs,
                            allprojects=allprojects,
                            userOrgs=userOrgs)


# query specified org object & all project objects associated with org
# serves objects to org page template
@app.route('/<int:org_id>/')
def orgPage(org_id):
    allorgs = session.query(Org).all()
    allprojects = session.query(Project).all()
    org = session.query(Org).filter_by(id=org_id).one()
    projects = session.query(Project).filter_by(org_id=org.id).all()
    return render_template('org.html', org=org, projects=projects,
                            allorgs=allorgs, allprojects=allprojects)


# query specified org & project objects
# query projects objects associated with org
# query function groups, screens, functions & role objects for specified project
# pass objects to project page template
@app.route('/<int:org_id>/<int:project_id>/')
def projectPage(org_id, project_id):
    allorgs = session.query(Org).all()
    allprojects = session.query(Project).all()
    org = session.query(Org).filter_by(id=org_id).one()
    project = session.query(Project).filter_by(id=project_id).one()
    projects = session.query(Project).filter_by(org_id=org.id).all()
    roles = session.query(Role).filter_by(project_id=project.id).all()
    screens = session.query(Screen).filter_by(project_id=project.id).all()
    fgs = session.query(Functgroup).filter_by(project_id=project.id).all()
    functions = session.query(Function).filter_by(project_id=project.id).all()
    return render_template('project.html', org=org,
                           project=project, roles=roles,
                           screens=screens, fgs=fgs,
                           functions=functions, projects=projects,
                           allorgs=allorgs, allprojects=allprojects)


# CREATE Pages-------------------------

# serves new org form for get request,
# for post, searches for duplicate org title,
#   if none found, adds form data to db
@app.route('/new', methods=['GET', 'POST'])
def newOrg():
    if request.method == 'POST':
        # check for org with same title
        try:
            check = session.query(Org).filter_by(title=request.form['orgtitle']).one()
        except:
            check = None
        if check is not None:
            flash("Org with this title already exists.")
            return redirect(url_for('orgPage', org_id=check.id))
        newOrg = Org(title=request.form['orgtitle'],
                     description=request.form['orgdesc'])
        session.add(newOrg)
        session.commit()
        flash("New org created!")
        org = session.query(Org).filter_by(title=request.form['orgtitle']).one()
        return redirect(url_for('orgPage',org_id=org.id))
    else:
        return render_template('create/org.html')


# serves new org form for get request,
# for post, searches for duplicate project titles within the org,
#   if none found, adds form data to db
@app.route('/newproject', methods=['GET', 'POST'])
def newProject():
    if request.method == 'POST':
        org = session.query(Org).filter_by(title=request.form['org_title']).one()
        unique= checkUniqueTitle(org.id, request.form['title'])
        if unique == "confirmed":
            newProject = Project(title=request.form['title'],
                         description=request.form['description'],
                         org_id=org.id)
            session.add(newProject)
            session.commit()
            flash("New project created!")
            # project = session.query(Project).filter_by(title=request.form['title']).one()
            title=request.form['title']
            project = session.query(Project).\
                filter(Project.title==title, Project.org_id==org.id).one()
            return redirect(url_for('projectPage',org_id=org.id, project_id=project.id))
        else:
            flash("Duplicate project detected")
            return redirect(url_for('mainPage'))
    else:
        return render_template('create/org.html')

def checkUniqueTitle(org_id, project_title):
    projects = session.query(Project).filter_by(org_id=org_id).all()
    unique = "1"
    for i in projects:
        if i.title == project_title:
            unique="0"
    if unique == "1":
        unique = "confirmed"
    return unique


# serves new role form for get request, adds form data to db for post
@app.route('/<int:project_id>/newrole', methods=['GET', 'POST'])
def newRole(project_id):
    project = session.query(Project).filter_by(id=project_id).one()
    if request.method == 'POST':
        newRole = Role(title=request.form['title'],
                     description=request.form['description'],
                     authRequired=request.form['authRequired'],
                     project_id=project.id)
        session.add(newRole)
        session.commit()
        flash("New role created!")
        return redirect(url_for('projectPage',org_id=project.org.id, project_id=project.id))
    else:
        return render_template('create/role.html', project=project)


# serves new screen form for get request, adds form data to db for post
@app.route('/<int:project_id>/newscreen', methods=['GET', 'POST'])
def newScreen(project_id):
    project = session.query(Project).filter_by(id=project_id).one()
    if request.method == 'POST':
        newScreen = Screen(title=request.form['title'],
                     description=request.form['description'],
                     project_id=project.id,
                     org_id=project.org.id)
        session.add(newScreen)
        session.commit()
        flash("New Screen created!")
        screen = session.query(Screen).filter_by(title=request.form['title']).one()
        return redirect(url_for('projectPage',org_id=project.org.id, project_id=project_id))
    else:
        return render_template('create/screen.html', project=project)


# serves new function form for get, adds form data to db for post
#
# NOTE: Adding Function, then Committing - this may cause an issue! Test!
# Iterating over screens returned from multiselect, adding each to FunctScreen
@app.route('/<int:project_id>/newfunction', methods=['GET', 'POST'])
def newFunction(project_id):
    targetproject = session.query(Project).filter_by(id=project_id).one()
    projectscreens = session.query(Screen).filter_by(project_id=project_id).all()
    roles = session.query(Role).filter_by(project_id=project_id).all()
    if request.method == 'POST':
        # receive form with title, description, authRequired, screens (list)
        newFunction = Function(title=request.form['title'],
                        description=request.form['description'],
                        authRequired=request.form['authRequired'],
                        org_id=targetproject.org.id,
                        project_id=targetproject.id,)
        session.add(newFunction)
        session.commit()
        # NEED TO STORE THE ASSOCIATED SCREENS
        # NEED TO STORE THE ASSOCIATED ROLES
        # title=request.form['title']
        # function = session.query(Project).\
        #     filter(Project.title==title, Function.org_id==targetproject.org.id,
        #            function.project_id==targetproject.id).one()
        # screens = request.form.getlist('screens')
        flash("New Function created!")
        return redirect(url_for('projectPage',org_id=targetproject.org.id, project_id=targetproject.id))
    else:
        return render_template('create/function.html', project=targetproject,
                               roles=roles, screens=projectscreens)


# UPDATE Pages-------------------------

# query specified org, serve edit org page for get, update form data for post
@app.route('/<int:org_id>/edit', methods=['GET', 'POST'])
def editOrg(org_id):
    editOrg=session.query(Org).filter_by(id=org_id).one()
    allorgs = session.query(Org).all()
    allprojects = session.query(Project).all()
    if request.method == 'POST':
        if request.form['orgtitle']:
            editOrg.title = request.form['orgtitle']
            editOrg.description = request.form['orgdesc']
        session.add(editOrg)
        session.commit()
        flash("Org Edited!")
        return redirect(url_for('orgPage',org_id=editOrg.id))
    else:
        return render_template('update/org.html', org=editOrg)


# query specified org & project
# serve edit project page for get, update form data for post
@app.route('/<int:org_id>/<int:project_id>/edit', methods=['GET', 'POST'])
def editProject(org_id, project_id):
    editOrg=session.query(Org).filter_by(id=org_id).one()
    editProject=session.query(Project).filter_by(id=project_id).one()
    allorgs = session.query(Org).all()
    allprojects = session.query(Project).all()
    if request.method == 'POST':
        if request.form['projecttitle']:
            editProject.title = request.form['projecttitle']
            editProject.description = request.form['projectdesc']
        session.add(editProject)
        session.commit()
        flash("Project Edited!")
        return redirect(url_for('projectPage',org_id=editOrg.id, project_id=editProject.id))
    else:
        return render_template('editProject.html', org=editOrg, project=editProject)


# DELETE Pages-------------------------

# query specified org, serve delete form for get
# on post, cycle-delete all project elements per org,
#   then projects per org, then finally - org
@app.route('/<int:org_id>/del', methods=['GET', 'POST'])
def delOrg(org_id):
    delOrg = session.query(Org).filter_by(id=org_id).one()
    delProjects = session.query(Project).filter_by(org_id=org_id).all()
    allorgs = session.query(Org).all()
    allprojects = session.query(Project).all()
    if request.method == 'POST':
        for i in delProjects:
            remProjectElements(i.id)
            session.delete(i)
        session.delete(delOrg)
        session.commit()
        flash("Org & Associated Projects Removed")
        return redirect(url_for('mainPage'))
    else:
        return render_template('delete/org.html', i=delOrg)


# query specified project, org; serve delete form for get, delete db for post
# iterate to remove all project elements before deleting project
@app.route('/<int:org_id>/<int:project_id>/del', methods=['GET', 'POST'])
def delProject(org_id, project_id):
    delOrg = session.query(Org).filter_by(id=org_id).one()
    delProject = session.query(Project).filter_by(id=project_id).one()
    if request.method == 'POST':
        remProjectElements(project_id)
        session.delete(delProject)
        session.commit()
        flash("Project Removed")
        return redirect(url_for('mainPage'))
    else:
        return render_template('delete/project.html', i=delProject, o=delOrg)

def remProjectElements(project_id):
    delRoles = session.query(Role).filter_by(id=project_id).all()
    delScreens = session.query(Screen).filter_by(id=project_id).all()
    delFunctions = session.query(Function).filter_by(id=project_id).all()
    for i in delRoles:
        session.delete(i)
    for i in delScreens:
        session.delete(i)
    for i in delFunctions:
        session.delete(i)
    session.commit()
    return


# query specified role, observe org & project id's in role object
# serve delete form for get; on post, delete function
@app.route('/roledel/<int:role_id>', methods=['GET', 'POST'])
def delRole(role_id):
    delRole = session.query(Role).filter_by(id=role_id).one()
    org_id=delRole.org_id
    project_id=delRole.project_id
    if request.method == 'POST':
        session.delete(delRole)
        session.commit()
        flash("Role Removed")
        return redirect(url_for('projectPage',org_id=org_id,
                                 project_id=project_id))
    else:
        return render_template('delete/role.html', i=delRole)


# query specified screen, observe org & project id's in role object
# serve delete form for get; on post, delete function
@app.route('/_screendel/<int:screen_id>', methods=['GET', 'POST'])
def delScreen(screen_id):
    delScreen = session.query(Screen).filter_by(id=screen_id).one()
    org_id=delScreen.org.id
    project_id=delScreen.project.id
    allorgs = session.query(Org).all()
    allprojects = session.query(Project).all()
    if request.method == 'POST':
        session.delete(delScreen)
        session.commit()
        flash("Screen Removed")
        return redirect(url_for('projectPage',org_id=org_id,
                                 project_id=project_id))
    else:
        return render_template('delete/screen.html', i=delScreen)


# query specified function, observe org & project id's in role object
# serve delete form for get; on post, delete function
@app.route('/functiondel/<int:function_id>', methods=['GET', 'POST'])
def delFunction(function_id):
    delFunction = session.query(Function).filter_by(id=function_id).one()
    org_id=delFunction.org_id
    project_id=delFunction.project_id
    if request.method == 'POST':
        session.delete(delFunction)
        session.commit()
        flash("Function Removed")
        return redirect(url_for('projectPage',org_id=org_id,
                                 project_id=project_id))
    else:
        return render_template('delete/function.html', i=delFunction)


# JSON Pages---------------------------

# JSON Project page:
# displays project info in db, serialized
@app.route('/<int:org_id>/<int:project_id>/JSON')
def projectJSON(org_id, project_id):
    org = session.query(Org).filter_by(id=org_id).one()
    project = session.query(Project).filter_by(
        org_id=org_id, id=project_id).one()
    return jsonify(Project=project.serialize)


# JSON Org page:
# displays org info in db, serialized
@app.route('/<int:org_id>/JSON')
def orgJSON(org_id):
    org = session.query(Org).filter_by(id=org_id).one()
    projects = session.query(Project).filter_by(org_id=org_id).all()
    # return jsonify(Projects=[i.serialize for i in projects])
    return jsonify(Org=org.serialize)


# JSON Org Projects page:
# displays info for all of an orgs projects in db, serialized
@app.route('/<int:org_id>/projects/JSON')
def orgProjectsJSON(org_id):
    org = session.query(Org).filter_by(id=org_id).one()
    projects = session.query(Project).filter_by(org_id=org_id).all()
    # return jsonify(Projects=[i.serialize for i in projects])
    return jsonify(Projects=[i.serialize for i in projects])


# JSON Project page:
# displays info for a given project in db, serialized
@app.route('/_get_project/<int:project_id>')
def get_project(project_id):
    project = session.query(Project).filter_by(id=project_id).one()
    return jsonify(Project=project.serialize)


if __name__ == '__main__':
    app.secret_key = 'supersecretkey'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
