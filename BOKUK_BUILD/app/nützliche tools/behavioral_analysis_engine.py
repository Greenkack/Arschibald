#!/usr/bin/env python3
"""
🧐 BEHAVIORAL ANALYSIS ENGINE
=============================
Analysiert Benutzerverhalten und erkennt Anomalien
"""
import hashlib
import json
import sqlite3
import time
from collections import defaultdict
from datetime import datetime

import numpy as np


class BehavioralAnalysisEngine:

    def __init__(self, db_path="behavioral_analysis.db"):
        self.db_path = db_path
        self.init_database()
        self.behavioral_patterns = defaultdict(list)
        self.anomaly_threshold = 2.5  # Standard deviations

    def init_database(self):
        """Initialisiert Behavioral Analysis Database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                action_type TEXT,
                timestamp REAL,
                metadata TEXT,
                session_id TEXT,
                ip_hash TEXT,
                user_agent_hash TEXT,
                risk_score REAL DEFAULT 0.0
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS behavioral_profiles (
                user_id TEXT PRIMARY KEY,
                profile_data TEXT,
                last_updated REAL,
                anomaly_count INTEGER DEFAULT 0,
                trust_score REAL DEFAULT 1.0
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anomaly_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                anomaly_type TEXT,
                severity TEXT,
                description TEXT,
                timestamp REAL,
                resolved BOOLEAN DEFAULT 0
            )
        """)

        conn.commit()
        conn.close()

    def record_action(
            self,
            user_id: str,
            action_type: str,
            metadata: dict = None,
            session_id: str = None,
            ip_address: str = None,
            user_agent: str = None):
        """Zeichnet Benutzeraktion auf und analysiert sie"""

        timestamp = time.time()

        # Hashe sensitive Daten
        ip_hash = hashlib.sha256(
            ip_address.encode()).hexdigest()[
            :16] if ip_address else None
        user_agent_hash = hashlib.sha256(user_agent.encode()).hexdigest()[
            :16] if user_agent else None

        # Berechne Risk Score basierend auf Verhalten
        risk_score = self.calculate_risk_score(
            user_id, action_type, metadata, timestamp)

        # Speichere in Database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO user_actions
            (user_id, action_type, timestamp, metadata, session_id, ip_hash, user_agent_hash, risk_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, action_type, timestamp, json.dumps(metadata) if metadata else None,
              session_id, ip_hash, user_agent_hash, risk_score))

        conn.commit()
        conn.close()

        # Prüfe auf Anomalien
        self.detect_anomalies(user_id, action_type, timestamp, risk_score)

        return risk_score

    def calculate_risk_score(
            self,
            user_id: str,
            action_type: str,
            metadata: dict,
            timestamp: float) -> float:
        """Berechnet Risk Score basierend auf Behavioral Patterns"""

        risk_factors = []

        # 1. Zeit-basierte Anomalien
        time_risk = self.analyze_temporal_patterns(user_id, timestamp)
        risk_factors.append(time_risk)

        # 2. Frequenz-Anomalien
        frequency_risk = self.analyze_action_frequency(
            user_id, action_type, timestamp)
        risk_factors.append(frequency_risk)

        # 3. Sequenz-Anomalien
        sequence_risk = self.analyze_action_sequences(user_id, action_type)
        risk_factors.append(sequence_risk)

        # 4. Metadata-Anomalien
        if metadata:
            metadata_risk = self.analyze_metadata_patterns(user_id, metadata)
            risk_factors.append(metadata_risk)

        # Kombiniere Risk Factors (gewichteter Durchschnitt)
        weights = [0.3, 0.3, 0.2, 0.2][:len(risk_factors)]
        total_risk = sum(
            rf * w for rf,
            w in zip(
                risk_factors,
                weights,
                strict=False))

        return min(max(total_risk, 0.0), 10.0)  # Clamp zwischen 0-10

    def analyze_temporal_patterns(
            self,
            user_id: str,
            timestamp: float) -> float:
        """Analysiert zeitliche Verhaltensmuster"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Hole letzte Aktionen der letzten 7 Tage
        week_ago = timestamp - (7 * 24 * 3600)
        cursor.execute("""
            SELECT timestamp FROM user_actions
            WHERE user_id = ? AND timestamp > ?
            ORDER BY timestamp
        """, (user_id, week_ago))

        recent_times = [row[0] for row in cursor.fetchall()]
        conn.close()

        if len(recent_times) < 10:
            return 1.0  # Zu wenig Daten, mittleres Risiko

        # Analysiere Aktivitätsmuster
        hours = [(datetime.fromtimestamp(t).hour) for t in recent_times]
        hour_pattern = np.bincount(hours, minlength=24) / len(hours)

        current_hour = datetime.fromtimestamp(timestamp).hour
        expected_activity = hour_pattern[current_hour]

        # Anomalie wenn Aktivität zu ungewöhnlicher Zeit
        if expected_activity < 0.02:  # < 2% der normalen Aktivität
            return 8.0  # Hohes Risiko
        if expected_activity < 0.05:  # < 5%
            return 5.0  # Mittleres Risiko

        return 1.0  # Normales Risiko

    def analyze_action_frequency(
            self,
            user_id: str,
            action_type: str,
            timestamp: float) -> float:
        """Analysiert Aktionsfrequenz für Anomalien"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Aktionen der letzten Stunde
        hour_ago = timestamp - 3600
        cursor.execute("""
            SELECT COUNT(*) FROM user_actions
            WHERE user_id = ? AND action_type = ? AND timestamp > ?
        """, (user_id, action_type, hour_ago))

        recent_count = cursor.fetchone()[0]

        # Durchschnittliche Frequenz der letzten 30 Tage
        month_ago = timestamp - (30 * 24 * 3600)
        cursor.execute("""
            SELECT COUNT(*) FROM user_actions
            WHERE user_id = ? AND action_type = ? AND timestamp > ?
        """, (user_id, action_type, month_ago))

        monthly_count = cursor.fetchone()[0]
        conn.close()

        if monthly_count == 0:
            return 2.0  # Neue Aktion, mittleres Risiko

        # Erwartete Aktionen pro Stunde
        expected_hourly = monthly_count / (30 * 24)

        if recent_count > expected_hourly * 10:  # 10x mehr als normal
            return 9.0  # Sehr hohes Risiko (möglicher Bot-Angriff)
        if recent_count > expected_hourly * 5:  # 5x mehr
            return 6.0  # Hohes Risiko
        if recent_count > expected_hourly * 2:  # 2x mehr
            return 3.0  # Mittleres Risiko

        return 1.0  # Normales Risiko

    def analyze_action_sequences(
            self,
            user_id: str,
            current_action: str) -> float:
        """Analysiert Aktionssequenzen für ungewöhnliche Muster"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Hole letzte 10 Aktionen
        cursor.execute("""
            SELECT action_type FROM user_actions
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT 10
        """, (user_id,))

        recent_actions = [row[0] for row in cursor.fetchall()]
        conn.close()

        if len(recent_actions) < 3:
            return 1.0  # Zu wenig Daten

        # Prüfe auf verdächtige Muster
        sequence = recent_actions[:5]  # Letzte 5 Aktionen

        # 1. Repetitive Muster (Bot-Verhalten)
        if len(set(sequence)) == 1:  # Alle Aktionen identisch
            return 8.0  # Hohes Bot-Risiko

        # 2. Unlogische Sequenzen
        suspicious_sequences = [
            ['login', 'delete_account', 'login'],  # Verdächtig
            ['create_user', 'create_user', 'create_user'],  # Spam
            ['download_file'] * 5,  # Massen-Download
        ]

        for sus_seq in suspicious_sequences:
            if sequence[:len(sus_seq)] == sus_seq:
                return 7.0  # Verdächtige Sequenz

        return 1.0  # Normale Sequenz

    def analyze_metadata_patterns(self, user_id: str, metadata: dict) -> float:
        """Analysiert Metadata auf Anomalien"""

        risk_score = 1.0

        # Prüfe auf verdächtige Metadata-Werte
        if 'file_size' in metadata:
            file_size = metadata['file_size']
            if file_size > 100 * 1024 * 1024:  # > 100MB
                risk_score += 2.0  # Große Datei-Uploads verdächtig

        if 'request_count' in metadata:
            request_count = metadata['request_count']
            if request_count > 100:  # > 100 Requests
                risk_score += 3.0  # Möglicher API-Missbrauch

        if 'error_rate' in metadata:
            error_rate = metadata['error_rate']
            if error_rate > 0.5:  # > 50% Fehlerrate
                risk_score += 2.0  # Viele Fehler = verdächtig

        return min(risk_score, 10.0)

    def detect_anomalies(
            self,
            user_id: str,
            action_type: str,
            timestamp: float,
            risk_score: float):
        """Erkennt und meldet Anomalien"""

        if risk_score > 7.0:
            severity = "HIGH"
            description = f"High-risk {action_type} detected (score: {
                risk_score:.1f})"
        elif risk_score > 5.0:
            severity = "MEDIUM"
            description = f"Medium-risk {action_type} detected (score: {
                risk_score:.1f})"
        elif risk_score > 3.0:
            severity = "LOW"
            description = f"Low-risk {action_type} detected (score: {
                risk_score:.1f})"
        else:
            return  # Keine Anomalie

        # Speichere Anomalie-Alert
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO anomaly_alerts
            (user_id, anomaly_type, severity, description, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, action_type, severity, description, timestamp))

        conn.commit()
        conn.close()

        print(f"🚨 ANOMALIE ERKANNT: {description}")

        # Aktualisiere Benutzer-Trust-Score
        self.update_trust_score(user_id, risk_score)

    def update_trust_score(self, user_id: str, risk_score: float):
        """Aktualisiert Trust Score des Benutzers"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Lade aktuellen Trust Score
        cursor.execute(
            "SELECT trust_score, anomaly_count FROM behavioral_profiles WHERE user_id = ?",
            (user_id,
             ))
        result = cursor.fetchone()

        if result:
            current_trust, anomaly_count = result
            new_anomaly_count = anomaly_count + (1 if risk_score > 5.0 else 0)

            # Reduziere Trust Score basierend auf Risk Score
            trust_reduction = min(risk_score * 0.1, 0.5)  # Max 0.5 Reduktion
            new_trust = max(current_trust - trust_reduction, 0.0)

            cursor.execute("""
                UPDATE behavioral_profiles
                SET trust_score = ?, anomaly_count = ?, last_updated = ?
                WHERE user_id = ?
            """, (new_trust, new_anomaly_count, time.time(), user_id))
        else:
            # Erstelle neues Profil
            initial_trust = max(1.0 - (risk_score * 0.1), 0.1)
            cursor.execute("""
                INSERT INTO behavioral_profiles
                (user_id, profile_data, last_updated, anomaly_count, trust_score)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, '{}', time.time(), 1 if risk_score > 5.0 else 0, initial_trust))

        conn.commit()
        conn.close()

    def get_user_risk_profile(self, user_id: str) -> dict:
        """Gibt detailliertes Risikoprofil eines Benutzers zurück"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Basis-Profil
        cursor.execute(
            "SELECT * FROM behavioral_profiles WHERE user_id = ?", (user_id,))
        profile_result = cursor.fetchone()

        # Aktuelle Anomalien
        cursor.execute("""
            SELECT anomaly_type, severity, timestamp, description
            FROM anomaly_alerts
            WHERE user_id = ? AND resolved = 0
            ORDER BY timestamp DESC
            LIMIT 10
        """, (user_id,))
        active_anomalies = cursor.fetchall()

        # Aktivitäts-Statistiken
        cursor.execute("""
            SELECT action_type, COUNT(*), AVG(risk_score), MAX(risk_score)
            FROM user_actions
            WHERE user_id = ?
            GROUP BY action_type
        """, (user_id,))
        action_stats = cursor.fetchall()

        conn.close()

        if not profile_result:
            return {'error': 'User not found'}

        return {'user_id': user_id,
                'trust_score': profile_result[4],
                'anomaly_count': profile_result[3],
                'last_updated': datetime.fromtimestamp(profile_result[2]).isoformat(),
                'active_anomalies': [{'type': a[0],
                                      'severity': a[1],
                                      'timestamp': datetime.fromtimestamp(a[2]).isoformat(),
                                      'description': a[3]} for a in active_anomalies],
                'action_statistics': [{'action_type': s[0],
                                       'count': s[1],
                                       'avg_risk': round(s[2],
                                      2),
                                       'max_risk': round(s[3],
                                      2)} for s in action_stats]}


# ELITE MONITORING EXAMPLE
if __name__ == "__main__":
    engine = BehavioralAnalysisEngine()

    # Simuliere verschiedene Benutzeraktivitäten
    test_users = ['admin_user', 'normal_user', 'suspicious_user']

    for user in test_users:
        print(f"\n🧐 Simuliere Aktivitäten für {user}")

        if user == 'suspicious_user':
            # Verdächtige Aktivitäten
            for i in range(50):  # Viele Login-Versuche
                engine.record_action(user, 'login_attempt',
                                     {'success': False, 'ip': '192.168.1.100'})

            # Ungewöhnliche Uhrzeit
            night_timestamp = time.time() - (6 * 3600)  # 6 Stunden früher (Nacht)
            engine.record_action(user, 'admin_access',
                                 {'timestamp_override': night_timestamp})
        else:
            # Normale Aktivitäten
            for action in ['login', 'view_page', 'edit_data', 'logout']:
                engine.record_action(user, action, {'normal_activity': True})

    # Zeige Risikoprofile
    print("\n📊 BENUTZER-RISIKOPROFILE:")
    for user in test_users:
        profile = engine.get_user_risk_profile(user)
        print(f"\n👤 {user}:")
        print(f"  🎯 Trust Score: {profile['trust_score']:.2f}")
        print(f"  ⚠️ Anomalien: {profile['anomaly_count']}")
        print(f"  📈 Aktive Alerts: {len(profile['active_anomalies'])}")

        for anomaly in profile['active_anomalies']:
            print(f"    🚨 {anomaly['severity']}: {anomaly['description']}")
