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


## 🔥 Características implementadas

| Feature | Estado | Descripción |
|---------|--------|-------------|
| Extracción DBs | ✅ | `--dbs` |
| Enumeración tablas | ✅ | `--tables` |
| Volcado de datos | ✅ | `--dump` |
| Modo verboso | ✅ | `-v` / `-vv` |
| POST requests | ✅ | `-m POST -d` |
| Evasión WAF | ✅ | `--waf-evasion` |
| Modo stealth | ✅ | `--stealth` |
| Detección DB engine | ✅ | `--detect-db` |

## 📦 Instalación rápida

```bash
git clone https://github.com/Falconmx1/Sqlmxmap.git
cd Sqlmxmap
pip install -r requirements.txt
python sqlmxmap.py -h
