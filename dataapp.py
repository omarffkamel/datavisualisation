import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- App Setup ---
st.set_page_config(page_title="Data Analysis App", layout="wide")
st.title("Data Analysis and Visualization Web App")

# --- Load CSV ---
@st.cache_data
def load_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file, sep=None, engine='python')
        df.columns = df.columns.str.strip().str.replace(" ", "_")
        df = df.dropna(how='all', axis=1)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

@st.cache_data
def filter_data(df, conditions):
    for col, values in conditions.items():
        df = df[df[col].astype(str).isin(values)]
    return df

def plot_data(df, x, y, kind='line'):
    plt.figure(figsize=(10, 5))
    if kind == 'line':
        plt.plot(df[x], df[y], marker='o')
    else:
        plt.bar(df[x], df[y])
    plt.title(f'{y} vs {x}')
    plt.xlabel(x)
    plt.ylabel(y)
    plt.grid(True)
    st.pyplot(plt)

def plot_counts(df, column):
    plt.figure(figsize=(10, 5))
    df[column].value_counts().plot(kind='bar')
    plt.title(f'Value Counts in {column}')
    plt.xlabel(column)
    plt.ylabel('Count')
    plt.grid(True)
    st.pyplot(plt)

def plot_trend(df, date_col, value_col):
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col])
    df.set_index(date_col, inplace=True)
    trend = df[value_col].resample('M').mean()
    plt.figure(figsize=(10, 5))
    trend.plot()
    plt.title(f'Trend of {value_col}')
    plt.xlabel('Date')
    plt.ylabel(value_col)
    plt.grid(True)
    st.pyplot(plt)

# --- App Logic ---
uploaded_file = st.file_uploader("Upload your CSV file", type="csv")
if uploaded_file:
    df = load_data(uploaded_file)
    if not df.empty:
        st.subheader("Raw Data Preview")
        st.dataframe(df.head())

        st.subheader("Filter Options")
        filters = {}
        add_more = True
        key = 0

        while add_more:
            col = st.selectbox("Choose column to filter by", [''] + list(df.columns), key=f"filter_{key}")
            if col:
                options = df[col].dropna().astype(str).unique().tolist()
                selected = st.multiselect(f"Select values for {col}", options, key=f"values_{key}")
                if selected:
                    filters[col] = selected
            key += 1
            add_more = st.radio("Add another filter?", ["Yes", "No"], index=1, key=f"more_{key}") == "Yes"

        filtered_df = filter_data(df, filters)
        if not filtered_df.empty:
            st.success(f"{len(filtered_df)} rows after filtering.")
            st.dataframe(filtered_df.head())

            st.subheader("Visualize Data")
            col1, col2 = st.columns(2)
            with col1:
                x_col = st.selectbox("X-axis", filtered_df.columns)
            with col2:
                y_col = st.selectbox("Y-axis", filtered_df.columns)

            plot_type = st.radio("Plot Type", ["line", "bar"])
            if st.button("Generate Plot"):
                plot_data(filtered_df, x_col, y_col, plot_type)

            st.subheader("Value Counts")
            count_col = st.selectbox("Column for Value Count", filtered_df.columns)
            if st.button("Show Value Counts"):
                st.dataframe(filtered_df[count_col].value_counts())
                plot_counts(filtered_df, count_col)

            st.subheader("Trend Over Time")
            date_col = st.selectbox("Date Column", filtered_df.columns)
            val_col = st.selectbox("Value Column", filtered_df.columns)
            if st.button("Show Trend"):
                plot_trend(filtered_df, date_col, val_col)

            st.download_button("Download Filtered CSV", data=filtered_df.to_csv(index=False), file_name="filtered_data.csv")
        else:
            st.warning("No data matched your filter criteria.")
else:
    st.info("Upload a file to begin.")
