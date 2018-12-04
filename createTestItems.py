from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Org, Project, Role, Screen, Function, Functgroup, Base

engine = create_engine('sqlite:///project-map-tool.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# adding test org
org1 = Org(title="abcd",
           description="An org for testing purposes")
session.add(org1)
session.commit()


org2 = Org(title="xkcd",
           description="An org for testing purposes")
session.add(org2)
session.commit()


# adding test projects
project1 = Project(title="Phase 1",
                   description="A project for testing purposes",
                   org_id="1")
session.add(project1)
session.commit()


project2 = Project(title="Phase 2",
                   description="A project for testing purposes",
                   org_id="1")
session.add(project2)
session.commit()


project3 = Project(title="Phase 1",
                   description="A project for testing purposes",
                   org_id="2")
session.add(project3)
session.commit()


project4 = Project(title="Phase 2",
                   description="A project for testing purposes",
                   org_id="2")
session.add(project4)
session.commit()


# adding test roles
role1 = Role(title="Unauthenticated User",
             description="A role for testing purposes",
             authRequired="Yes",
             project_id="1")
session.add(role1)
session.commit()


role2 = Role(title="Authenticated User",
             description="A role for testing purposes",
             authRequired="No",
             project_id="1")
session.add(role2)
session.commit()


role3 = Role(title="Unauthenticated User",
             description="A role for testing purposes",
             authRequired="Yes",
             project_id="2")
session.add(role3)
session.commit()


role4 = Role(title="Authenticated User",
             description="A role for testing purposes",
             authRequired="No",
             project_id="2")
session.add(role4)
session.commit()


# adding test screens
screen1 = Screen(title="Public Screen",
               description="A screen for testing purposes",
               project_id="1")
session.add(screen1)
session.commit()


screen2 = Screen(title="Private Screen",
               description="A screen for testing purposes",
               project_id="1")
session.add(screen2)
session.commit()


# adding test sections
section1 = Section(title="Public Screen",
               description="A screen for testing purposes",
               project_id="1")
session.add(section1)
session.commit()


section2 = Section(title="Private Screen",
               description="A screen for testing purposes",
               project_id="1")
session.add(section2)
session.commit()


# adding test elements
elem1 = Function(title="Test Element",
                  description="An element for testing purposes",
                  project_id="1",
                  section_id="1")
session.add(elem1)
session.commit()


elem2 = Function(title="Test Element",
                  description="An element for testing purposes",
                  project_id="1",
                  section_id="1")
session.add(elem2)
session.commit()


# adding test function group
action1 = Functgroup(title="Function Group 1",
                 description="A function group for testing purposes",
                 functions="1,3",
                 org_id="1",
                 project_id="1")
session.add(action1)
session.commit()


print ("Added test elements!")
