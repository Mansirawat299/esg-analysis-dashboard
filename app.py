import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import seaborn as sns
import numpy as np

# Page configuration
st.set_page_config(
    page_title="ESG Analytics Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .subheader {
        font-size: 1.5rem;
        color: #2e86ab;
        border-bottom: 2px solid #2e86ab;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Color scheme
COLOR_SCHEME = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'tertiary': '#2ca02c',
    'quaternary': '#d62728',
    'background': '#f0f2f6',
    'card': '#ffffff'
}

# Title and description
st.markdown('<p class="main-header">🌍 ESG Analytics Dashboard</p>', unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #666; margin-bottom: 2rem;'>
    Comprehensive Environmental, Social, and Governance performance analysis across companies and industries
</div>
""", unsafe_allow_html=True)

# Load the dataset
uploaded_file = st.file_uploader("📁 Upload Company ESG Dataset (CSV format)", type="csv", 
                                 help="Upload your company_esg_financial_dataset.csv file")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    st.warning("⚠️ Please upload the dataset to proceed.")
    st.info("💡 If you don't have the dataset, the dashboard will display sample visualizations once data is uploaded.")
    st.stop()

# Handle missing values
if 'GrowthRate' in df.columns:
    df['GrowthRate'] = df['GrowthRate'].fillna(df['GrowthRate'].median())

# Function to safely get column names
def get_column_name(possible_names, df):
    for name in possible_names:
        if name in df.columns:
            return name
    return None

# Function to prepare size column (handle negative values)
def prepare_size_column(column_data, column_name):
    """Convert column data to positive values suitable for size encoding"""
    if column_data.min() < 0:
        # Shift all values to positive range
        min_val = column_data.min()
        size_data = column_data - min_val + 1  # Add 1 to avoid zero sizes
        st.sidebar.info(f"⚠️ {column_name} contains negative values. Adjusted for visualization.")
        return size_data
    elif column_data.min() == 0:
        # Add small value to avoid zero sizes
        return column_data + 1
    else:
        return column_data

# Get actual column names
company_col = get_column_name(['Company', 'CompanyName', 'CompanyID'], df)
industry_col = get_column_name(['Industry', 'Sector', 'BusinessSector'], df)
region_col = get_column_name(['Region', 'Country', 'Geography'], df)
year_col = get_column_name(['Year', 'FiscalYear', 'ReportingYear'], df)

# Sidebar with filters
st.sidebar.markdown("## 🔍 Filters & Controls")

# Year filter
if year_col:
    years = sorted(df[year_col].unique())
    selected_years = st.sidebar.slider(
        "Select Year Range",
        min_value=int(min(years)),
        max_value=int(max(years)),
        value=(int(min(years)), int(max(years)))
    )
    df = df[(df[year_col] >= selected_years[0]) & (df[year_col] <= selected_years[1])]

# Industry filter
if industry_col:
    industries = st.sidebar.multiselect(
        "Select Industries",
        options=df[industry_col].unique(),
        default=df[industry_col].unique()[:5] if len(df[industry_col].unique()) > 5 else df[industry_col].unique()
    )
    df = df[df[industry_col].isin(industries)]

# Region filter
if region_col:
    regions = st.sidebar.multiselect(
        "Select Regions",
        options=df[region_col].unique(),
        default=df[region_col].unique()
    )
    df = df[df[region_col].isin(regions)]

# Prepare size columns if they exist
if 'ProfitMargin' in df.columns:
    df['ProfitMargin_Size'] = prepare_size_column(df['ProfitMargin'], 'ProfitMargin')
if 'Revenue' in df.columns:
    df['Revenue_Size'] = prepare_size_column(df['Revenue'], 'Revenue')
if 'CarbonEmissions' in df.columns:
    df['CarbonEmissions_Size'] = prepare_size_column(df['CarbonEmissions'], 'CarbonEmissions')

# Key metrics at the top
st.markdown("## 📊 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if 'ESG_Overall' in df.columns:
        avg_esg = df['ESG_Overall'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h3>🌱 Avg ESG Score</h3>
            <h2>{avg_esg:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

with col2:
    if 'Revenue' in df.columns:
        total_rev = df['Revenue'].sum() / 1e9  # Convert to billions
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
            <h3>💰 Total Revenue</h3>
            <h2>${total_rev:.1f}B</h2>
        </div>
        """, unsafe_allow_html=True)

with col3:
    if 'CarbonEmissions' in df.columns:
        avg_carbon = df['CarbonEmissions'].mean()
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #fc466b 0%, #3f5efb 100%);">
            <h3>🏭 Avg Carbon Emissions</h3>
            <h2>{avg_carbon:.0f}</h2>
        </div>
        """, unsafe_allow_html=True)

with col4:
    if 'ProfitMargin' in df.columns:
        avg_profit = df['ProfitMargin'].mean()
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #fdbb2d 0%, #22c1c3 100%);">
            <h3>📈 Avg Profit Margin</h3>
            <h2>{avg_profit:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)

# Create tabs for better organization
tab1, tab2, tab3, tab4 = st.tabs(["📈 ESG Overview", "🌿 Environmental", "👥 Social & Governance", "📋 Data Details"])

with tab1:
    st.markdown('<p class="subheader">ESG Performance Overview</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Distribution of ESG Overall Scores")
        if 'ESG_Overall' in df.columns:
            fig1 = px.histogram(df, x='ESG_Overall', nbins=30, 
                               color_discrete_sequence=[COLOR_SCHEME['primary']],
                               marginal="violin", 
                               title="Distribution of ESG Overall Scores",
                               template="plotly_white")
            fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("2. ESG Scores by Industry")
        if 'ESG_Overall' in df.columns and industry_col:
            fig2 = px.box(df, x=industry_col, y='ESG_Overall', 
                         color=industry_col,
                         title="ESG Overall Scores by Industry",
                         template="plotly_white")
            fig2.update_layout(xaxis_tickangle=45, showlegend=False,
                              plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2, use_container_width=True)
    
    st.subheader("3. Revenue vs ESG Overall Score")
    if 'Revenue' in df.columns and 'ESG_Overall' in df.columns:
        # Prepare hover data safely
        hover_data = {}
        if company_col:
            hover_data[company_col] = True
        if region_col:
            hover_data[region_col] = True
        
        # Use the prepared size column
        size_col = 'ProfitMargin_Size' if 'ProfitMargin_Size' in df.columns else None
        
        fig3 = px.scatter(df, x='Revenue', y='ESG_Overall', 
                         color=industry_col if industry_col else None,
                         size=size_col,
                         hover_data=hover_data if hover_data else None,
                         title="Revenue vs ESG Overall Score",
                         template="plotly_white")
        fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig3, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("4. Average ESG Scores Over Years")
        if 'ESG_Overall' in df.columns and year_col:
            year_mean = df.groupby(year_col)['ESG_Overall'].mean().reset_index()
            fig4 = px.line(year_mean, x=year_col, y='ESG_Overall', 
                          color_discrete_sequence=[COLOR_SCHEME['secondary']],
                          markers=True,
                          title="Average ESG Overall Scores Over Years",
                          template="plotly_white")
            fig4.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig4, use_container_width=True)
    
    with col4:
        st.subheader("5. Average ESG Scores by Region")
        if 'ESG_Overall' in df.columns and region_col:
            region_mean = df.groupby(region_col)['ESG_Overall'].mean().reset_index().sort_values('ESG_Overall', ascending=False)
            fig5 = px.bar(region_mean, x=region_col, y='ESG_Overall',
                         color='ESG_Overall',
                         color_continuous_scale='Viridis',
                         title="Average ESG Overall Scores by Region",
                         template="plotly_white")
            fig5.update_layout(xaxis_tickangle=45, 
                              plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig5, use_container_width=True)

with tab2:
    st.markdown('<p class="subheader">Environmental Performance Metrics</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("6. Carbon Emissions vs ESG Environmental Score")
        if 'CarbonEmissions' in df.columns and 'ESG_Environmental' in df.columns:
            hover_data_env = {}
            if company_col:
                hover_data_env[company_col] = True
            if region_col:
                hover_data_env[region_col] = True
                
            fig6 = px.scatter(df, x='CarbonEmissions', y='ESG_Environmental', 
                             color=industry_col if industry_col else None,
                             size='Revenue_Size' if 'Revenue_Size' in df.columns else None,
                             hover_data=hover_data_env if hover_data_env else None,
                             title="Carbon Emissions vs ESG Environmental Score",
                             template="plotly_white")
            fig6.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig6, use_container_width=True)
    
    with col2:
        st.subheader("7. Water Usage by Industry")
        if 'WaterUsage' in df.columns and industry_col:
            fig8 = px.box(df, x=industry_col, y='WaterUsage', 
                         color=industry_col,
                         title="Water Usage by Industry",
                         template="plotly_white")
            fig8.update_layout(xaxis_tickangle=45, showlegend=False,
                              plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig8, use_container_width=True)
    
    st.subheader("8. Energy Consumption vs ESG Environmental Score by Region")
    if 'EnergyConsumption' in df.columns and 'ESG_Environmental' in df.columns and region_col:
        hover_data_energy = {}
        if company_col:
            hover_data_energy[company_col] = True
        if industry_col:
            hover_data_energy[industry_col] = True
            
        fig9 = px.scatter(df, x='EnergyConsumption', y='ESG_Environmental', 
                         color=region_col,
                         size='CarbonEmissions_Size' if 'CarbonEmissions_Size' in df.columns else None,
                         symbol=region_col,
                         hover_data=hover_data_energy if hover_data_energy else None,
                         title="Energy Consumption vs ESG Environmental Score by Region",
                         template="plotly_white")
        fig9.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig9, use_container_width=True)

with tab3:
    st.markdown('<p class="subheader">Social & Governance Metrics</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("9. Profit Margin vs ESG Governance Score")
        if 'ProfitMargin' in df.columns and 'ESG_Governance' in df.columns:
            hover_data_gov = {}
            if company_col:
                hover_data_gov[company_col] = True
            if region_col:
                hover_data_gov[region_col] = True
                
            fig7 = px.scatter(df, x='ProfitMargin', y='ESG_Governance', 
                             color=industry_col if industry_col else None,
                             size='Revenue_Size' if 'Revenue_Size' in df.columns else None,
                             hover_data=hover_data_gov if hover_data_gov else None,
                             title="Profit Margin vs ESG Governance Score",
                             template="plotly_white")
            fig7.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig7, use_container_width=True)
    
    with col2:
        # Additional social metric if available
        if 'ESG_Social' in df.columns and region_col:
            st.subheader("Social Performance by Region")
            social_region = df.groupby(region_col)['ESG_Social'].mean().reset_index().sort_values('ESG_Social', ascending=False)
            fig_social = px.bar(social_region, x=region_col, y='ESG_Social',
                              color='ESG_Social',
                              color_continuous_scale='Blues',
                              title="Average Social Scores by Region",
                              template="plotly_white")
            fig_social.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_social, use_container_width=True)
    
    st.subheader("10. Correlation Heatmap: Key Metrics")
    # Select numeric columns for correlation
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    important_cols = [col for col in ['ESG_Overall', 'Revenue', 'CarbonEmissions', 'WaterUsage', 
                                     'ProfitMargin', 'ESG_Environmental', 'ESG_Social', 'ESG_Governance'] 
                     if col in numeric_cols]
    
    if len(important_cols) > 1:
        corr_matrix = df[important_cols].corr()
        fig10 = ff.create_annotated_heatmap(
            z=corr_matrix.values,
            x=list(corr_matrix.columns),
            y=list(corr_matrix.index),
            annotation_text=corr_matrix.round(2).values,
            colorscale='RdBu',
            showscale=True
        )
        fig10.update_layout(title="Correlation Heatmap of Key Metrics",
                           height=600)
        st.plotly_chart(fig10, use_container_width=True)

with tab4:
    st.markdown('<p class="subheader">Dataset Overview & Details</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Dataset Summary")
        st.write(f"**Total Records:** {len(df)}")
        st.write(f"**Total Companies:** {df[company_col].nunique() if company_col else 'N/A'}")
        st.write(f"**Industries:** {df[industry_col].nunique() if industry_col else 'N/A'}")
        st.write(f"**Regions:** {df[region_col].nunique() if region_col else 'N/A'}")
        if year_col:
            st.write(f"**Time Period:** {df[year_col].min()} - {df[year_col].max()}")
    
    with col2:
        st.subheader("🔍 Data Quality")
        missing_data = df.isnull().sum().sum()
        total_cells = df.size
        completeness = ((total_cells - missing_data) / total_cells) * 100
        st.write(f"**Data Completeness:** {completeness:.1f}%")
        st.write(f"**Missing Values:** {missing_data}")
        st.write(f"**Total Columns:** {len(df.columns)}")
        
        # Show negative value warnings
        negative_cols = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].min() < 0:
                negative_cols.append(col)
        if negative_cols:
            st.write(f"**Columns with negative values:** {', '.join(negative_cols)}")
    
    st.subheader("📊 Data Preview")
    st.dataframe(df.head(10), use_container_width=True)
    
    st.subheader("📈 Column Information")
    st.write(df.dtypes)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>ESG Analytics Dashboard • Built with Streamlit • Promoting Sustainable Business Practices</p>
</div>
""", unsafe_allow_html=True)