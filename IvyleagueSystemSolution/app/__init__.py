import psycopg2
from flask import Flask
from .models import db, Base, migrate
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from sqlalchemy import create_engine, text


def create_postgres_db_if_not_exists(db_name, user, password, host="localhost", port=5432):
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(dbname='postgres', user=user, password=password, host=host, port=port)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        cur = conn.cursor()
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}';")
        exists = cur.fetchone()

        if not exists:
            cur.execute(f"CREATE DATABASE {db_name};")
            print(f"✅ Database '{db_name}' created.")
        else:
            print(f"⚠️ Database '{db_name}' already exists.")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Failed to create database: {e}")


engine = create_engine("postgresql://postgres:root@localhost:5432/ivyleague")  # Replace with your actual URL

def reset_database():
    with engine.connect() as conn:
        trans = conn.begin()

        try:
            # Get all table names (except protected ones)
            result = conn.execute(text("""
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public'
                AND tablename NOT IN ('your_core_table1', 'your_core_table2')
            """))
            tables = [row[0] for row in result]

            for table in tables:
                conn.execute(text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE;'))

            trans.commit()
        except Exception as e:
            trans.rollback()
            raise e

    # Recreate any missing tables
    Base.metadata.create_all(engine)


def create_app():

    create_postgres_db_if_not_exists("ivyleague", "postgres", "root")
    # reset_database()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/ivyleague'

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # db.drop_all() # For development purposes
        db.create_all()

    # Import and register routes
    from app.routes import register_routes
    register_routes(app)

    from flask_cors import CORS

    CORS(app, resources={r"/*": {
        "origins": "*",  # Or specify your frontend domain
        "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }})  # Use specific origin instead of "*" in production

    return app
