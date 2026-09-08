import pandas as pd

def parse_clinica_system(file_path):
    """Считывает CSV из ИС Renovatio и возвращает список операций."""
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        return [] # Если файла нет, возвращаем пустой список
    
    # Меняем запятую на точку для корректного преобразования в числа
    df['Сумма'] = df['Сумма'].astype(str).str.replace(',', '.').astype(float)
    
    operations = []
    for _, row in df.iterrows():
        operations.append({
            'Дата': row['Дата'],
            'Расход (Дебет)': 0.0,
            'Приход (Кредит)': row['Сумма'],
            'Назначение': 'Прибыль из ИС'
        })
    return operations