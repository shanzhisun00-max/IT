import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. 页面配置
st.set_page_config(page_title="日报数据看板", layout="wide")

# 2. 注入深空蓝色系 UI 的 CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* 背景色：极浅的灰蓝色 */
    .stApp { background-color: #F4F7FC; font-family: 'Inter', sans-serif; }
    
    /* 标题：深藏青色 */
    h1 { color: #1E3A8A; font-size: 2.4rem !important; font-weight: 700; margin-bottom: 0px !important; }
    .subtitle { color: #64748B; font-size: 0.95rem; margin-bottom: 2rem; }
    
    /* 卡片样式：硬朗圆角(12px)，极淡描边 */
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
        align-items: center; /* 进度条卡片居中对齐 */
    }
    .metric-title { color: #64748B; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px;}
    .progress-text { color: #64748B; font-size: 0.85rem; margin-top: -10px; font-weight: 500;}
</style>
""", unsafe_allow_html=True)

# 核心配色：深蓝 (主色) 和 亮橘色 (辅助色)
COLOR_SALES = "#2D5B93" 
COLOR_TRAFFIC = "#F4A261"

# 3. 读取 Excel 数据 (指定读取月份数据的 Sheet)
@st.cache_data(ttl=600)
def load_monthly_data():
    # 注意链接里的 format 改成了 xlsx
    excel_url = "https://docs.google.com/spreadsheets/d/1eOy9c2EIAD1mGmy7LqF5O_9ITQNga21F4fWJ24Bztwc/export?format=xlsx"
    
    df = pd.read_excel(excel_url, sheet_name="月报")
    
    # 同样进行转置清洗
    df = df.set_index(df.columns[0]).T
    df.reset_index(inplace=True)
    df.rename(columns={'index': '月份'}, inplace=True)
    
    for col in df.columns:
        if col != '月份':
            df[col] = df[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.replace('%', '', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

try:
    df_month = load_monthly_data()
    months = df_month['月份'].tolist()
except Exception as e:
    st.error("⚠️ 读取数据失败，请检查 Google 表格中是否包含名为 '月度数据' 的工作表，或者是否忘记在 requirements.txt 中添加 openpyxl。")
    st.stop()

# 4. 侧边栏：月份筛选
with st.sidebar:
    st.markdown("### ⚙️ 日报控制台")
    st.divider()
    selected_month = st.selectbox("📅 选择目标月份", months, index=len(months)-1)

# 获取选中月份的数据
current_month_data = df_month[df_month['月份'] == selected_month].iloc[0]

# 5. 页面头部
st.markdown("<h1>Daily Performance</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='subtitle'>Real-time tracking and daily insights. | 当前筛选：{selected_month}</div>", unsafe_allow_html=True)


# 6. 核心功能：生成高级环形进度条
def create_progress_ring(actual, goal, color):
    # 计算进度并限制最高 100%（防止圆环画爆）
    rate = actual / goal if goal > 0 else 0
    display_pct = f"{rate * 100:.1f}%"
    rate_capped = min(rate, 1.0) 
    
    fig = go.Figure(data=[go.Pie(
        values=[rate_capped, 1 - rate_capped],
        hole=0.75, # 调整空心圆的粗细
        marker_colors=[color, '#E2E8F0'], # 填充色与底色
        textinfo='none', hoverinfo='none', direction='clockwise', sort=False
    )])
    
    fig.update_layout(
        showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=160,
        annotations=[dict(text=f"<span style='font-size:1.8rem;font-weight:700;color:#0F172A'>{display_pct}</span>", x=0.5, y=0.5, showarrow=False)],
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig

# 7. 渲染顶部目标卡片区 (分配两列给卡片，剩余两列留空以控制尺寸)
st.markdown("##### 🎯 本月目标达成进度")
c1, c2, c3, c4 = st.columns(4, gap="large")

with c1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-title">💰 销售目标完成率</div>', unsafe_allow_html=True)
    
    actual_sales = current_month_data['销售实际完成']
    goal_sales = current_month_data['销售目标']
    st.plotly_chart(create_progress_ring(actual_sales, goal_sales, COLOR_SALES), use_container_width=True)
    
    st.markdown(f'<div class="progress-text">${actual_sales:,.2f} / ${goal_sales:,.2f}</div></div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-title">🌐 流量目标完成率</div>', unsafe_allow_html=True)
    
    actual_traffic = current_month_data['流量实际完成']
    goal_traffic = current_month_data['流量目标']
    st.plotly_chart(create_progress_ring(actual_traffic, goal_traffic, COLOR_TRAFFIC), use_container_width=True)
    
    st.markdown(f'<div class="progress-text">{int(actual_traffic):,} / {int(goal_traffic):,}</div></div>', unsafe_allow_html=True)
