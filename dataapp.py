import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import base64

st.markdown(f"""
    <style>
    .header-container {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 20px;
        margin-bottom: 20px;
    }}
    .header h1 {{
        font-size: 2rem;
        margin: 0;
        padding: 0;
    }}
    .header img {{
        height: 60px;
    }}
    .user-manual {{
        padding: 10px;
        margin-top: 20px;
    }}
    .footer {{
        padding: 10px;
        margin-top: 20px;
        text-align: center;
    }}
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="header-container">
        <div class="header">
            <h1>Data Analysis and Visualization Web App</h1>
        </div>
    </div>
""", unsafe_allow_html=True)

page = st.sidebar.radio("Navigation", ["App", "User Manual"])

if page == "App":
    @st.cache_data
    def load_data(uploaded_file):
        dtype_spec = {
            'Plant (WERKS)': str,
            'G/L Account (SAKNR)': str,
            'Company Code (BUKRS)': str
        }
        try:
            df = pd.read_csv(uploaded_file, delimiter=';', dtype=dtype_spec, low_memory=False)
            df = df.loc[:, (df != 0).any(axis=0)]
            df = df.dropna(how='all', axis=1)
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return pd.DataFrame()
        return df

    @st.cache_data
    def filter_data(df, filter_conditions):
        if not df.empty:
            for column, values in filter_conditions.items():
                df = df[df[column].astype(str).isin(values)]
            if df.empty:
                st.warning("No data found for the given filter conditions.")
            return df
        return pd.DataFrame()

    def plot_data(df, x_col, y_col, plot_type='line'):
        if not df.empty:
            try:
                df[x_col] = pd.to_numeric(df[x_col], errors='ignore')
                df[y_col] = pd.to_numeric(df[y_col], errors='ignore')
            except ValueError:
                pass
            
            plt.figure(figsize=(10, 5))
            if plot_type == 'line':
                if pd.api.types.is_numeric_dtype(df[x_col]) and pd.api.types.is_numeric_dtype(df[y_col]):
                    plt.plot(df[x_col], df[y_col], marker='o')
                else:
                    st.warning("Line plot requires numeric data for both axes.")
                    return
            elif plot_type == 'bar':
                if pd.api.types.is_numeric_dtype(df[y_col]):
                    df.groupby(x_col)[y_col].sum().plot(kind='bar')
                else:
                    df[x_col].value_counts().plot(kind='bar')
            plt.title(f'{y_col} over {x_col}')
            plt.xlabel(x_col)
            plt.ylabel(y_col)
            plt.grid(True)
            st.pyplot(plt)
        else:
            st.warning("Filtered data is empty, no plot to display.")

    def plot_counts(df, count_col):
        if not df.empty:
            count_data = df[count_col].value_counts()
            plt.figure(figsize=(10, 5))
            count_data.plot(kind='bar')
            plt.title(f'Count of different values in {count_col}')
            plt.xlabel(count_col)
            plt.ylabel('Count')
            plt.grid(True)
            st.pyplot(plt)
        else:
            st.warning("Data is empty, no plot to display.")

    def plot_trend(df, date_col, value_col):
        if not df.empty:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            if df[date_col].isnull().all():
                st.warning("Date parsing failed. Please select a valid date column.")
                return

            df[value_col] = pd.to_numeric(df[value_col], errors='coerce')

            if df[value_col].isnull().all():
                st.warning("Value column cannot be converted to numeric. Please select a different value column.")
                return

            df = df.set_index(date_col)
            trend_data = df[value_col].resample('M').mean()
            plt.figure(figsize=(10, 5))
            trend_data.plot()
            plt.title(f'Trend of {value_col} over Time')
            plt.xlabel('Time')
            plt.ylabel(value_col)
            plt.grid(True)
            st.pyplot(plt)
        else:
            st.warning("Filtered data is empty, no trend to display.")

    def descriptive_statistics(df, column):
        st.write(f"Descriptive Statistics for {column}:")
        desc_stats = df[column].describe()
        st.write(desc_stats)
        
        plt.figure(figsize=(10, 5))
        desc_stats.plot(kind='bar')
        plt.title(f'Descriptive Statistics for {column}')
        plt.xlabel('Statistics')
        plt.ylabel('Values')
        plt.grid(True)
        st.pyplot(plt)

    def correlation_matrix(df):
        st.write("Correlation Matrix:")
        numeric_df = df.select_dtypes(include=[float, int])
        if numeric_df.empty:
            st.warning("No numeric columns available for correlation matrix.")
            return
        corr = numeric_df.corr()
        st.write(corr)
        plt.figure(figsize=(10, 5))
        plt.matshow(corr, cmap='coolwarm')
        plt.colorbar()
        st.pyplot(plt)

    def distribution_plot(df, column):
        st.write(f"Distribution of {column}:")
        plt.figure(figsize=(10, 5))
        df[column].hist(bins=30)
        plt.title(f'Distribution of {column}')
        plt.xlabel(column)
        plt.ylabel('Frequency')
        st.pyplot(plt)

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="file_uploader")
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        if not df.empty:
            st.write("Data Preview:")
            st.dataframe(df.head())

            filter_conditions = {}
            key_index = 0
            while True:
                filter_column = st.selectbox("Select Column to Filter By", [''] + list(df.columns), key=f'filter_column_{key_index}')
                if filter_column:
                    filter_values = df[filter_column].unique().tolist()
                    selected_values = st.multiselect(f"Select Values for {filter_column}", filter_values, key=f'selected_values_{key_index}')
                    if selected_values:
                        filter_conditions[filter_column] = selected_values
                key_index += 1
                add_more = st.radio("Do you want to filter by another column?", ("Yes", "No"), index=1, key=f'add_more_{key_index}')
                if add_more == "No":
                    break

            filtered_df = filter_data(df, filter_conditions)
            if not filtered_df.empty:
                st.write("Filtered Data Preview:")
                st.dataframe(filtered_df.head())

                col1, col2 = st.columns(2)
                with col1:
                    x_col = st.selectbox('Select X-axis Column', filtered_df.columns)
                with col2:
                    y_col = st.selectbox('Select Y-axis Column', filtered_df.columns)

                plot_type = st.selectbox('Select Plot Type', ['line', 'bar'])
                if st.button('Generate Plot'):
                    plot_data(filtered_df, x_col, y_col, plot_type)

                if st.button('Export Filtered Data'):
                    filtered_df.to_csv('filtered_data.csv', index=False)
                    st.success('Filtered data has been exported as filtered_data.csv.')

                count_col = st.selectbox("Select Column to Show Value Counts", filtered_df.columns)
                if st.button('Show Counts'):
                    st.write(filtered_df[count_col].value_counts())
                    plot_counts(filtered_df, count_col)

                date_col = st.selectbox('Select Date Column for Trend Analysis', filtered_df.columns)
                value_col = st.selectbox('Select Value Column for Trend Analysis', filtered_df.columns)
                if st.button('Show Trend'):
                    plot_trend(filtered_df, date_col, value_col)
                
                desc_col = st.selectbox('Select Column for Descriptive Statistics', filtered_df.columns)
                if st.button('Show Descriptive Statistics'):
                    descriptive_statistics(filtered_df, desc_col)

                if st.button('Show Correlation Matrix'):
                    correlation_matrix(filtered_df)

                distribution_col = st.selectbox('Select Column for Distribution Plot', filtered_df.columns)
                if st.button('Show Distribution Plot'):
                    distribution_plot(filtered_df, distribution_col)
    else:
        st.write("Please upload a CSV file to get started.")

    st.markdown(f"""
        <div class="footer">
            <p><i>This app was developed by Omar Kamel.</i></p>
        </div>
    """, unsafe_allow_html=True)

elif page == "User Manual":
    st.markdown(f"""
        <div class="user-manual">
            <h2>User Manual for Data Analysis and Visualization Web App</h2>
            <p>Welcome to the Data Analysis and Visualization Web App. This guide will help you understand what each button and function does in the app.</p>
            <h3>Overview</h3>
            <p>This web app allows you to upload a CSV file, filter the data, visualize it in various ways, and export the filtered data.</p>
            <h3>Uploading Data</h3>
            <p><b>Upload CSV File:</b> Click the "Choose a CSV file" button to upload your data file. The app supports CSV files with a semi-colon (;) delimiter.</p>
            <h3>Data Preview</h3>
            <p><b>Data Preview:</b> Once the file is uploaded, you will see a preview of the first few rows of your data.</p>
            <h3>Filtering Data</h3>
            <p><b>Select Column to Filter By:</b> Choose a column from the dropdown to filter the data by specific values.</p>
            <p><b>Select Values for Column:</b> Choose the values you want to include from the selected column.</p>
            <p><b>Add More Filters:</b> Click the "Yes" radio button to add more filters, otherwise select "No" to proceed.</p>
            <h3>Data Visualization</h3>
            <p><b>Generate Plot:</b></p>
            <ul>
                <li><b>Select X-axis Column:</b> Choose the column to be used on the X-axis of the plot.</li>
                <li><b>Select Y-axis Column:</b> Choose the column to be used on the Y-axis of the plot.</li>
                <li><b>Select Plot Type:</b> Choose between 'line' or 'bar' plot types. A line plot is used for showing trends over time or continuous data, while a bar plot is used for comparing discrete categories.</li>
                <li><b>Generate Plot:</b> Click this button to create the plot based on the selected columns and plot type.</li>
            </ul>
            <p><b>Export Filtered Data:</b> Click this button to export the filtered data as a CSV file.</p>
            <p><b>Show Counts:</b></p>
            <ul>
                <li><b>Select Column:</b> Choose a column to display the count of its unique values. This shows how many times each unique value appears in the selected column.</li>
                <li><b>Show Counts:</b> Click this button to display the value counts and generate a bar plot of these counts.</li>
            </ul>
            <p><b>Show Trend:</b></p>
            <ul>
                <li><b>Select Date Column:</b> Choose a column containing date values. This is used for trend analysis over time.</li>
                <li><b>Select Value Column:</b> Choose a column with numeric values to analyze trends over time.</li>
                <li><b>Show Trend:</b> Click this button to display the trend over time. This shows how the values change over the selected time period.</li>
            </ul>
            <p><b>Show Descriptive Statistics:</b></p>
            <ul>
                <li><b>Select Column:</b> Choose a column to display its descriptive statistics. Descriptive statistics summarize the main features of a dataset, including measures such as mean, median, standard deviation, and more.</li>
                <li><b>Show Descriptive Statistics:</b> Click this button to display summary statistics and a bar plot of these statistics.</li>
            </ul>
            <p><b>Show Correlation Matrix:</b> Click this button to display and plot the correlation matrix of the numeric columns in the data. A correlation matrix shows the relationship between pairs of variables, indicating how they move together.</p>
            <p><b>Show Distribution Plot:</b></p>
            <ul>
                <li><b>Select Column:</b> Choose a column to display the distribution of its values. This shows how frequently each value appears in the column.</li>
                <li><b>Show Distribution Plot:</b> Click this button to display a histogram of the column's values. A histogram is a graphical representation of the distribution of numerical data.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
