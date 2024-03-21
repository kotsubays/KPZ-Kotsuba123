import pandas as pd
from datetime import datetime

# Проверка наличия файла и чтение, если он существует
try:
    df = pd.read_csv('filename.csv')
except FileNotFoundError:
    df = pd.DataFrame(columns=['year', 'month', 'day', 'hour', 'minute', 'second'])

# Получение текущей даты и времени
now = datetime.now()

# Добавление новой строки с текущей датой и временем
df.loc[len(df)] = now.strftime('%Y %m %d %H %M %S').split()

# Сохранение данных в файл
df.to_csv("filename.csv", index=False)

print(df)
