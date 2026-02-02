from crea_dades import engine
from models import User, Base
from sqlalchemy import text, inspect
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)

def update_db():
    print("Updating database schema...")
    
    # Check if table 'pissarra_users' exists
    inspector = inspect(engine)
    if 'pissarra_users' not in inspector.get_table_names():
        print("Creating 'pissarra_users' table...")
        Base.metadata.create_all(engine)
    else:
        print("'pissarra_users' table already exists.")

    # Check if 'role' column exists in 'users'
    with engine.connect() as conn:
        try:
            conn.execute(text("SELECT role FROM users LIMIT 1"))
            print("'role' column already exists.")
        except Exception:
            print("Adding 'role' column to users table...")
            try:
                # Add check for SQLite vs PostgreSQL syntax if needed, but assuming simple ALTER works
                conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user' NOT NULL"))
                conn.commit()
                print("'role' column added.")
            except Exception as e:
                print(f"Error adding column: {e}")

    # Check if 'is_public' column exists in 'pissarres'
    with engine.connect() as conn:
        try:
            conn.execute(text("SELECT is_public FROM pissarres LIMIT 1"))
            print("'is_public' column already exists.")
        except Exception:
            print("Adding 'is_public' column to pissarres table...")
            try:
                conn.execute(text("ALTER TABLE pissarres ADD COLUMN is_public BOOLEAN DEFAULT 0 NOT NULL"))
                conn.commit()
                print("'is_public' column added.")
            except Exception as e:
                print(f"Error adding column: {e}")

    # Set admins
    sess = Session()
    admins = ['roma']  # Only roma is admin now
    for username in admins:
        user = sess.query(User).filter_by(username=username).first()
        if user:
            user.role = 'admin'
            print(f"Set role 'admin' for user {username}")
        else:
            print(f"User {username} not found. Creating as admin...")
            user = User(username=username, role='admin')
            user.set_password('1234') 
            sess.add(user)
            print(f"Created user {username}")
    
    sess.commit()
    sess.close()
    print("Database update complete.")

if __name__ == "__main__":
    update_db()
