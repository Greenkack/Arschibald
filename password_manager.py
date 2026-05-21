"""password_manager.py - Password Management Utilities"""
import secrets
import string
from typing import List

def generate_strong_password(length: int = 16) -> str:
    """Generiere sicheres Passwort"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

def check_password_strength(password: str) -> dict:
    """Prüfe Passwort-Stärke"""
    score = 0
    feedback = []
    
    # Länge
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Mindestens 8 Zeichen erforderlich")
    
    if len(password) >= 12:
        score += 1
    
    # Großbuchstaben
    if any(c.isupper() for c in password):
        score += 1
    else:
        feedback.append("Verwende Großbuchstaben")
    
    # Kleinbuchstaben
    if any(c.islower() for c in password):
        score += 1
    else:
        feedback.append("Verwende Kleinbuchstaben")
    
    # Zahlen
    if any(c.isdigit() for c in password):
        score += 1
    else:
        feedback.append("Verwende Zahlen")
    
    # Sonderzeichen
    if any(c in string.punctuation for c in password):
        score += 1
    else:
        feedback.append("Verwende Sonderzeichen")
    
    strength_labels = {
        0: "Sehr schwach",
        1: "Sehr schwach",
        2: "Schwach",
        3: "Mittel",
        4: "Stark",
        5: "Sehr stark",
        6: "Exzellent"
    }
    
    return {
        'score': score,
        'max_score': 6,
        'strength': strength_labels[score],
        'feedback': feedback
    }

def validate_password_policy(password: str, min_length: int = 8, require_uppercase: bool = True, 
                            require_lowercase: bool = True, require_digits: bool = True, 
                            require_special: bool = True) -> tuple[bool, List[str]]:
    """Validiere Passwort gegen Policy"""
    errors = []
    
    if len(password) < min_length:
        errors.append(f"Passwort muss mindestens {min_length} Zeichen lang sein")
    
    if require_uppercase and not any(c.isupper() for c in password):
        errors.append("Passwort muss mindestens einen Großbuchstaben enthalten")
    
    if require_lowercase and not any(c.islower() for c in password):
        errors.append("Passwort muss mindestens einen Kleinbuchstaben enthalten")
    
    if require_digits and not any(c.isdigit() for c in password):
        errors.append("Passwort muss mindestens eine Zahl enthalten")
    
    if require_special and not any(c in string.punctuation for c in password):
        errors.append("Passwort muss mindestens ein Sonderzeichen enthalten")
    
    return len(errors) == 0, errors
