import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import aiosqlite
from backend.config import settings
from backend.db.models import UserProfile, ConversationMessage

class Database:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db_sync()

    def _init_db_sync(self):
        """Initialize the database tables synchronously on startup."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User Profiles Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            session_id TEXT PRIMARY KEY,
            name TEXT,
            age INTEGER,
            income INTEGER,
            category TEXT,
            gender TEXT,
            occupation TEXT,
            farmer_type TEXT,
            housing_status TEXT,
            student_class INTEGER,
            district TEXT,
            education TEXT,
            marital_status TEXT,
            has_bpl_card BOOLEAN,
            disabilities_json TEXT,
            scheme_interest TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Conversations Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES user_profiles(session_id)
        )
        ''')
        
        conn.commit()
        conn.close()

    async def get_profile(self, session_id: str) -> Optional[UserProfile]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM user_profiles WHERE session_id = ?", (session_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    data = dict(row)
                    # Convert JSON back to list
                    if data.get('disabilities_json'):
                        data['disabilities'] = json.loads(data['disabilities_json'])
                    del data['disabilities_json']
                    del data['created_at']
                    del data['updated_at']
                    return UserProfile(**data)
        return UserProfile(session_id=session_id) # Return empty if not found

    async def save_profile(self, profile: UserProfile):
        async with aiosqlite.connect(self.db_path) as db:
            disabilities_json = json.dumps(profile.disabilities)
            await db.execute('''
                INSERT INTO user_profiles 
                (session_id, name, age, income, category, gender, occupation, farmer_type, housing_status, student_class, district, education, marital_status, has_bpl_card, scheme_interest, disabilities_json, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(session_id) DO UPDATE SET
                name=excluded.name,
                age=excluded.age,
                income=excluded.income,
                category=excluded.category,
                gender=excluded.gender,
                occupation=excluded.occupation,
                farmer_type=excluded.farmer_type,
                housing_status=excluded.housing_status,
                student_class=excluded.student_class,
                district=excluded.district,
                education=excluded.education,
                marital_status=excluded.marital_status,
                has_bpl_card=excluded.has_bpl_card,
                scheme_interest=excluded.scheme_interest,
                disabilities_json=excluded.disabilities_json,
                updated_at=CURRENT_TIMESTAMP
            ''', (
                profile.session_id, profile.name, profile.age, profile.income, profile.category, 
                profile.gender, profile.occupation, profile.farmer_type, profile.housing_status,
                profile.student_class, profile.district, profile.education, 
                profile.marital_status, profile.has_bpl_card, profile.scheme_interest, disabilities_json
            ))
            await db.commit()

    async def add_message(self, session_id: str, role: str, content: str):
        async with aiosqlite.connect(self.db_path) as db:
            # Ensure profile exists
            await db.execute("INSERT OR IGNORE INTO user_profiles (session_id) VALUES (?)", (session_id,))
            
            await db.execute('''
                INSERT INTO conversations (session_id, role, content)
                VALUES (?, ?, ?)
            ''', (session_id, role, content))
            await db.commit()

    async def get_chat_history(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        history = []
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            # Get latest limit messages, ordered chronologically
            query = '''
                SELECT role, content FROM (
                    SELECT role, content, timestamp, id 
                    FROM conversations 
                    WHERE session_id = ? 
                    ORDER BY id DESC LIMIT ?
                ) ORDER BY id ASC
            '''
            async with db.execute(query, (session_id, limit)) as cursor:
                async for row in cursor:
                    history.append({"role": row['role'], "content": row['content']})
        return history

# Global async DB instance
db_client = Database(settings.DB_PATH)
