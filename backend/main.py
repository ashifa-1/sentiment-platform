from models.database import init_db
import time

def main():
    init_db()
    print("✅ Database initialized successfully")
    print("🚀 Backend service running...")

    # Keep container alive
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
from models.database import init_db

if __name__ == "__main__":
    init_db()
    print("✅ Database initialized successfully")
