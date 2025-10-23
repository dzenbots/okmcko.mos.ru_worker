# Получение документов, размещаемых на сайте okmcko.mos.ru (ЭЖД &rarr; Организация образования &rarr; Внешняя оценка )

1. [Установка](#установка)
2. [Предварительная настройка параметров в .env.dist](#предварительная-настройка) 
3. [Запуск](#запуск)

---

## Установка

    При написании использовался Python 3.13
1. Качаем репозиторий:
    ```shell
    git clone https://github.com/dzenbots/okmcko.mos.ru_worker.git
    ```
2. Создаем вирутальное окружение, активируем его и устанавливаем зависимости:
    
    для CMD:
    ```cmd
    python -m venv .venv
    .\venv\scripts\activate.bat
    pip install -r requirements.txt
    ```
    для Powershell 
    ```powershell
    python -m venv .venv
    .\venv\scripts\activate.ps1
    pip install -r requirements.txt
    ```
    для Bash (Linux) 
    ```shell
    python -m venv .venv
    ./venv/bin/activate
    pip install -r requirements.txt
    ```
   
3. Устанавливаем драйвер браузера для Playwright

    ```shell
    playwright install chromium
    ```
   
## Предварительная настройка параметров в [.env.dist](.env.dist)

Переименовываем (или копируем) файл `.env.dist` в `.env`

Заполняем переменные своими данными:

| Переменная | Значение |
|:---|:---|:---|


## Запуск

При активированном виртуальном окружении запускаем командой

```shell
python main.py
```

