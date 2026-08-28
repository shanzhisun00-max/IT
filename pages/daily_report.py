import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. 页面配置 (注意：子页面同样需要配置)
st.set_page_config(page_title="日报数据看板", layout="wide")

# 2. 注入新版蓝色系 UI 的 CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* 背景色改为极浅的灰蓝色 */
    .stApp { background-color: #F4F7FC; font-family: 'Inter', sans-serif; }
    
    /* 标题改为深藏青色 */
    h1 { color: #1E3A8A; font-size: 2.4rem !important; font-weight: 700; margin-bottom: 0px !important; }
    .subtitle { color: #64748B; font-size: 0.95rem; margin-bottom: 2rem; }
    
    /* 卡片样式：更硬朗的圆角(12px)，极淡的描边 */
    .metric-card { 
        background-color: #FFFFFF; 
        border-radius: 12px; 
        padding: 20px; 
        box-shadow: 0 2px 12px rgba(30, 58, 138, 0.04); 
        border: 1px solid #E2E8F0; 
        margin-bottom: 16px; 
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-title { color: #64748B; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;}
    .metric-value { color: #0F172A; font-size: 2rem; font-weight: 700; margin: 0 0 4px 0; line-height: 1.1;}
    .metric-trend { font-size: 0.8rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# 核心配色：深蓝、浅蓝、亮橘色、灰蓝
COLORS = ["#2D5B93", "#8CA8D1", "#F4A261", "#A9BEE8"]

# 3. 页面头部
st.markdown("<h1>Daily Performance</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Real-time tracking and daily insights.</div>", unsafe_allow_html=True)

# 4. 模拟核心指标区 (暂时用假数据占位)
st.markdown("##### 📊 今日核心指标 (示例)")
def create_daily_card(title, value, trend_val, is_up=True):
    trend_color = "#10B981" if is_up else "#EF4444"
    trend_symbol = "↑" if is_up else "↓"
    return f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-trend" style="color: {trend_color};">{trend_symbol} {trend_val} vs 昨日</div>
    </div>
    """

c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(create_daily_card("Organic Traffic", "2,159", "12.5%"), unsafe_allow_html=True)
with c2: st.markdown(create_daily_card("Cost Per Click", "$2.39", "3.2%", is_up=False), unsafe_allow_html=True)
with c3: st.markdown(create_daily_card("Keyword Rank", "459", "15%"), unsafe_allow_html=True)
with c4: st.markdown(create_daily_card("Conversion", "5.2%", "0.8%"), unsafe_allow_html=True)

# 5. 模拟图表区 (使用蓝色系)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("##### 📈 流量趋势")
# 生成假数据演示颜色
dates = pd.date_range(start='2026-08-01', periods=14)
df_dummy = pd.DataFrame({'Date': dates, 'Traffic': np.random.randint(1000, 3000, 14)})
fig = px.area(df_dummy, x='Date', y='Traffic', color_discrete_sequence=[COLORS[0]])
fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0, r=0, t=20, b=0),
    yaxis=dict(gridcolor='#F1F5F9')
)
fig.update_traces(fillcolor='rgba(45, 91, 147, 0.2)', line=dict(width=3)) # 半透明蓝色填充
st.plotly_chart(fig, use_container_width=True)
