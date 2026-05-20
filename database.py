import sqlite3
import json
import pandas as pd
from datetime import datetime
import streamlit as st

class Database:
    def __init__(self, db_path="codescan.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
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
        """Save a scan result to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scans (
                timestamp, code_a_name, code_b_name, language,
                score, verdict, risk, engines_used,
                type_agnostic_seq_sim, type_agnostic_jac_sim, ted_sim, cfg_sim,
                winnowing_sim, codebert_sim, bytecode_sim, big_o_match,
                ast_sim, seq_sim, jac_sim, ngram_sim,
                code_a_preview, code_b_preview
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            result.get('timestamp', datetime.now().isoformat()),
            code_a_name, code_b_name,
            st.session_state['settings'].get('language', 'Python'),
            result.get('score', 0),
            result.get('verdict', 'UNKNOWN'),
            result.get('risk', 'Low'),
            result.get('engines_used', 0),
            result.get('type_agnostic_seq_sim', 0),
            result.get('type_agnostic_jac_sim', 0),
            result.get('ted_sim', 0),
            result.get('cfg_sim', 0),
            result.get('winnowing_sim', 0),
            result.get('codebert_sim', 0),
            result.get('bytecode_sim', 0),
            result.get('big_o_match', 0),
            result.get('ast_sim', 0),
            result.get('seq_sim', 0),
            result.get('jac_sim', 0),
            result.get('ngram_sim', 0),
            code_a[:200] if code_a else "",
            code_b[:200] if code_b else ""
        ))
        
        conn.commit()
        conn.close()
    
    def get_all_scans(self):
        """Get all scan history"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM scans ORDER BY timestamp DESC", conn)
        conn.close()
        return df
    
    def get_scan_by_id(self, scan_id: int):
        """Get a specific scan by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def delete_scan(self, scan_id: int):
        """Delete a scan by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
        conn.commit()
        conn.close()
    
    def clear_history(self):
        """Clear all scan history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM scans")
        conn.commit()
        conn.close()
    
    def save_training_example(self, features: dict, label: str):
        """Save training example"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO training_data (timestamp, features, label)
            VALUES (?, ?, ?)
        ''', (datetime.now().isoformat(), json.dumps(features), label))
        conn.commit()
        conn.close()
    
    def get_training_data(self):
        """Get all training data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT features, label FROM training_data")
        results = cursor.fetchall()
        conn.close()
        return [(json.loads(features), label) for features, label in results]
    
    def save_setting(self, key: str, value: str):
        """Save a setting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value)
            VALUES (?, ?)
        ''', (key, value))
        conn.commit()
        conn.close()
    
    def get_setting(self, key: str, default: str = None):
        """Get a setting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else default
    
    def get_statistics(self):
        """Get scan statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM scans")
        total_scans = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM scans WHERE verdict = 'PLAGIARIZED'")
        plagiarized = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(score) FROM scans")
        avg_score = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_scans': total_scans,
            'plagiarized': plagiarized,
            'original': total_scans - plagiarized,
            'avg_score': round(avg_score, 2)
        }


# Global database instance
db = Database()