from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


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


class Project(Base):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    description = Column(String(500))
    stage = Column(String(100))
    org_id = Column(Integer, ForeignKey('org.id'))
    org = relationship(Org)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'stage': self.stage,
            'org_id': self.org_id
        }


class Role(Base):
    __tablename__ = 'role'
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


class Screen(Base):
    __tablename__ = 'screen'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    description = Column(String(500))
    authRequired = Column(String(5))
    roles = Column(String(500))
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
            'roles': self.roles,
            'org_id': self.org_id,
            'project_id': self.project_id
        }


class Function(Base):
    __tablename__ = 'function'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    description = Column(String(500))
    authRequired = Column(String(5))
    roles = Column(String(500))
    screens = Column(String(500))
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
            'roles': self.roles,
            'screens': self.screens,
            'org_id': self.org_id,
            'project_id': self.project_id,
            'fg_id': self.functgroup.id
        }


class Functgroup(Base):
    __tablename__ = 'functgroup'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    description = Column(String(500))
    functions = Column(String(100))
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
            'functions': self.roles,
            'org_id': self.org_id,
            'project_id': self.project_id
        }


engine = create_engine('sqlite:///project-map-tool.db')
Base.metadata.create_all(engine)
