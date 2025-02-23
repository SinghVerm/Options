import streamlit as st
import pandas as pd

def calculate_spread(sell_strike, sell_premium, buy_strikes, buy_premiums, max_loss):
    """
    Calculates the best strike to buy, required premium for 1:1 RR, number of lots needed, 
    risk-reward ratio, and total loss.
    """
    results = []

    for buy_strike, buy_premium in zip(buy_strikes, buy_premiums):
        spread_width = abs(sell_strike - buy_strike)
        net_credit = sell_premium - buy_premium
        max_loss_per_lot = spread_width - net_credit
        req_prem_1to1 = sell_premium - (spread_width / 2)

        # Calculate lots needed to match max loss
        lots_needed = int(max_loss // (max_loss_per_lot * 75)) if max_loss_per_lot > 0 else 0
        total_loss = int(lots_needed * max_loss_per_lot * 75)  # Total risk if trade goes wrong
        total_max_profit = int(lots_needed * net_credit * 75)  # Total profit potential

        # Calculate Risk-Reward Ratio
        risk_reward = round(net_credit / max_loss_per_lot, 2) if max_loss_per_lot > 0 else float("inf")

        # Format premiums to 2 decimal places
        results.append((
            buy_strike,
            f"{req_prem_1to1:.2f}",
            f"{buy_premium:.2f}",
            lots_needed,
            total_loss,
            total_max_profit,
            risk_reward
        ))

    return results


# Streamlit UI
st.title("Options Spread Optimizer")

# Market View Selection
market_view = st.selectbox("Market View", ["Long", "Short"])
option_type = "PUT" if market_view == "Long" else "CALL"  # FIXED

sell_strike = st.number_input(f"Sell Strike ({option_type})", min_value=10000, max_value=30000, step=100)
sell_premium = st.number_input(f"Sell Prem ({option_type})", min_value=0.1, step=0.1)

st.write(f"Enter Buy Premiums for Nearby {option_type} Strikes:")

# 1) First buy strike = 100 points away
# 2) Then allow 50-pt increments
if option_type == "PUT":
    first_buy_strike = sell_strike - 100
    buy_strikes = [first_buy_strike - i * 50 for i in range(4)]  # Adjust range(...) to get as many strikes as you want
else:
    first_buy_strike = sell_strike + 100
    buy_strikes = [first_buy_strike + i * 50 for i in range(4)]

buy_premiums = []
for idx, strike in enumerate(buy_strikes):
    bp = st.number_input(
        f"Buy Prem {strike} {option_type}",
        min_value=0.1,
        step=0.1,
        key=f"buy_{strike}_{idx}"
    )
    buy_premiums.append(bp)

# User enters max loss they are willing to take
max_loss = st.number_input("Max Loss (₹)", min_value=1000, step=500, key="max_loss")

if st.button("Calculate"):
    result = calculate_spread(sell_strike, sell_premium, buy_strikes, buy_premiums, max_loss)
    df = pd.DataFrame(
        result,
        columns=["Buy Strike", "1:1 Prem", "Buy Prem", "Lots", "Loss", "Profit", "Risk-Reward"]
    )

    # Remove default index and format table properly
    st.markdown(
        df.style.hide(axis="index")
        .set_table_styles(
            [
                {"selector": "th", "props": [("text-align", "center"), ("width", "80px")]},
                {"selector": "td", "props": [("text-align", "center")]}
            ]
        ).to_html(),
        unsafe_allow_html=True
    )

    best_strike = df.iloc[0]["Buy Strike"]
    st.write(f"### Best Strike to Buy: **{best_strike} {option_type}**")
