from flask import Flask, render_template, request, redirect
from flask import url_for, flash, jsonify
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker
from database_setup import Org, Project, Role
from database_setup import Screen, Function, Functgroup
from database_setup import Action, Story, Section
from database_setup import Element, RoleScreen, RoleSection
from database_setup import StoryScreen, user, userProject
from database_setup import SectionElement, ScreenSection
from database_setup import userOrg, super, Base
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
@app.route('/o?<int:org_id>')
def orgPage(org_id):
    allorgs = session.query(Org).all()
    allprojects = session.query(Project).all()
    org = session.query(Org).filter_by(id=org_id).one()
    projects = session.query(Project).filter_by(org_id=org.id).all()
    userOrgs = session.query(userOrg).filter_by(org_id=org.id).all()
    return render_template('org.html', org=org, projects=projects,
                            allorgs=allorgs, allprojects=allprojects,
                            userOrgs=userOrgs)


# query specified org & project objects
# query projects objects associated with org
# query function groups, screens, functions & role objects for project
# pass objects to project page template
@app.route('/o?<int:org_id>&p?<int:project_id>')
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


# query specified project & screen
# query roleScreen, roleSection, storyScreen for related screen
# pass info to template to display wireframe of screen, with user stories, etc
@app.route('/p<int:project_id>/scrn<int:screen_id>')
def screenPage(project_id, screen_id):
    allorgs = session.query(Org).all()
    allprojects = session.query(Project).all()
    project = session.query(Project).filter_by(id=project_id).one()
    org = session.query(Org).filter_by(id=project.org.id).one()
    projects = session.query(Project).filter_by(org_id=org.id).all()
    screens = session.query(Screen).filter_by(project_id=project.id).all()
    roleaccess = session.query(Role.id, Role.title, RoleScreen.access).\
        join(RoleScreen).\
        filter(Role.project_id==project_id).\
        filter(RoleScreen.screen_id==screen_id).all()
    knownroles=[]
    for i in roleaccess:
        knownroles.append(i.id)
    getnewroles = session.query(Role).\
        filter(Role.project_id==project_id).\
        filter(Role.id not in knownroles).all()
    newroles = []
    for i in getnewroles:
        if i.id not in knownroles:
            newrole=Role(id=i.id, title=i.title)
            newroles.append(newrole)
    screen = session.query(Screen).filter_by(id=screen_id).one()
    screenSections = session.query(ScreenSection).\
        filter_by(screen_id=screen_id).all()
    roleScreen = session.query(RoleScreen).filter_by(screen_id=screen_id).all()
    se=session.query(SectionElement).filter_by(project_id=project.id).all()
    # BROKEN
    # sectionElements=session.query(SectionElement).\
    #    filter(SectionElement.section_id.in_(screenSections[0])).all()
    return render_template('wire.html', screen=screen,
        screenSections=screenSections,
        roleScreen=roleScreen,
        allorgs=allorgs,
        allprojects=allprojects, roleaccess=roleaccess,
        projects=projects, org=org, newroles=newroles, sectionElements=se,
        screens=screens, project=project)


# A page to lay out user stories for a given screen
@app.route('/scrn<int:screen_id>/story')
def screenStory(screen_id):
    # query all stories, roles, screensections, elements
    # for this screen to variable 'stories'
    screen = session.query(Screen).filter_by(id=screen_id).one()
    project = session.query(Project).filter_by(id=screen.project.id).one()
    stories = session.query(Story).filter_by(screen_id=screen_id).all()
    ss = session.query(ScreenSection).filter_by(screen_id=screen_id).all()
    se = session.query(SectionElement).filter_by(project_id=project.id)
    allorgs = session.query(Org).all()
    allprojects = session.query(Project).all()
    org = session.query(Org).filter_by(id=project.org.id).one()
    projects = session.query(Project).filter_by(org_id=org.id).all()
    screens = session.query(Screen).filter_by(project_id=project.id).all()
    roles = session.query(Role).filter_by(project_id=project.id).all()
    # render template passing stories
    return render_template('stories.html', screen=screen, project=project,
    stories=stories, ss=ss, se=se, allorgs=allorgs, allprojects=allprojects,
    org=org, projects=projects, screens=screens, roles=roles)


# CREATE Pages-------------------------

# serves new screen form for get request, adds form data to db for post
@app.route('/+u', methods=['GET', 'POST'])
def newUser():
    if request.method == 'POST':
        org = session.query(Org).filter_by(title=request.form['orgtitle']).one()
        newUser = user(firstname=request.form['firstname'],
                     lastname=request.form['lastname'],
                     email=request.form['email'])
        session.add(newUser)
        session.commit()
        session.refresh(newUser)
        newUserOrg = userOrg(access=request.form['access'],
                             user_id=newUser.id,
                             org_id=org.id)
        session.add(newUserOrg)
        session.commit()
        flash("New User created!")
        return redirect(url_for('mainPage'))
    else:
        return redirect(url_for('mainPage'))


# serves new org form for get request,
# for post, searches for duplicate org title,
#   if none found, adds form data to db
@app.route('/+o', methods=['GET', 'POST'])
def newOrg():
    if request.method == 'POST':
        # check for org with same title
        try:
            check = session.query(Org).filter_by(
                title=request.form['orgtitle']).one()
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
@app.route('/+p', methods=['GET', 'POST'])
def newProject():
    if request.method == 'POST':
        org = session.query(Org).filter_by(
            title=request.form['org_title']).one()
        unique= checkUniqueTitle(org.id, request.form['title'])
        if unique == "confirmed":
            newProject = Project(title=request.form['title'],
                         description=request.form['description'],
                         org_id=org.id)
            session.add(newProject)
            session.commit()
            flash("New project created!")
            session.refresh(newProject)
            return redirect(url_for('projectPage',org_id=org.id,
                                     project_id=newProject.id))
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
@app.route('/p?<int:project_id>&+rle', methods=['GET', 'POST'])
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
        return redirect(url_for('projectPage',org_id=project.org.id,
                                 project_id=project.id))
    else:
        return render_template('create/role.html', project=project)


# serves new screen form for get request, adds form data to db for post
@app.route('/p?<int:project_id>&+scrn', methods=['GET', 'POST'])
def newScreen(project_id):
    project = session.query(Project).filter_by(id=project_id).one()
    if request.method == 'POST':
        newScreen = Screen(title=request.form['title'],
                     description=request.form['description'],
                     project_id=project.id)
        session.add(newScreen)
        session.commit()
        flash("New Screen created!")
        return redirect(url_for('projectPage',org_id=project.org.id,
                                 project_id=project_id))
    else:
        return render_template('create/screen.html', project=project)


# serves new section form for get request, adds form data to db for post
@app.route('/scrn?<int:screen_id>&+sctn', methods=['GET', 'POST'])
def newSection(screen_id):
    screen = session.query(Screen).filter_by(id=screen_id).one()
    if request.method == 'POST':
        newSection = Section(title=request.form['title'],
                     description=request.form['description'],
                     project_id=screen.project.id)
        session.add(newSection)
        session.commit()
        session.refresh(newSection)
        newScreenSection = ScreenSection(screen_id=screen_id,
            section_id=newSection.id)
        session.add(newScreenSection)
        session.commit()
        flash("New Section created!")
        return redirect(url_for('screenPage',project_id=screen.project.id,
                                 screen_id=screen_id))
    else:
        return render_template('create/section.html', screen=screen)


# serves new element form for get request, adds form data to db for post
@app.route('/sctn?<int:section_id>&+elem', methods=['GET', 'POST'])
def newElement(section_id):
    section = session.query(Section).filter_by(id=section_id).one()
    ss=session.query(ScreenSection).filter_by(section_id=section.id).one()
    screen = session.query(Screen).filter_by(id=ss.screen.id).one()
    project = session.query(Project).filter_by(id=section.project.id).one()
    if request.method == 'POST':
        newElement = Element(title=request.form['title'],
                     description=request.form['description'],
                     project_id=section.project.id)
        session.add(newElement)
        session.commit()
        session.refresh(newElement)
        newSectionElement = SectionElement(section_id=section_id,
            element_id=newElement.id, project_id=project.id)
        session.add(newSectionElement)
        session.commit()
        flash("New Element created!")
        return redirect(url_for('screenPage',project_id=project.id,
                                 screen_id=screen.id))
    else:
        return render_template('create/element.html',
            section=section, screen=screen,
            screensection=ss, project=project)


# serves screen page for get request, adds user story to db for post
@app.route('/p?<int:project_id>&+story', methods=['GET', 'POST'])
def newStory(project_id):
    project = session.query(Project).filter_by(id=project_id).one()
    screen_id = request.form['screen_id']
    screen = session.query(Screen).filter_by(id=screen_id).one()
    if request.method == 'POST':
        rawhook = request.form['hook']
        if rawhook.endswith('_s'):
            sethookID = rawhook[:-2]
            sethook = "section"
        elif rawhook.endswith('_e'):
            sethookID = rawhook[:-2]
            sethook = "element"
        elif rawhook.endswith('_scr'):
            sethookID = rawhook[:-4]
            sethook = "screen"
        else:
            sethook = "unkonwn"
        newStory = Story(project_id=project.id,
            screen_id=screen.id,
            role_id=request.form['role_id'],
            hook=sethook,
            hookID=sethookID,
            action=request.form['action'],
            expectation=request.form['expectation'])
        session.add(newStory)
        session.commit()
        session.refresh(newStory)
        flash("New Story created!")
        return redirect(url_for('screenStory', screen_id=screen.id))
    else:
        return redirect(url_for('projectPage',org_id=project.org.id,
                                 project_id=project.id))


# serves new function form for get, adds form data to db for post
#
# NOTE: Adding Function, then Committing - this may cause an issue! Test!
# Iterating over screens returned from multiselect, adding each to FunctScreen
@app.route('/p?<int:project_id>&+fnctn', methods=['GET', 'POST'])
def newFunction(project_id):
    targetproject = session.query(Project).filter_by(id=project_id).one()
    projectscreens = session.query(Screen).filter_by(
        project_id=project_id).all()
    roles = session.query(Role).filter_by(
        project_id=project_id).all()
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
        #   filter(Project.title==title, Function.org_id==targetproject.org.id,
        #          function.project_id==targetproject.id).one()
        # screens = request.form.getlist('screens')
        flash("New Function created!")
        return redirect(url_for('projectPage',org_id=targetproject.org.id,
                                 project_id=targetproject.id))
    else:
        return render_template('create/function.html', project=targetproject,
                               roles=roles, screens=projectscreens)


# UPDATE Pages-------------------------

# query specified org, serve edit org page for get, update form data for post
@app.route('/o?<int:org_id>&ed', methods=['GET', 'POST'])
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
        return render_template('update/org.html', org=editOrg)


# query specified org & project
# serve edit project page for get, update form data for post
@app.route('/o?<int:org_id>&p?<int:project_id>&ed', methods=['GET', 'POST'])
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
        return redirect(url_for('projectPage',org_id=editOrg.id,
                                 project_id=editProject.id))
    else:
        return render_template('editProject.html', org=editOrg,
                                project=editProject)


# query specified screen
# serve edit screen page for get, update db from form data for post
@app.route('/scrn?<int:screen_id>&ed', methods=['GET', 'POST'])
def editScreen(screen_id):
    editScreen=session.query(Screen).filter_by(id=screen_id).one()
    if request.method == 'POST':
        if request.form['title']:
            editScreen.title = request.form['title']
            editScreen.description = request.form['description']
        session.add(editScreen)
        session.commit()
        flash("Screen Edited!")
        return redirect(url_for('screenPage',project_id=editScreen.project.id,
                                 screen_id=editScreen.id))
    else:
        return redirect(url_for('screenPage',project_id=editScreen.project.id,
                                 screen_id=editScreen.id))


# query specified section
# serve edit screen page for get, update db from form data for post
@app.route('/sctn?<int:section_id>&ed', methods=['GET', 'POST'])
def editSection(section_id):
    editSection=session.query(Section).filter_by(id=section_id).one()
    ss=session.query(ScreenSection).filter_by(section_id=section_id).one()
    screen=session.query(Screen).filter_by(id=ss.screen.id).one()
    if request.method == 'POST':
        if request.form['title']:
            editSection.title = request.form['title']
            editSection.description = request.form['description']
        session.add(editSection)
        session.commit()
        flash("Section Edited!")
        return redirect(url_for('screenPage',project_id=editSection.project.id,
                                 screen_id=ss.screen_id))
    else:
        return render_template('update/section.html', section=editSection,
            ScreenSection=ss, screen=screen)


# query specified element
# serve edit element page for get, update db from form data for post
@app.route('/elem?<int:element_id>&ed', methods=['GET', 'POST'])
def editElement(element_id):
    editElement = session.query(Element).filter_by(id=element_id).one()
    se = session.query(SectionElement).filter_by(element_id=element_id).one()
    ss=session.query(ScreenSection).filter_by(section_id=se.section_id).one()
    screen_id=ss.screen_id
    project_id=editElement.project.id
    if request.method == 'POST':
        if request.form['title']:
            editElement.title = request.form['title']
            editElement.description = request.form['description']
        session.add(editElement)
        session.commit()
        flash("Element Edited!")
        return redirect(url_for('screenPage', project_id=project_id,
                                 screen_id=screen_id))
    else:
        return render_template('update/element.html', element=editElement,
            screen_id=screen_id)


# query specified role; find screens & sections from related project
# serve edit role page for get, update db data for post
@app.route('/rle?<int:role_id>&ed', methods=['GET', 'POST'])
def editRole(role_id):
    editRole=session.query(Role).filter_by(id=role_id).one()
    screens=session.query(Screen).filter_by(
        project_id=editRole.project.id).all()
    sections=session.query(Section).filter_by(
        project_id=editRole.project.id).all()
    if request.method == 'POST':
        if request.form['title']:
            editRole.title = request.form['title']
            editRole.description = request.form['description']
            editRole.authRequired = request.form['authRequired']
        session.add(editRole)
        session.commit()
        flash("Role Edited!")
        return redirect(url_for('projectPage',org_id=editRole.project.org.id,
                                 project_id=editRole.project.id))
    else:
        return render_template('update/role.html', editRole=editRole,
            section=sections, screens=screens)


# query specified role; find screens & sections from related project
# serve edit role page for get, update db data for post
@app.route('/story?<int:story_id>&ed', methods=['GET', 'POST'])
def editStory(story_id):
    editStory=session.query(Story).filter_by(id=story_id).one()
    project = session.query(Project).filter_by(id=editStory.project.id).one()
    screen = session.query(Screen).filter_by(id=editStory.screen.id).one()
    if editStory.hook == "screen":
        target_type="screen"
        target = session.query(Screen).filter_by(id=editStory.hookID).one()
    elif editStory.hook == "section":
        target_type="section"
        target = session.query(Section).filter_by(id=editStory.hookID).one()
    elif editStory.hook == "element":
        target_type="element"
        target = session.query(Element).filter_by(id=editStory.hookID).one()
    else:
        target_type = "unknown"
        title = "unknown"
    if request.method == 'POST':
        if request.form['role_id']:
            editStory.action = request.form['action']
            editStory.expectation = request.form['expectation']
        session.add(editStory)
        session.commit()
        session.refresh(editStory)
        flash("Story edited!")
        return redirect(url_for('screenStory', screen_id=screen.id))
    else:
        return render_template('update/story.html', story=editStory,
        target_title=target.title, target_type=target_type, project=project,
        screen=screen)


@app.route('/_fliprolescreen/r?<int:role_id>/scrn?<int:screen_id>')
def flipRoleScreen(role_id, screen_id):
    screen=session.query(Screen).filter_by(id=screen_id).one()
    try:
        check = session.query(RoleScreen).\
            filter(and_(RoleScreen.role_id==role_id,
                RoleScreen.screen_id==screen_id)).one()
    except:
        check = "nf"
    if check == "nf":
        newRow = RoleScreen(project_id=screen.project.id,
            screen_id=screen.id, role_id=role_id, access="1")
        session.add(newRow)
        session.commit()
        return redirect(url_for('screenPage', project_id=screen.project.id,
            screen_id=screen.id))
    if check.access == "1":
        check.access = "0"
        session.add(check)
        session.commit()
        flash("Role's access to screen revoked.")
        return redirect(url_for('screenPage', project_id=screen.project.id,
            screen_id=screen.id))
    if check.access == "0":
        check.access = "1"
        session.add(check)
        session.commit()
        flash("Role granted access to screen.")
        return redirect(url_for('screenPage', project_id=screen.project.id,
            screen_id=screen.id))
    else:
        output=""
        test1=check.role_id
        test2=check.screen_id
        test3=check.access
        output+="role_id: " + str(test1) + "<br>"
        output+="screen_id: " + str(test2)+ "<br>"
        output+="access: " + str(test3)+ "<br>"
        return output
        # check is a list of RoleScreens, which have attributes:
        # id, access, project_id, role_id, screen_id



# DELETE Pages-------------------------

# query specified org, serve delete form for get
# on post, cycle-delete all project elements per org,
#   then projects per org, then finally - org
@app.route('/o?<int:org_id>&d', methods=['GET', 'POST'])
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
@app.route('/o?<int:org_id>&o?<int:project_id>&d', methods=['GET', 'POST'])
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
@app.route('/rle?<int:role_id>&d', methods=['GET', 'POST'])
def delRole(role_id):
    delRole = session.query(Role).filter_by(id=role_id).one()
    project = session.query(Project).filter_by(id=delRole.project.id).one()
    org_id=project.org.id
    if request.method == 'POST':
        session.delete(delRole)
        session.commit()
        flash("Role Removed")
        return redirect(url_for('projectPage',org_id=org_id,
                                 project_id=project.id))
    else:
        return render_template('delete/role.html', i=delRole, project=project)


# query specified screen, observe org & project id's in role object
# serve delete form for get; on post, delete function
@app.route('/scrn?<int:screen_id>&d', methods=['GET', 'POST'])
def delScreen(screen_id):
    delScreen = session.query(Screen).filter_by(id=screen_id).one()
    org_id=delScreen.project.org.id
    project_id=delScreen.project.id
    allorgs = session.query(Org).all()
    allprojects = session.query(Project).all()
    if request.method == 'POST':
        session.delete(delScreen)
        session.commit()
        flash("Screen Removed")

        return redirect(url_for('projectPage', project_id=screen.project.id,
            screen_id=screen_id))
    else:
        return render_template('delete/screen.html', i=delScreen)


# query specified section, observe org & project id's in role object
# serve delete form for get; on post, delete function
@app.route('/sctn?<int:section_id>&d', methods=['GET', 'POST'])
def delSection(section_id):
    delSection = session.query(Section).filter_by(id=section_id).one()
    ss=session.query(ScreenSection).filter_by(section_id=section_id).one()
    try:
        se = session.query(SectionElement).filter_by(
            section_id=section_id).all()
    except:
        se = ""
    screen_id=ss.screen_id
    project_id=delSection.project.id
    if request.method == 'POST':
        if se != "":
            for i in se:
                session.delete(i)
        session.delete(delSection)
        session.delete(ss)
        session.commit()
        flash("Section Removed")
        return redirect(url_for('screenPage', project_id=project_id,
            screen_id=screen_id))
    else:
        return render_template('delete/section.html', i=delSection)


# query specified section, observe org & project id's in role object
# serve delete form for get; on post, delete function
@app.route('/elem?<int:element_id>&d', methods=['GET', 'POST'])
def delElement(element_id):
    delElement = session.query(Element).filter_by(id=element_id).one()
    se=session.query(SectionElement).filter_by(element_id=element_id).one()
    ss=session.query(ScreenSection).filter_by(section_id=se.section_id).one()
    project=session.query(Project).filter_by(id=delElement.project.id).one()
    project_id=delElement.project.id
    screen_id=ss.screen.id
    if request.method == 'POST':
        session.delete(delElement)
        session.delete(se)
        session.commit()
        flash("Element Removed")
        return redirect(url_for('screenPage', project_id=project_id,
            screen_id=screen_id))
    else:
        return render_template('delete/element.html', i=delElement,
            project=project, screen_id=ss.screen_id)


# query specified function, observe org & project id's in role object
# serve delete form for get; on post, delete function
@app.route('/fnctn?<int:function_id>&d', methods=['GET', 'POST'])
def delFunction(function_id):
    delFunction = session.query(Function).filter_by(id=function_id).one()
    org_id=delFunction.org_id
    project_id=delFunction.project_id
    if request.method == 'POST':
        session.delete(delFunction)
        session.commit()
        flash("Function Removed")
        return redirect(url_for('screenPage',org_id=org_id,
                                 project_id=project_id))
    else:
        return render_template('delete/function.html', i=delFunction)


# receive user_id, query userOrg (and in the future, userProject) rows matching,
# delete userOrg rows, then user record
# serve delete form for get; on post, delete user
@app.route('/u?<int:user_id>&d', methods=['GET', 'POST'])
def delUser(user_id):
    delUser = session.query(user).filter_by(id=user_id).one()
    delUserOrg = session.query(userOrg).filter_by(user_id=user_id).all()
    if request.method == 'POST':
        for i in delUserOrg:
            session.delete(i)
        session.delete(delUser)
        session.commit()
        flash("User Removed")
        return redirect(url_for('mainPage'))
    else:
        return render_template('delete/user.html', i=delUser)


# JSON Pages---------------------------

# JSON Project page:
# displays project info in db, serialized
@app.route('/o?<int:org_id>&p?<int:project_id>/JSON')
def projectJSON(org_id, project_id):
    org = session.query(Org).filter_by(id=org_id).one()
    project = session.query(Project).filter_by(
        org_id=org_id, id=project_id).one()
    return jsonify(Project=project.serialize)


# JSON Org page:
# displays org info in db, serialized
@app.route('/o?<int:org_id>/JSON')
def orgJSON(org_id):
    org = session.query(Org).filter_by(id=org_id).one()
    projects = session.query(Project).filter_by(org_id=org_id).all()
    # return jsonify(Projects=[i.serialize for i in projects])
    return jsonify(Org=org.serialize)


# JSON Org Projects page:
# displays info for all of an orgs projects in db, serialized
@app.route('/o?<int:org_id>/projects/JSON')
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
