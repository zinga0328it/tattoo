#!/usr/bin/env python3
"""
Monitor dei log di sicurezza in tempo reale
"""

import time
import os

def monitor_logs(log_file):
    """Monitora il file di log per nuove linee"""
    if not os.path.exists(log_file):
        print(f"File {log_file} non trovato. Crealo prima.")
        return
    
    with open(log_file, 'r') as f:
        f.seek(0, 2)  # Vai alla fine del file
        
        print(f"Monitoraggio {log_file} in tempo reale...")
        print("Premi Ctrl+C per uscire\n")
        
        while True:
            line = f.readline()
            if line:
                print(line.strip())
            else:
                time.sleep(0.1)

if __name__ == '__main__':
    monitor_logs('/home/alex/web/eternaai/security.log')
