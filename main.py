import pandas as pd
import streamlit as st
from sber import parse_sberbank_statement
from renovatia import parse_clinica_system

def load_all_data(sber_file, clinica_file):
    sber_data = []
    clinica_data = []
    
    if sber_file is not None:
        sber_data = parse_sberbank_statement(sber_file)
        
    if clinica_file is not None:
        clinica_data = parse_clinica_system(clinica_file)
    
    all_operations = sber_data + clinica_data
    
    if not all_operations:
        return pd.DataFrame()
        
    df = pd.DataFrame(all_operations)
    df['Дата'] = pd.to_datetime(df['Дата'], format='%d.%m.%Y', errors='coerce')
    df = df.dropna(subset=['Дата']) 
    return df

st.set_page_config(page_title="Мои Финансы", layout="wide")
st.title("📊 Сводный финансовый дашборд")

col_upload1, col_upload2 = st.columns(2)
with col_upload1:
    sber_file = st.file_uploader("📥 Загрузите выписку Сбербанка", type=["xlsx"])
with col_upload2:
    clinica_file = st.file_uploader("📥 Загрузите статистику Renovatio", type=["csv"])

df_all = load_all_data(sber_file, clinica_file)

if df_all.empty:
    st.info("👆 Загрузите файлы выписок через формы выше, чтобы увидеть аналитику.")
else:
    st.divider() 
    
    st.sidebar.header("Фильтры")
    min_date = df_all['Дата'].min().date()
    max_date = df_all['Дата'].max().date()
    
    date_range = st.sidebar.date_input("Выберите период", [min_date, max_date])
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range[0]

    mask = (df_all['Дата'].dt.date >= start_date) & (df_all['Дата'].dt.date <= end_date)
    filtered_df = df_all.loc[mask]

    total_income = filtered_df['Приход (Кредит)'].sum()
    total_expense = filtered_df['Расход (Дебет)'].sum()
    net_profit = total_income - total_expense

    col1, col2, col3 = st.columns(3)
    col1.metric("Общий приход", f"{total_income:,.2f} ₽".replace(',', ' '))
    col2.metric("Общий расход", f"{total_expense:,.2f} ₽".replace(',', ' '))
    col3.metric("Сальдо (Чистая прибыль)", f"{net_profit:,.2f} ₽".replace(',', ' '))

    st.subheader("Детализация операций")
    display_df = filtered_df.copy()
    display_df['Дата'] = display_df['Дата'].dt.strftime('%d.%m.%Y')
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
