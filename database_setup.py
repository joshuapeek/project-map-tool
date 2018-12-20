from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


# MVP table 1
class Org(Base):
    __tablename__ = 'org'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    description = Column(String(500))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description
        }


# MVP table 2
class Project(Base):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    description = Column(String(500))
    org_id = Column(Integer, ForeignKey('org.id'))
    org = relationship(Org)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'org_id': self.org_id
        }


# MVP table 3
class Role(Base):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    description = Column(String(500))
    authRequired = Column(String(5))
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'authRequired': self.authRequired,
            'project_id': self.project_id
        }


# MVP table 4
class Screen(Base):
    __tablename__ = 'screen'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    description = Column(String(500))
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'project_id': self.project_id
        }


# MVP table 5
class Action(Base):
    __tablename__ = 'action'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    description = Column(String(500))
    screen_id = Column(Integer, ForeignKey('screen.id'))
    screen = relationship(Screen)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'screen_id': self.screen_id,
            'project_id': self.project_id
        }


# MVP table 6
class Story(Base):
    __tablename__ = 'story'
    id = Column(Integer, primary_key=True)
    title = Column(String(250))
    expectation = Column(String(500), nullable=False)
    action = Column(String(50), nullable=False)
    hook = Column(String(10), nullable=False)
    hookID = Column(Integer, nullable=False)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project)
    screen_id = Column(Integer, ForeignKey('screen.id'))
    screen = relationship(Screen)
    role_id = Column(Integer, ForeignKey('role.id'))
    role = relationship(Role)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'expectation': self.description,
            'action': self.action,
            'hook': self.hook,
            'hookID': self.hookID,
            'project_id': self.project_id,
            'screen_id': self.screen_id,
            'role_id': self.role_id
        }


# MVP table 7
class Section(Base):
    __tablename__ = 'section'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    description = Column(String(500))
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'project_id': self.project_id,
        }


# MVP table 8
class Element(Base):
    __tablename__ = 'element'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    description = Column(String(500))
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'project_id': self.project_id
        }


# MVP table 9
class RoleScreen(Base):
    __tablename__ = 'rolescreen'
    id = Column(Integer, primary_key=True)
    access = Column(String(1), nullable=False)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=False)
    role = relationship(Role)
    screen_id = Column(Integer, ForeignKey('screen.id'), nullable=False)
    screen = relationship(Screen)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'access': self.access,
            'project_id': self.project_id,
            'role_id': self.role_id,
            'screen_id': self.screen_id
        }


# MVP table 10
class RoleSection(Base):
    __tablename__ = 'rolesection'
    id = Column(Integer, primary_key=True)
    access = Column(String(1), nullable=False)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=False)
    role = relationship(Role)
    section_id = Column(Integer, ForeignKey('section.id'), nullable=False)
    screen = relationship(Section)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'access': self.access,
            'project_id': self.project_id,
            'role_id': self.role_id,
            'section_id': self.section_id
        }


# MVP table 11 - MIGHT NOT NEED THIS
class StoryScreen(Base):
    __tablename__ = 'storyscreen'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project)
    story_id = Column(Integer, ForeignKey('story.id'), nullable=False)
    story = relationship(Story)
    screen_id = Column(Integer, ForeignKey('screen.id'), nullable=False)
    screen = relationship(Screen)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'story_id': self.story_id,
            'screen_id': self.screen_id
        }


# MVP table 12
class user(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    firstname = Column(String(100))
    lastname = Column(String(100))
    email = Column(String(250))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'email': self.email
        }


# MVP table 13
class userProject(Base):
    __tablename__ = 'userproject'
    id = Column(Integer, primary_key=True)
    access = Column(String(1), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(user)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'access': self.access,
            'user_id': self.user_id,
            'project_id': self.project_id
        }


# MVP table 14
class userOrg(Base):
    __tablename__ = 'userorg'
    id = Column(Integer, primary_key=True)
    access = Column(String(1), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(user)
    org_id = Column(Integer, ForeignKey('org.id'))
    org = relationship(Org)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'access': self.access,
            'user_id': self.user_id,
            'org_id': self.project_id
        }


# MVP table 15
class super(Base):
    __tablename__ = 'super'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(user)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'access': self.access,
            'user_id': self.user_id,
            'org_id': self.project_id
        }


# MVP table 16
class ScreenSection(Base):
    __tablename__ = 'screensection'
    id = Column(Integer, primary_key=True)
    screen_id = Column(Integer, ForeignKey('screen.id'))
    screen = relationship(Screen)
    section_id = Column(Integer, ForeignKey('section.id'))
    section = relationship(Section)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'screen_id': self.screen_id,
            'section_id': self.section_id
        }


# MVP table 17
class SectionElement(Base):
    __tablename__ = 'sectionelement'
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey('section.id'))
    section = relationship(Section)
    element_id = Column(Integer, ForeignKey('element.id'))
    element = relationship(Element)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'section_id': self.section_id,
            'element_id': self.element_id,
            'project_id': self.project_id
        }


# Original Build Table
class Function(Base):
    __tablename__ = 'function'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    description = Column(String(500))
    authRequired = Column(String(5))
    org_id = Column(Integer, ForeignKey('org.id'))
    org = relationship(Org)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'authRequired': self.authRequired,
            'org_id': self.org_id,
            'project_id': self.project_id
        }


# Original Build Table
class FunctScreen(Base):
    __tablename__ = 'functscreen'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project)
    function_id = Column(Integer, ForeignKey('function.id'))
    function = relationship(Function)
    screen_id = Column(Integer, ForeignKey('screen.id'))
    screen = relationship(Screen)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'function_id': self.function_id,
            'screen_id': self.screen_id
        }


# Original Build Table
class FunctRole(Base):
    __tablename__ = 'functrole'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project)
    function_id = Column(Integer, ForeignKey('function.id'))
    function = relationship(Function)
    role_id = Column(Integer, ForeignKey('role.id'))
    role = relationship(Role)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'function_id': self.function_id,
            'role_id': self.role_id
        }


# Original Build Table
class ScreenRole(Base):
    __tablename__ = 'screenrole'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project)
    screen_id = Column(Integer, ForeignKey('screen.id'))
    screen = relationship(Screen)
    role_id = Column(Integer, ForeignKey('role.id'))
    role = relationship(Role)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'screen_id': self.screen_id,
            'role_id': self.role_id
        }


# Original Build Table
class Functgroup(Base):
    __tablename__ = 'functgroup'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    description = Column(String(500))
    org_id = Column(Integer, ForeignKey('org.id'))
    org = relationship(Org)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project)
    function_id = Column(Integer, ForeignKey('function.id'))
    function = relationship(Function)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'org_id': self.org_id,
            'project_id': self.project_id,
            'function_id': self.function_id
        }


# Original Build Table
class Screengroup(Base):
    __tablename__ = 'screengroup'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    description = Column(String(500))
    authRequired = Column(String(5))
    org_id = Column(Integer, ForeignKey('org.id'))
    org = relationship(Org)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project)
    screen_id = Column(Integer, ForeignKey('screen.id'))
    screen = relationship(Screen)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'authRequired': self.authRequired,
            'org_id': self.org_id,
            'project_id': self.project_id,
            'screen_id':self.screen_id
        }


engine = create_engine('sqlite:///project-map-tool.db')
Base.metadata.create_all(engine)
