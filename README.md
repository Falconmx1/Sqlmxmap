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

🎯 Uso básico
bash

python sqlmxmap.py -u "http://test.com/page.php?id={{id}}"

🧪 Ejemplo
bash

python sqlmxmap.py -u "http://testphp.vulnweb.com/artists.php?artist={{id}}" -p artist
