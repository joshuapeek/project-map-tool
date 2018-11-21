from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Org, Project, Role, Screen, Function, Functgroup, Base

engine = create_engine('sqlite:///project-map-tool.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# adding test orgs
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
                   stage="Started",
                   org_id="1")
session.add(project1)
session.commit()


project2 = Project(title="Phase 2",
                   description="A project for testing purposes",
                   stage="Not Started",
                   org_id="1")
session.add(project2)
session.commit()


project3 = Project(title="Phase 1",
                   description="A project for testing purposes",
                   stage="Started",
                   org_id="2")
session.add(project3)
session.commit()


project4 = Project(title="Phase 2",
                   description="A project for testing purposes",
                   stage="Not Started",
                   org_id="2")
session.add(project4)
session.commit()


# adding test roles
role1 = Role(title="Unauthenticated User",
             description="A role for testing purposes",
             authRequired="No",
             org_id="1",
             project_id="1")
session.add(role1)
session.commit()


role2 = Role(title="Authenticated User",
             description="A role for testing purposes",
             authRequired="No",
             org_id="1",
             project_id="1")
session.add(role2)
session.commit()


role3 = Role(title="Unauthenticated User",
             description="A role for testing purposes",
             authRequired="No",
             org_id="1",
             project_id="2")
session.add(role3)
session.commit()


role4 = Role(title="Authenticated User",
             description="A role for testing purposes",
             authRequired="No",
             org_id="1",
             project_id="2")
session.add(role4)
session.commit()


# adding test screens
screen1 = Screen(title="Public Screen",
               description="A screen for testing purposes",
               authRequired="No",
               roles="1,2",
               org_id="1",
               project_id="1")
session.add(screen1)
session.commit()


screen2 = Screen(title="Private Screen",
               description="A screen for testing purposes",
               authRequired="Yes",
               roles="2",
               org_id="1",
               project_id="1")
session.add(screen2)
session.commit()

# adding test functions
funct1 = Function(title="Public Function",
                  description="A function for testing purposes",
                  authRequired="No",
                  roles="1",
                  org_id="1",
                  project_id="1")
session.add(funct1)
session.commit()


funct2 = Function(title="Private Function",
                  description="A function for testing purposes",
                  authRequired="Yes",
                  roles="2",
                  org_id="1",
                  project_id="1")
session.add(funct2)
session.commit()


funct3 = Function(title="Public Function",
                  description="A function for testing purposes",
                  authRequired="No",
                  roles="1",
                  org_id="1",
                  project_id="1")
session.add(funct3)
session.commit()


funct4 = Function(title="Private Function",
                  description="A function for testing purposes",
                  authRequired="Yes",
                  roles="2",
                  org_id="1",
                  project_id="1")
session.add(funct4)
session.commit()


# adding test function group
fg1 = Functgroup(title="Function Group 1",
                 description="A function group for testing purposes",
                 functions="1,3",
                 org_id="1",
                 project_id="1")
session.add(fg1)
session.commit()


print ("Added test elements!")
