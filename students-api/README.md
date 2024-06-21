## Запуск

1. Перейдите в папку проекта

2. Создайте виртуальное окружение командой и активируйте его:
    ```console
    foo@bar:~$ python3 -m venv venv
    foo@bar:~$ source ./venv/bin/activate  # На MacOS и Linux
    foo@bar:~$ venv\Scripts\activate  # На Windows
    ```

3. Установите библиотеки
    ```console
    foo@bar:~$ pip install -r requirements.txt
    foo@bar:~$ pip install -r requirements.dev.txt
    ```
4. Запускайте приложение!
    ```console
    foo@bar:~$ python -m api
    ```

## Форматирование
```console
foo@bar:~$ black api
foo@bar:~$ isort api
```