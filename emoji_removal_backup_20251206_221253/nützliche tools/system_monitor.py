#!/usr/bin/env python3
"""
System-Monitor für Streamlit-App Performance
"""
import json
import time
from datetime import datetime

import psutil


def monitor_system(duration=60):
    """Überwacht System-Performance"""

    print(f"SYSTEM-MONITORING für {duration} Sekunden...")

    stats = {
        'timestamp': [],
        'cpu_percent': [],
        'memory_percent': [],
        'memory_used_mb': [],
        'disk_usage': [],
        'network_sent': [],
        'network_recv': [],
    }

    # Initial network stats
    net_start = psutil.net_io_counters()

    start_time = time.time()
    while time.time() - start_time < duration:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)

        # Memory
        memory = psutil.virtual_memory()

        # Disk
        disk = psutil.disk_usage('.')

        # Network
        net_current = psutil.net_io_counters()

        # Sammle Stats
        stats['timestamp'].append(datetime.now().isoformat())
        stats['cpu_percent'].append(cpu_percent)
        stats['memory_percent'].append(memory.percent)
        stats['memory_used_mb'].append(memory.used / 1024 / 1024)
        stats['disk_usage'].append(disk.percent)
        stats['network_sent'].append(
            net_current.bytes_sent -
            net_start.bytes_sent)
        stats['network_recv'].append(
            net_current.bytes_recv -
            net_start.bytes_recv)

        # Live-Anzeige
        print(
            f"\r🖥️ CPU: {
                cpu_percent:5.1f}% | 💾 RAM: {
                memory.percent:5.1f}% | 💽 Disk: {
                disk.percent:5.1f}%",
            end='')

        time.sleep(1)

    print("\n")

    # Analysiere Stats
    avg_cpu = sum(stats['cpu_percent']) / len(stats['cpu_percent'])
    avg_memory = sum(stats['memory_percent']) / len(stats['memory_percent'])
    max_memory_mb = max(stats['memory_used_mb'])

    print("MONITORING-ERGEBNISSE:")
    print(f"🖥️ Durchschnittliche CPU: {avg_cpu:.1f}%")
    print(f"💾 Durchschnittlicher RAM: {avg_memory:.1f}%")
    print(f"💾 Max RAM-Verbrauch: {max_memory_mb:.1f} MB")
    print(
        f"🌐 Netzwerk gesendet: {stats['network_sent'][-1] / 1024 / 1024:.1f} MB")
    print(
        f"🌐 Netzwerk empfangen: {stats['network_recv'][-1] / 1024 / 1024:.1f} MB")

    # Warnungen
    if avg_cpu > 80:
        print("WARNUNG: Hohe CPU-Auslastung!")
    if avg_memory > 85:
        print("WARNUNG: Hoher Speicherverbrauch!")

    # Stats speichern
    with open(f'system_monitor_{int(time.time())}.json', 'w') as f:
        json.dump(stats, f, indent=2)

    return stats


def check_streamlit_process():
    """Prüft Streamlit-Prozess-Details"""

    streamlit_processes = []

    for proc in psutil.process_iter(
            ['pid', 'name', 'cmdline', 'memory_info', 'cpu_percent']):
        try:
            if 'streamlit' in proc.info['name'].lower() or \
               any('streamlit' in arg.lower() for arg in proc.info['cmdline']):
                streamlit_processes.append(proc.info)
        except BaseException:
            continue

    if streamlit_processes:
        print(f"STREAMLIT-PROZESSE ({len(streamlit_processes)}):")
        for proc in streamlit_processes:
            memory_mb = proc['memory_info'].rss / 1024 / 1024
            print(
                f"  PID {
                    proc['pid']}: {
                    memory_mb:.1f} MB RAM, {
                    proc['cpu_percent']:.1f}% CPU")
    else:
        print("Keine Streamlit-Prozesse gefunden")


if __name__ == "__main__":
    check_streamlit_process()
    monitor_system(60)
