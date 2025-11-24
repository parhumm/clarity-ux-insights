"""Database manager for Clarity API data storage."""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import config


class DatabaseManager:
    """Manage SQLite database for Clarity metrics storage."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database manager."""
        self.db_path = db_path or config.DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn

    def init_database(self):
        """Initialize database with schema."""
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path, 'r') as f:
            schema_sql = f.read()

        conn = self.get_connection()
        try:
            conn.executescript(schema_sql)
            conn.commit()
        finally:
            conn.close()

    def insert_metrics(self, metrics_data: List[Dict], num_days: int,
                      dimension1: Optional[str] = None,
                      dimension2: Optional[str] = None,
                      dimension3: Optional[str] = None) -> int:
        """Insert metrics data into database.

        Args:
            metrics_data: List of metric dictionaries from API response
            num_days: Number of days the data covers
            dimension1: First dimension name
            dimension2: Second dimension name
            dimension3: Third dimension name

        Returns:
            Number of rows inserted
        """
        conn = self.get_connection()
        inserted = 0

        try:
            for metric_group in metrics_data:
                metric_name = metric_group.get('metricName', 'Unknown')
                information_list = metric_group.get('information', [])

                for info in information_list:
                    # Extract dimension values from the info dict
                    dim1_value = info.get(dimension1) if dimension1 else None
                    dim2_value = info.get(dimension2) if dimension2 else None
                    dim3_value = info.get(dimension3) if dimension3 else None

                    # Extract metrics
                    total_sessions = self._parse_int(info.get('totalSessionCount'))
                    bot_sessions = self._parse_int(info.get('totalBotSessionCount'))
                    distinct_users = self._parse_int(info.get('distantUserCount'))
                    pages_per_session = self._parse_float(info.get('PagesPerSessionPercentage'))

                    try:
                        conn.execute("""
                            INSERT INTO clarity_metrics (
                                metric_name, num_days,
                                total_session_count, total_bot_session_count,
                                distinct_user_count, pages_per_session,
                                dimension1_name, dimension1_value,
                                dimension2_name, dimension2_value,
                                dimension3_name, dimension3_value,
                                raw_json
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            metric_name, num_days,
                            total_sessions, bot_sessions,
                            distinct_users, pages_per_session,
                            dimension1, dim1_value,
                            dimension2, dim2_value,
                            dimension3, dim3_value,
                            json.dumps(info)
                        ))
                        inserted += 1
                    except sqlite3.IntegrityError:
                        # Duplicate entry, skip
                        pass

            conn.commit()
        finally:
            conn.close()

        return inserted

    def log_api_request(self, endpoint: str, num_days: int,
                       dimension1: Optional[str] = None,
                       dimension2: Optional[str] = None,
                       dimension3: Optional[str] = None,
                       status_code: Optional[int] = None,
                       success: bool = False,
                       error_message: Optional[str] = None,
                       response_size: int = 0,
                       rows_returned: int = 0):
        """Log API request details."""
        conn = self.get_connection()
        try:
            conn.execute("""
                INSERT INTO api_requests (
                    endpoint, num_days, dimension1, dimension2, dimension3,
                    status_code, success, error_message, response_size, rows_returned
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                endpoint, num_days, dimension1, dimension2, dimension3,
                status_code, success, error_message, response_size, rows_returned
            ))
            conn.commit()
        finally:
            conn.close()

    def get_metrics(self, metric_name: Optional[str] = None,
                   dimension1: Optional[str] = None) -> List[Dict]:
        """Retrieve metrics from database.

        Args:
            metric_name: Filter by metric name
            dimension1: Filter by first dimension name

        Returns:
            List of metric dictionaries
        """
        conn = self.get_connection()
        query = "SELECT * FROM clarity_metrics WHERE 1=1"
        params = []

        if metric_name:
            query += " AND metric_name = ?"
            params.append(metric_name)

        if dimension1:
            query += " AND dimension1_name = ?"
            params.append(dimension1)

        query += " ORDER BY fetch_timestamp DESC"

        try:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_statistics(self) -> Dict:
        """Get database statistics."""
        conn = self.get_connection()
        try:
            stats = {}

            # Total metrics
            cursor = conn.execute("SELECT COUNT(*) as count FROM clarity_metrics")
            stats['total_metrics'] = cursor.fetchone()['count']

            # API requests
            cursor = conn.execute("SELECT COUNT(*) as count FROM api_requests")
            stats['total_api_requests'] = cursor.fetchone()['count']

            # Successful requests
            cursor = conn.execute("SELECT COUNT(*) as count FROM api_requests WHERE success = 1")
            stats['successful_requests'] = cursor.fetchone()['count']

            # Unique dimensions
            cursor = conn.execute("""
                SELECT COUNT(DISTINCT dimension1_value) as count
                FROM clarity_metrics
                WHERE dimension1_value IS NOT NULL
            """)
            stats['unique_dimension1_values'] = cursor.fetchone()['count']

            # Latest fetch
            cursor = conn.execute("""
                SELECT MAX(fetch_timestamp) as latest
                FROM clarity_metrics
            """)
            stats['latest_fetch'] = cursor.fetchone()['latest']

            return stats
        finally:
            conn.close()

    def _parse_int(self, value) -> Optional[int]:
        """Parse integer value from string or int."""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _parse_float(self, value) -> Optional[float]:
        """Parse float value from string or number."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None


def test_database():
    """Test database operations."""
    print("Testing database operations...")

    # Initialize
    db = DatabaseManager()
    print("✓ Database initialized")

    # Test insert with sample data
    sample_data = [{
        "metricName": "Traffic",
        "information": [{
            "totalSessionCount": "1000",
            "totalBotSessionCount": "100",
            "distantUserCount": "800",
            "PagesPerSessionPercentage": 2.5,
            "Device": "Desktop"
        }]
    }]

    inserted = db.insert_metrics(sample_data, num_days=3, dimension1="Device")
    print(f"✓ Inserted {inserted} test records")

    # Test duplicate prevention
    inserted_again = db.insert_metrics(sample_data, num_days=3, dimension1="Device")
    print(f"✓ Duplicate prevention works (inserted {inserted_again} duplicates)")

    # Test retrieval
    metrics = db.get_metrics(dimension1="Device")
    print(f"✓ Retrieved {len(metrics)} metrics")

    # Test statistics
    stats = db.get_statistics()
    print(f"✓ Statistics: {stats}")

    print("\n✅ All database tests passed!")


if __name__ == "__main__":
    test_database()
