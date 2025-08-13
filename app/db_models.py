# backend/app/db_models.py

from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, TIMESTAMP, Boolean, Float, Date, DECIMAL
from sqlalchemy.orm import relationship
from .database import Base


# --- Modelos de Asociación (Tablas Intermedias) ---

class CourseEnrollment(Base):
    __tablename__ = 'course_enrollments'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), primary_key=True)
    enrollment_date = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP')
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

class LearningPathCourse(Base):
    __tablename__ = 'learning_path_courses'
    path_id = Column(Integer, ForeignKey('learning_paths.id'), primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), primary_key=True)
    step = Column(Integer, nullable=False)
    path = relationship("LearningPath", back_populates="courses")
    course = relationship("Course")


# --- Modelos Principales ---

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(255), unique=True, index=True, nullable=True)

    # --- RELACIONES CORREGIDAS ---
    role = relationship("Role", back_populates="users")
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    courses_taught = relationship("Course", back_populates="instructor", foreign_keys="[Course.instructor_id]")
    courses_created = relationship("Course", back_populates="creator", foreign_keys="[Course.creator_id]")
    enrollments = relationship("CourseEnrollment", back_populates="user", cascade="all, delete-orphan")
    progress = relationship("StudentProgress", back_populates="user", cascade="all, delete-orphan")
    last_login = Column(TIMESTAMP, nullable=True)

    @property
    def enrolled_courses(self):
        return [enrollment.course for enrollment in self.enrollments]

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    users = relationship("User", back_populates="role")  # <-- Relación añadida


class UserProfile(Base):
    __tablename__ = "user_profiles"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    document_type = Column(String(50), nullable=True)
    document_country = Column(String(100), nullable=True)
    document_number = Column(String(50), nullable=True)
    birth_date = Column(Date, nullable=True)
    phone_country_code = Column(String(10), nullable=True)
    phone_number = Column(String(50), nullable=True)
    user = relationship("User", back_populates="profile")


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    courses = relationship("Course", back_populates="category")


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    level = Column(Enum('basico', 'intermedio', 'avanzado'), nullable=False)
    status = Column(Enum('published', 'draft'), nullable=False, server_default='published')
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    visibility = Column(Enum('public', 'private'), nullable=False, server_default='private')
    price = Column(DECIMAL(10, 2), default=0.00)  # Asegúrate que también esté aquí

    # --- COLUMNA AÑADIDA ---
    is_free = Column(Boolean, nullable=False, default=True)

    instructor = relationship("User", back_populates="courses_taught", foreign_keys=[instructor_id])
    creator = relationship("User", back_populates="courses_created", foreign_keys=[creator_id])
    category = relationship("Category", back_populates="courses")
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("CourseEnrollment", back_populates="course", cascade="all, delete-orphan")




    @property
    def enrolled_students(self):
        return [enrollment.user for enrollment in self.enrollments]

class Module(Base):
    __tablename__ = "modules"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False)
    content_data = Column(Text, nullable=True)

    # Relaciones
    course = relationship("Course", back_populates="modules")
    progress = relationship("StudentProgress", back_populates="module", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="module", cascade="all, delete-orphan")


class StudentProgress(Base):
    __tablename__ = "student_progress"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    status = Column(Enum('not_started', 'in_progress', 'completed'), nullable=False, default='not_started')

    user = relationship("User", back_populates="progress")
    module = relationship("Module", back_populates="progress")


class LearningPath(Base):
    __tablename__ = "learning_paths"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    courses = relationship("LearningPathCourse", back_populates="path", cascade="all, delete-orphan")


# --- Modelos de Quiz ---
class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")
    module = relationship("Module", back_populates="questions")


class Option(Base):
    __tablename__ = "options"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    option_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)
    question = relationship("Question", back_populates="options")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    score = Column(Float, nullable=False)
    passed = Column(Boolean, nullable=False)
    submitted_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP')
    user = relationship("User")
    module = relationship("Module")


class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    join_code = Column(String(10), unique=True)

    instructor = relationship("User")
    members = relationship("User", secondary="room_members")
    courses = relationship("Course", secondary="room_courses")


class RoomMember(Base):
    __tablename__ = "room_members"
    room_id = Column(Integer, ForeignKey("rooms.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)


class RoomCourse(Base):
    __tablename__ = "room_courses"
    room_id = Column(Integer, ForeignKey("rooms.id"), primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    link_url = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP')

    user = relationship("User")


class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    plan_name = Column(String(100), nullable=False)
    start_date = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP')
    end_date = Column(TIMESTAMP, nullable=True)

    user = relationship("User")