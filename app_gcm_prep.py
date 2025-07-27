from datetime import date
from dateutil.relativedelta import relativedelta
import streamlit as st
import pandas as pd

def map_to_last_year(d: date) -> date:
    """
    Given a date d (e.g. Aug 1, 2025), returns the same‐ordinal weekday
    in the prior year (e.g. the 1st Friday of Aug 2024).
    """
    weekday = d.weekday()  # Mon=0 … Sun=6
    # count which occurrence this is in the month
    ordinal = sum(
        1 for day in range(1, d.day + 1)
        if date(d.year, d.month, day).weekday() == weekday
    )
    target_year = d.year - 1
    count = 0
    # scan that month last year for the same ordinal
    for day in range(1, 32):
        try:
            cand = date(target_year, d.month, day)
        except ValueError:
            break
        if cand.weekday() == weekday:
            count += 1
            if count == ordinal:
                return cand
    # fallback if no match
    return d - relativedelta(years=1)


# → your map from Step 2
location_files = {
    "Malibu":               "malibu_data_aug_dec_2024.csv",
    "Grand Central Market": "gcm_data_aug_dec_2024.csv",
    "Huntington Beach":     "hb_data_aug_dec_2024.csv",
    "Ghirardelli Square":   "sf_data_aug_dec_2024.csv",
    "Santa Barbara":        "sb_data_aug_dec_2024.csv"
}

st.title("🦞 Broad Street Oyster Co. Smart Prep 🦪")

# create one tab per location
tabs = st.tabs(list(location_files.keys()))

for tab, location in zip(tabs, location_files):
    with tab:
        st.header(location)
        # 1) load the right CSV
        df = pd.read_csv(location_files[location])
        df['Date'] = pd.to_datetime(df['Date'])
        df['Qty']  = pd.to_numeric(df['Qty'], errors='coerce')
        
        # 2) same-day last-year mapping (reuse your function)
        sel = st.date_input(f"Select a date for {location}:", value=date(2025,8,1))
        past = map_to_last_year(sel)  # your existing helper
        
        st.markdown(f"Mapping: **{sel:%b %d, %Y}** → **{past:%b %d, %Y}**")
        
        # 3) build and filter the forecast
        day = (
            df[df['Date'].dt.date == past]
              .groupby('Item')['Qty'].sum()
              .reset_index(name='Forecast Qty')
        )
        exclude = [
            'N/A Beverage','Draft Beer','Beer','BROAD STREET Hard Lemonade',
            'Wine by the Glass', 'Wine by the glass', 'Side Sourdough Toast', 'OG Tote',
            'OG Malibu Tee', 'OG Grand Central Market Tee', 'Delivery Fee', 'Wine By The Bottle', 'Beanie', 'Pro Hat','BROAD STREET Spicy Marg',
            'BROAD STREET Bloody','Party Wines', 'Party Size', 'Custom Amount'
        ]
        day = day[~day['Item'].isin(exclude)]
        
        # 4) buffer slider
        buf = st.slider("Adjust by % buffer:", -35, 35, 0, key=location)
        day['Adjusted Qty'] = (day['Forecast Qty'] * (1 + buf/100)).round().astype(int)
        
        # 5) display
        st.subheader(f"Prep for {sel:%A, %b %d, %Y}")
        st.dataframe(
            day.sort_values('Forecast Qty', ascending=False)
               .set_index('Item')[['Forecast Qty','Adjusted Qty']]
        )
