"""Database models and connection for SQLite."""

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from datetime import datetime
import os

Base = declarative_base()


class Section(Base):
    """Section model for organizing APIs."""
    __tablename__ = 'sections'

    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    order = Column(Integer, default=0)

    # Relationships
    apis = relationship('API', back_populates='section', cascade='all, delete-orphan')


class API(Base):
    """API model for storing API test configurations."""
    __tablename__ = 'apis'

    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    section_id = Column(String(50), ForeignKey('sections.id', ondelete='CASCADE'), nullable=False)
    curl = Column(Text)  # Original cURL command
    method = Column(String(10), nullable=False)
    url = Column(Text, nullable=False)
    headers = Column(JSON)
    body = Column(Text)
    verify_ssl = Column(Boolean, default=True)
    custom_rules = Column(JSON)  # Custom validation rules
    extract_rules = Column(JSON)  # Extraction rules
    last_status = Column(String(20))  # Last test status
    last_result = Column(JSON)  # Last test result
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    order = Column(Integer, default=0)

    # Relationships
    section = relationship('Section', back_populates='apis')
    rules = relationship('Rule', back_populates='api', cascade='all, delete-orphan')


class Rule(Base):
    """Rule model for API validation rules."""
    __tablename__ = 'rules'

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_id = Column(String(50), ForeignKey('apis.id', ondelete='CASCADE'), nullable=False)
    rule_type = Column(String(50), nullable=False)
    field_path = Column(String(500))
    expected_value = Column(Text)
    operator = Column(String(20))
    config = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    api = relationship('API', back_populates='rules')


class Variable(Base):
    """Variable model for storing reusable variables."""
    __tablename__ = 'variables'

    id = Column(String(50), primary_key=True)
    name = Column(String(200), unique=True, nullable=False)
    value = Column(Text)
    type = Column(String(20), default='string')
    description = Column(Text)
    source_api_id = Column(String(50))
    source_field_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Report(Base):
    """Report model for storing test execution reports."""
    __tablename__ = 'reports'

    id = Column(String(50), primary_key=True)
    module = Column(String(200))
    total_apis = Column(Integer, default=0)  # Number of APIs tested
    total_rules = Column(Integer, default=0)  # Number of rules tested
    passed = Column(Integer, default=0)  # Rules passed
    failed = Column(Integer, default=0)  # Rules failed
    total_duration = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    html_path = Column(String(500))
    json_path = Column(String(500))
    status = Column(String(20), default='completed')
    error = Column(Text)

    # Relationships
    results = relationship('TestResult', back_populates='report', cascade='all, delete-orphan')


class TestResult(Base):
    """Individual test result within a report."""
    __tablename__ = 'test_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(String(50), ForeignKey('reports.id', ondelete='CASCADE'), nullable=False)
    api_id = Column(String(50))
    api_name = Column(String(200))
    status = Column(String(20))
    response_time = Column(Float)
    status_code = Column(Integer)
    error_message = Column(Text)
    rule_results = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    report = relationship('Report', back_populates='results')


# Database setup
def get_database_path():
    """Get the database file path."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'database.db')


def get_engine():
    """Create and return database engine."""
    db_path = get_database_path()
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    return engine


def init_db():
    """Initialize database and create all tables."""
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """Get a new database session."""
    engine = get_engine()
    Session = scoped_session(sessionmaker(bind=engine))
    return Session()


def close_session(session):
    """Close a database session."""
    try:
        session.close()
    except Exception:
        pass
