import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 页面与全局设置
st.set_page_config(page_title="周报数据看板", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600&display=swap');
    .stApp { background-color: #FDF9FA; font-family: 'Inter', sans-serif; }
    h1 { font-family: 'Playfair Display', serif; color: #1A1A1A; font-size: 2.8rem !important; margin-bottom: 0px !important; padding-bottom: 0px !important; }
    .subtitle { color: #666666; font-size: 1rem; margin-bottom: 2rem; }
    .metric-card { background-color: #FFFFFF; border-radius: 16px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); border: 1px solid rgba(0,0,0,0.02); margin-bottom: 16px; }
    .metric-title { color: #7A7A7A; font-size: 0.9rem; font-weight: 500; display: flex; align-items: center; gap: 8px;}
    .metric-value { color: #1A1A1A; font-size: 2rem; font-weight: 700; margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

# 2. 读取并处理 Google 表格数据
@st.cache_data(ttl=600) # 缓存10分钟，避免频繁请求
def load_data():
    # 将共享链接转换为 CSV 导出链接
    sheet_url = "https://docs.google.com/spreadsheets/d/1eOy9c2EIAD1mGmy7LqF5O_9ITQNga21F4fWJ24Bztwc/export?format=csv&gid=0"
    df = pd.read_csv(sheet_url)
    
    # 转置表格：将指标名变成列，日期变成行
    df = df.set_index(df.columns[0]).T
    df.reset_index(inplace=True)
    df.rename(columns={'index': '日期'}, inplace=True)
    
    # 数据清洗：去除 $ 和 % 以及逗号，转换为数字类型
    for col in df.columns:
        if col != '日期':
            df[col] = df[col].astype(str).str.replace('$', '', regex=False)
            df[col] = df[col].str.replace(',', '', regex=False)
            df[col] = df[col].str.replace('%', '', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

df = load_data()

# 3. 侧边栏与周筛选
with st.sidebar:
    st.markdown("### ⚙️ 数据看板控制台")
    st.divider()
    # 提供周筛选下拉菜单，默认选择最新的一周（最后一行）
    selected_week = st.selectbox("📅 选择查看的周期", df['日期'].tolist(), index=len(df)-1)
    
    st.markdown("<br><br><span style='color:gray;font-size:0.8rem;'>Data auto-synced from Google Sheets</span>", unsafe_allow_html=True)

# 过滤出选中周的数据
current_data = df[df['日期'] == selected_week].iloc[0]

# 4. 主视觉区
st.markdown("<h1>Weekly Analytics Dashboard</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='subtitle'>Track. Analyze. Optimize. Grow. ✨ | 当前视图：{selected_week}</div>", unsafe_allow_html=True)

# 5. 核心指标卡片区 (提取 superset 销售额, 转化率, GA4流量, GSC点击)
st.markdown("##### 💡 核心指标总览")
col1, col2, col3, col4 = st.columns(4)

def create_card(title, value, suffix="", icon="👁️"):
    return f"""
    <div class="metric-card">
        <div class="metric-title">{icon} {title}</div>
        <div class="metric-value">{value}{suffix}</div>
    </div>
    """

with col1: st.markdown(create_card("销售额", f"${current_data['销售额(superset)']:.2f}", icon="💰"), unsafe_allow_html=True)
with col2: st.markdown(create_card("转化率", f"{current_data['转化率(superset)']:.2f}", suffix="%", icon="📈"), unsafe_allow_html=True)
with col3: st.markdown(create_card("总流量 (GA4)", f"{int(current_data['流量(GA4)'])}", icon="👥"), unsafe_allow_html=True)
with col4: st.markdown(create_card("总点击 (GSC)", f"{int(current_data['点击(GSC)'])}", icon="🖱️"), unsafe_allow_html=True)

# 6. 图表区
st.markdown("<br>", unsafe_allow_html=True)
col_chart1, col_chart2 = st.columns([6, 4])

with col_chart1:
    st.markdown("##### 📈 流量与点击趋势 (历史数据)")
    # 绘制历史趋势折线图
    fig1 = px.line(df, x='日期', y=['流量(GA4)', '点击(GSC)'], 
                   color_discrete_sequence=["#FF5E8E", "#9B72F0"])
    fig1.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=20, b=0))
    fig1.update_traces(mode='lines+markers', line=dict(width=3))
    st.plotly_chart(fig1, use_container_width=True)

with col_chart2:
    st.markdown("##### 🍰 流量结构分布 (选中周)")
    # 提取 Blog 和 站内的流量画饼图
    donut_data = pd.DataFrame({
        'Source': ['Blog流量', '站内流量'],
        'Value': [current_data['流量(Blog)'], current_data['流量(站内)']]
    })
    fig2 = px.pie(donut_data, values='Value', names='Source', hole=0.6, 
                  color_discrete_sequence=["#FF5E8E", "#9B72F0"])
    fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig2, use_container_width=True)
