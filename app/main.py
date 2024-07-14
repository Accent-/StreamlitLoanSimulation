import streamlit as st
import numpy as np
import pandas as pd

def calculate_loan(principal, years, annural_rate, bonus_payment=0):
    monthly_rate = annural_rate / 100 / 12
    months = years * 12

    if monthly_rate > 0:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
    else:
        monthly_payment = principal / months

    total_payment = monthly_payment * months

    balance = principal
    schedule = []
    for month in range(1, months + 1):
        interest_payment = balance * monthly_rate
        principal_payment = monthly_payment - interest_payment
        balance -= principal_payment
        if balance < 0:
            balance = 0

        schedule.append({
            "Month": month,
            "Interest Payment": interest_payment,
            "Principal Payment": principal_payment,
            "Total Payment":monthly_payment,
            "Remaining Balance": balance,
        })

    # ボーナス返済を考慮
    if bonus_payment > 0:
        for i in range(0, len(schedule), 6):  # 6ヶ月ごとにボーナス返済を行うと仮定
            schedule[i]['Principal Payment'] += bonus_payment
            schedule[i]['Remaining Balance'] -= bonus_payment
            schedule[i]['Total Payment'] += bonus_payment
            if schedule[i]['Remaining Balance'] < 0:
                schedule[i]['Remaining Balance'] = 0
            # 残高を更新
            for j in range(i + 1, len(schedule)):
                schedule[j]['Remaining Balance'] -= bonus_payment
                if schedule[j]['Remaining Balance'] < 0:
                    schedule[j]['Remaining Balance'] = 0

    schedule_df = pd.DataFrame(schedule)

    schedule_df['Years'] = schedule_df['Month'].astype(int) // 12
    schedule_df['Remaining_Months'] = schedule_df['Month'].astype(int) % 12
    schedule_df['Years_Months'] = schedule_df['Years'].astype(str) + '年' + schedule_df['Remaining_Months'].astype(str) + 'か月'

    schedule_df = schedule_df.drop('Years', axis=1)
    schedule_df = schedule_df.drop('Remaining_Months', axis=1)
    schedule_df = schedule_df.drop('Month', axis=1)

    schedule_df = schedule_df.set_index('Years_Months')

    schedule_df = schedule_df.rename_axis('年月')
    schedule_df = schedule_df.rename(
        columns={
            "Interest Payment": "利息支払（万円）",
            "Principal Payment": "元本返済（万円）",
            "Total Payment": "総支払額（万円）",
            "Remaining Balance": "残高（万円）",
        })

    return monthly_payment, total_payment, schedule_df


st.title("ローン返済シミュレーション")

with st.sidebar:
    st.subheader('パラメータ')
    st.session_state['principal'] = st.number_input(
        "借入金額（万円）", 
        min_value=100, 
        max_value=100000, 
        value=500
    )
    st.session_state['years'] = st.slider(
        "返済期間（年）", 
        min_value=1, 
        max_value=45, 
        value=10
    )
    st.session_state['annual_rate'] = st.slider(
        "金利（%）", 
        min_value=0.1, 
        max_value=10.0, 
        value=1.0
    )
    st.session_state['bonus_payment'] = st.number_input(
        "ボーナス返済額（万円、任意）", 
        min_value=0, 
        max_value=st.session_state['principal']//2, 
        value=0
    )

(
    st.session_state['monthly_payment'], 
    st.session_state['total_payment'], 
    st.session_state['schedule'],
) = calculate_loan(
    st.session_state['principal'], 
    st.session_state['years'], 
    st.session_state['annual_rate'], 
    st.session_state['bonus_payment']
)

st.write(f"月々の返済額: {st.session_state['monthly_payment']:,.1f}万円")
st.write(f"総返済額: {st.session_state['total_payment']:,.0f}万円")

st.subheader("返済スケジュール")
st.dataframe(st.session_state['schedule'])
# st.dataframe(schedule.style.format("{:.1f}"))
