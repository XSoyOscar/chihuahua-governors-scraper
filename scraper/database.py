import sqlite3
import logging


class GovernorDatabase:
    def __init__(self, db_name="governors.db"):
        logging.info(f"Connecting to database {db_name}")
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS governors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    wikipedia_link TEXT,
                    birth_date TEXT,
                    death_date TEXT,
                    occupation TEXT,
                    nationality TEXT,
                    UNIQUE(name, wikipedia_link) ON CONFLICT IGNORE
                )
            """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS governor_periods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    governor_id INTEGER NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT,  -- Permitir NULL aquí
                    FOREIGN KEY(governor_id) REFERENCES governors(id),
                    UNIQUE(governor_id, start_date, end_date) ON CONFLICT IGNORE
                )
            """
            )
        logging.info("Tables created or verified successfully")

    def insert_governor(
        self,
        name,
        wikipedia_link,
        birth_date=None,
        death_date=None,
        occupation=None,
        nationality=None,
    ):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO governors (name, wikipedia_link, birth_date, death_date, occupation, nationality)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (name, wikipedia_link, birth_date, death_date, occupation, nationality),
            )
            logging.info(f"Governor inserted: {name}")
            return cursor.lastrowid

    def insert_governor_period(self, governor_id, start_date, end_date):
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO governor_periods (governor_id, start_date, end_date)
                VALUES (?, ?, ?)
            """,
                (governor_id, start_date, end_date),
            )
        logging.info(f"Period inserted for governor ID {governor_id}")

    def governor_exists(self, name, wikipedia_link):
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) FROM governors 
            WHERE name = ? AND COALESCE(wikipedia_link, '') = COALESCE(?, '')
            """,
            (name, wikipedia_link),
        )

        exists = cursor.fetchone()[0] > 0
        logging.info(f"Governor exists: {exists} - {name}")
        return exists

    def fetch_all_governors(self):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT * FROM governors
            """
            )
            governors = cursor.fetchall()
            logging.info(f"Fetched all governors: {len(governors)} records")
            return governors

    def fetch_governor_periods(self, governor_id):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT * FROM governor_periods
                WHERE governor_id = ?
            """,
                (governor_id,),
            )
            periods = cursor.fetchall()
            logging.info(
                f"Fetched periods for governor ID {governor_id}: {len(periods)} records"
            )
            return periods


if __name__ == "__main__":
    db = GovernorDatabase()
    governor_id = db.insert_governor(
        "Test Governor", "https://en.wikipedia.org/wiki/Test", nationality="American"
    )
    db.insert_governor_period(governor_id, "2000-01-01", "2004-12-31")
    print(db.fetch_all_governors())
    print(db.fetch_governor_periods(governor_id))
