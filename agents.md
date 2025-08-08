Что делает RangeForge (кратко)
range up — Terraform+Packer создают ВМ и сеть → Ansible конфигурирует роли (AD DC, WS, Linux, сенсоры, Wazuh).

range emulate --playbook T1055,T1208,... — запускает атаки (Atomic/Caldera/импакт-скрипты) по WinRM/SSH.

range observe — открывает готовые дашборды/правила в Wazuh/ELK.

range down — аккуратная уборка ресурсов.

Технологический стек
IaC и оркестрация
Terraform (+ провайдер Proxmox VE или libvirt как альтернатива).

Packer — образы Windows Server/Win10/Win11 и Ubuntu.

Ansible — роли: AD DC (win_domain), WinRM hardening, Sysmon, Winlogbeat/Osquery, Wazuh-agent, Linux hardening.

Python CLI (Typer/Click) — команда range (обёртка над TF/Ansible/runner’ом).

State/инвентарь: YAML + inventory.json (генерится после Terraform), опционально SQLite для истории прогонов.

Телеметрия и SIEM
Wazuh (менеджер + индекс-бэкенд) или ELK Stack (Elasticsearch + Kibana) — на выбор в range.yml.

Sysmon (SwiftOnSecurity config) + Winlogbeat на Windows.

Osquery + Filebeat/Auditbeat на Linux.

Suricata (опционально) на пограничной ВМ для сетевых алертов.

Эмуляция угроз
Atomic Red Team (Invoke-AtomicRedTeam) — безопасные атрибуты.

Caldera (опционально) — автономные цепочки ATT&CK.

Impacket (адресно: secretsdump.py, psexec.py) — в лабе и с синтетическими учётками.

Rubeus/Certify/SafetyKatz — только в оконтурах лаба, сценарии обернуты флагами безопасности.

Сервисная обвязка
Traefik/Nginx — reverse-proxy к Kibana/Wazuh-Dash.

Prometheus + Grafana — здоровье полигона.

GitHub Actions — lint/test/build; Trivy — скан образов.

Базовая топология (MVP)
pfSense/Opnsense (NAT, изоляция lab-LAN)

DC01 (Windows Server, AD DS, DNS, KDC)

WIN01 (Windows 10/11, рабочая станция)

LIN01 (Ubuntu Server, файл-шары/SSH)

SOC01 (Wazuh All-in-One или ELK)

Сегменты: mgmt, corp, soc (VLAN/виртуальные сети)

NFR и правила
Идемпотентность: повторный range up не ломает конфигурацию.

Изоляция: NAT, нет маршрутов в прод/интернет (кроме скачивания артефактов).

Скорость: полный подъём ≤ 25–35 мин на железе с 32 ГБ RAM.

Логи: всё в JSON, единый кореляционный range_run_id.

ТЗ (техническое задание)
Роли/персоны
Red: выбирает матрицу ATT&CK, запускает эмуляцию.

Blue: смотрит дашборды/алерты, пишет/включает правила.

Admin: настраивает топологию, лимиты, ключи, профили атак.

Функциональные требования
Развёртывание

Terraform-модули для Proxmox: сети, шаблоны, ВМ, cloud-init.

Packer-шаблоны Windows (sysprep + WinRM secure) и Ubuntu.

Ansible-роли: AD, WinRM (HTTPS, сертификат), Sysmon, Beats, Wazuh-agent, оснастка Linux.

Запуск атак

Исполнитель: PowerShell Remoting/WinRM и SSH.

Каталог плейбуков ATT&CK: YAML-описания TTP (pre-checks → execute → cleanup).

Три готовых цепочки: Kerberoasting (T1558.003), DCSync (T1003.006 симуляция), Lateral via PsExec (T1570).

Наблюдение/детекция

Импорт готовых правил Wazuh для выбранных TTP.

Дашборды в Kibana/Wazuh-Dash: “Attack Timeline”, “Auth/LSASS/NTDS”, “Lateral Movement”.

Экспорт артефактов тренинга (evtx/pcap/ndjson) кнопкой range collect.

Управление

range up|down|status|emulate|observe|collect с понятным CLI-UX.

Конфиг range.yml: провайдер, IP-планы, выбор SIEM, список атак, safety-флаги.

Безопасность

Политика блокировки “опасных” TTP по умолчанию; запуск — только с --i-understand.

Маркировка тестовых учёток/секретов; запрет на утечку наружу.

Команды CLI (пример)
range init — проверка гипервизора/ресурсов, загрузка базовых образов.

range up --profile basic-ad

range emulate --chain lateral-basic --targets WIN01

range observe --open kibana

range collect --out ./artifacts/run_2025-08-08

range down --destroy-images no

Задачи для GPT Codex (готовые промпты)
Общие требования: Python 3.12, Poetry, ruff+mypy, pre-commit, модульные тесты (pytest), IaC валидаторы (terraform validate, packer validate, ansible-lint), Docker-окружение для SOC01.
