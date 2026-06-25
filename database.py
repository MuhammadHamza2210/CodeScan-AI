import os
import sqlite3
import json
import pandas as pd
from datetime import datetime
import streamlit as st


# ── Type coercion helpers ───────────────────────────────────────
# SQLite cannot bind numpy scalars (numpy.float32/float64/int64) and
# json.dumps cannot serialize them either. These helpers normalize any
# value to a native Python type so saves never raise binding errors.
def _num(value, default=0.0):
    """Coerce any value (numpy, bytes, str, None) to a native float."""
    try:
        if value is None:
            return default
        if isinstance(value, bool):
            return float(value)
        if isinstance(value, bytes):
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def _int(value, default=0):
    """Coerce any value to a native int."""
    try:
        if value is None:
            return default
        return int(float(value))
    except (ValueError, TypeError):
        return default


def _text(value, default=""):
    """Coerce any value to a native str."""
    if value is None:
        return default
    try:
        return str(value)
    except Exception:
        return default


def _json_safe(obj):
    """Recursively convert a structure into something json.dumps can handle."""
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, (int, float, str)) or obj is None:
        return obj
    # numpy scalars expose .item(); fall back to float/str
    if hasattr(obj, "item"):
        try:
            return obj.item()
        except Exception:
            pass
    try:
        return float(obj)
    except (ValueError, TypeError):
        return _text(obj)


class Database:
    def __init__(self, db_path="codescan.db"):
        # Store the DB next to this file so the CWD never affects where it lands.
        if not os.path.isabs(db_path):
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_path)
        self.db_path = db_path
        self.init_db()

    def _connect(self):
        """Open a connection that tolerates Streamlit's threading + brief locks."""
        return sqlite3.connect(self.db_path, timeout=30, check_same_thread=False)

    def init_db(self):
        """Initialize database tables"""
        conn = self._connect()
        cursor = conn.cursor()
        
        # Scans history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                code_a_name TEXT,
                code_b_name TEXT,
                language TEXT,
                score REAL,
                verdict TEXT,
                risk TEXT,
                engines_used INTEGER,
                type_agnostic_seq_sim REAL,
                type_agnostic_jac_sim REAL,
                ted_sim REAL,
                cfg_sim REAL,
                winnowing_sim REAL,
                codebert_sim REAL,
                bytecode_sim REAL,
                big_o_match REAL,
                ast_sim REAL,
                seq_sim REAL,
                jac_sim REAL,
                ngram_sim REAL,
                code_a_preview TEXT,
                code_b_preview TEXT
            )
        ''')
        
        # Training data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                features TEXT,
                label TEXT
            )
        ''')
        
        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_scan(self, result: dict, code_a: str = "", code_b: str = "",
                  code_a_name: str = "Snippet A", code_b_name: str = "Snippet B"):
        """Save a scan result to database. All values are coerced to native
        Python types first so numpy scalars never trigger binding errors."""
        try:
            language = st.session_state.get('settings', {}).get('language', 'Python')
        except Exception:
            language = 'Python'

        row = (
            _text(result.get('timestamp'), datetime.now().isoformat()),
            _text(code_a_name, "Snippet A"),
            _text(code_b_name, "Snippet B"),
            _text(language, "Python"),
            _num(result.get('score')),
            _text(result.get('verdict'), 'UNKNOWN'),
            _text(result.get('risk'), 'Low'),
            _int(result.get('engines_used')),
            _num(result.get('type_agnostic_seq_sim')),
            _num(result.get('type_agnostic_jac_sim')),
            _num(result.get('ted_sim')),
            _num(result.get('cfg_sim')),
            _num(result.get('winnowing_sim')),
            _num(result.get('codebert_sim')),
            _num(result.get('bytecode_sim')),
            _num(result.get('big_o_match')),
            _num(result.get('ast_sim')),
            _num(result.get('seq_sim')),
            _num(result.get('jac_sim')),
            _num(result.get('ngram_sim')),
            _text(code_a)[:200],
            _text(code_b)[:200],
        )

        conn = self._connect()
        try:
            conn.execute('''
                INSERT INTO scans (
                    timestamp, code_a_name, code_b_name, language,
                    score, verdict, risk, engines_used,
                    type_agnostic_seq_sim, type_agnostic_jac_sim, ted_sim, cfg_sim,
                    winnowing_sim, codebert_sim, bytecode_sim, big_o_match,
                    ast_sim, seq_sim, jac_sim, ngram_sim,
                    code_a_preview, code_b_preview
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', row)
            conn.commit()
        finally:
            conn.close()

    def get_all_scans(self):
        """Get all scan history"""
        conn = self._connect()
        try:
            df = pd.read_sql_query("SELECT * FROM scans ORDER BY id DESC", conn)
        finally:
            conn.close()
        return df

    def get_scan_by_id(self, scan_id: int):
        """Get a specific scan by ID"""
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scans WHERE id = ?", (_int(scan_id),))
            result = cursor.fetchone()
        finally:
            conn.close()
        return result

    def delete_scan(self, scan_id: int):
        """Delete a scan by ID"""
        conn = self._connect()
        try:
            conn.execute("DELETE FROM scans WHERE id = ?", (_int(scan_id),))
            conn.commit()
        finally:
            conn.close()

    def clear_history(self):
        """Clear all scan history"""
        conn = self._connect()
        try:
            conn.execute("DELETE FROM scans")
            conn.commit()
        finally:
            conn.close()

    def save_training_example(self, features: dict, label: str):
        """Save training example (features made JSON-safe first)."""
        conn = self._connect()
        try:
            conn.execute('''
                INSERT INTO training_data (timestamp, features, label)
                VALUES (?, ?, ?)
            ''', (datetime.now().isoformat(), json.dumps(_json_safe(features)), _text(label)))
            conn.commit()
        finally:
            conn.close()

    def get_training_data(self):
        """Get all training data"""
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT features, label FROM training_data")
            results = cursor.fetchall()
        finally:
            conn.close()
        out = []
        for features, label in results:
            try:
                out.append((json.loads(features), label))
            except (ValueError, TypeError):
                continue
        return out

    def save_setting(self, key: str, value: str):
        """Save a setting"""
        conn = self._connect()
        try:
            conn.execute('''
                INSERT OR REPLACE INTO settings (key, value)
                VALUES (?, ?)
            ''', (_text(key), _text(value)))
            conn.commit()
        finally:
            conn.close()

    def get_setting(self, key: str, default: str = None):
        """Get a setting"""
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (_text(key),))
            result = cursor.fetchone()
        finally:
            conn.close()
        return result[0] if result else default

    def get_statistics(self):
        """Get scan statistics"""
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM scans")
            total_scans = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM scans WHERE verdict = 'PLAGIARIZED'")
            plagiarized = cursor.fetchone()[0] or 0

            cursor.execute("SELECT AVG(score) FROM scans")
            avg_score = cursor.fetchone()[0] or 0
        finally:
            conn.close()

        return {
            'total_scans': total_scans,
            'plagiarized': plagiarized,
            'original': total_scans - plagiarized,
            'avg_score': round(avg_score, 2)
        }


# Global database instance
db = Database()