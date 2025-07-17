import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Streamlit page configuration
st.set_page_config(page_title="Flight Load Dashboard", layout="wide")

# Load and cache the CSV file
@st.cache_data
def load_data():
    df = pd.read_csv("clean_flight_data.csv")
    df['Departure Date'] = pd.to_datetime(df['Departure Date'])
    return df

# Load data
df = load_data()

# Sidebar navigation
page = st.sidebar.radio("Select Page", [
    "By Date",
    "By Segment",
    "Advanced Statistics",
    "Compare Segments"
])

# Page 1: Filter by Date
if page == "By Date":
    st.header("📅 Filter by Date")
    unique_dates = df['Departure Date'].dt.date.unique()
    selected_date = st.selectbox("Select a Date", sorted(unique_dates))

    filtered_df = df[df['Departure Date'].dt.date == selected_date]

    st.subheader(f"Flight Data for {selected_date}")
    st.dataframe(filtered_df)

    st.subheader("Summary")
    summary = filtered_df[['Adults', 'Infants', 'Total Booked']].sum()
    st.write(summary.to_frame().T)

    st.subheader("No Shows by Segment")
    no_shows_by_segment = filtered_df.groupby('Segment')['No Shows'].sum().reset_index()

    fig, ax = plt.subplots()
    sns.barplot(data=no_shows_by_segment, x='Segment', y='No Shows', ax=ax)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    st.pyplot(fig)

# Page 2: Filter by Segment
elif page == "By Segment":
    st.header("✈️ Filter by Segment")
    segments = df['Segment'].unique()
    selected_segment = st.selectbox("Select Segment", sorted(segments))

    filtered_df = df[df['Segment'] == selected_segment]

    st.subheader(f"Flight Data for Segment: {selected_segment}")
    st.dataframe(filtered_df)

    st.subheader("Daily Total Booked")
    daily_totals = filtered_df.groupby('Departure Date')[['Adults', 'Infants', 'Total Booked']].sum()
    st.line_chart(daily_totals['Total Booked'])

    st.subheader("Daily No Shows")
    no_shows_daily = filtered_df.groupby('Departure Date')['No Shows'].sum()
    st.line_chart(no_shows_daily)

# Page 3: Advanced Statistical Insights
elif page == "Advanced Statistics":
    st.header("📊 Advanced Statistics")

    st.subheader("1. Average Passengers per Segment")
    avg_passengers = df.groupby('Segment')[['Adults', 'Infants']].mean()
    avg_passengers['Total'] = avg_passengers['Adults'] + avg_passengers['Infants']
    st.dataframe(avg_passengers.style.format("{:.2f}"))

    st.subheader("2. Top 5 Segments by Flown Load")
    top_segments = df.groupby('Segment')['Flown Load'].sum().sort_values(ascending=False).head(5)
    st.bar_chart(top_segments)

    st.subheader("3. Top 5 Dates by Total Booked")
    top_dates = df.groupby('Departure Date')['Total Booked'].sum().sort_values(ascending=False).head(5)
    st.bar_chart(top_dates)

    st.subheader("4. No Shows Trend Over Time")
    no_shows_by_date = df.groupby('Departure Date')['No Shows'].sum()
    st.line_chart(no_shows_by_date)

    st.subheader("5. Correlation Matrix")
    numeric_df = df.select_dtypes(include='number')
    corr = numeric_df.corr()
    st.dataframe(corr.style.background_gradient(cmap='coolwarm'))

    st.subheader("6. Outliers in No Shows")
    outlier_threshold = df['No Shows'].mean() + 2 * df['No Shows'].std()
    outliers = df[df['No Shows'] > outlier_threshold]
    st.write(f"Found {len(outliers)} flights with high no shows:")
    st.dataframe(outliers[['Departure Date', 'Flight Number', 'Segment', 'No Shows']])

# Page 4: Compare Two Segments
elif page == "Compare Segments":
    st.header("📌 Compare Two Segments")

    segments = sorted(df['Segment'].unique())
    seg1 = st.selectbox("Select First Segment", segments, index=0)
    seg2 = st.selectbox("Select Second Segment", segments, index=1)

    if seg1 == seg2:
        st.warning("Please select two different segments.")
    else:
        df1 = df[df['Segment'] == seg1]
        df2 = df[df['Segment'] == seg2]

        # Summary stats
        st.subheader(f"Summary for {seg1}")
        st.write(df1[['Adults', 'Infants', 'Total Booked', 'No Shows', 'Flown Load']].sum().to_frame().T)

        st.subheader(f"Summary for {seg2}")
        st.write(df2[['Adults', 'Infants', 'Total Booked', 'No Shows', 'Flown Load']].sum().to_frame().T)

        # Line chart comparison
        st.subheader("📈 Passenger Trends")
        fig, axs = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

        daily1 = df1.groupby('Departure Date')[['Adults', 'Infants']].sum()
        daily1['Total'] = daily1['Adults'] + daily1['Infants']
        sns.lineplot(data=daily1, ax=axs[0])
        axs[0].set_title(f"{seg1}")
        axs[0].tick_params(axis='x', rotation=45)

        daily2 = df2.groupby('Departure Date')[['Adults', 'Infants']].sum()
        daily2['Total'] = daily2['Adults'] + daily2['Infants']
        sns.lineplot(data=daily2, ax=axs[1])
        axs[1].set_title(f"{seg2}")
        axs[1].tick_params(axis='x', rotation=45)

        st.pyplot(fig)

        # No shows comparison
        st.subheader("📉 No Shows Comparison Over Time")
        no_shows1 = df1.groupby('Departure Date')['No Shows'].sum()
        no_shows2 = df2.groupby('Departure Date')['No Shows'].sum()

        compare_df = pd.DataFrame({
            seg1: no_shows1,
            seg2: no_shows2
        }).fillna(0)

        st.line_chart(compare_df)

        # Scatter plot: Booked Load vs Flown Load
        st.subheader("🟡 Booked vs Flown Load")
        fig2, ax2 = plt.subplots(figsize=(8,6))
        sns.scatterplot(data=df1, x='Booked Load (Adult/Infant)', y='Flown Load', label=seg1)
        sns.scatterplot(data=df2, x='Booked Load (Adult/Infant)', y='Flown Load', label=seg2)
        ax2.set_title("Booked vs Flown Load Comparison")
        ax2.legend()
        st.pyplot(fig2)
