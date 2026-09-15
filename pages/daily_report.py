import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. 页面配置
st.set_page_config(page_title="日报数据看板", layout="wide")

# 2. CSS 样式 (高级深蓝系)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp { background-color: #F4F7FC; font-family: 'Inter', sans-serif; }
    h1 { color: #1E3A8A; font-size: 2.2rem !important; font-weight: 700; margin-bottom: 0px !important; }
    .subtitle { color: #64748B; font-size: 0.95rem; margin-bottom: 1.5rem; }
    .metric-card { 
        background-color: #FFFFFF; border-radius: 12px; padding: 20px; 
        box-shadow: 0 2px 12px rgba(30, 58, 138, 0.04); border: 1px solid #E2E8F0; 
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .metric-title { color: #64748B; font-size: 0.9rem; font-weight: 600; margin-bottom: 10px;}
    .chart-container {
        background-color: #FFFFFF; border-radius: 12px; padding: 16px;
        box-shadow: 0 2px 12px rgba(30, 58, 138, 0.04); border: 1px solid #E2E8F0; margin-bottom: 24px;
    }
</style>
""", unsafe_allow_html=True)

COLORS = ["#2D5B93", "#F4A261", "#8CA8D1", "#E07A5F", "#3D405B"]

# 3. 读取并清洗数据 (日报格式)
@st.cache_data(ttl=600)
def load_daily_data():
    excel_url = "https://docs.google.com/spreadsheets/d/1eOy9c2EIAD1mGmy7LqF5O_9ITQNga21F4fWJ24Bztwc/export?format=xlsx"
    # 读取名为“日报”的 Sheet
    df = pd.read_excel(excel_url, sheet_name="日报")
    
    # 转置表格：第一列变表头，原本的表头（日期）变行索引
    df = df.set_index(df.columns[0]).T
    df.reset_index(inplace=True)
    df.rename(columns={'index': '日期'}, inplace=True)
    
    # 转换日期格式，剔除非日期数据
    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
    df = df.dropna(subset=['日期']).sort_values('日期')
    
    # 数据清洗：去除 $、%、逗号，转为数字
    for col in df.columns:
        if col != '日期':
            df[col] = df[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.replace('%', '', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    return df

try:
    df = load_daily_data()
except Exception as e:
    st.error("⚠️ 读取数据失败，请检查表格中是否有名为 '日报' 的 Sheet。")
    st.stop()

# 定义基准日期 (以数据表中的最新日期为准，防止数据没更新导致空白)
max_date = df['日期'].max().date()
min_date = df['日期'].min().date()

# 4. 侧边栏：全局设置与目标输入
with st.sidebar:
    st.markdown("### ⚙️ 看板全局设置")
    
    # 全局时间控制 (默认最近30天)
    default_start = max_date - timedelta(days=30)
    global_date_range = st.date_input(
        "📅 全局时间范围",
        value=(default_start, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    st.divider()
    st.markdown("### 🎯 本月目标设定")
    st.caption("用于计算顶部的进度条完成率")
    target_sales = st.number_input("本月 Superset SEO 销售额目标 ($)", value=50000, step=1000)
    target_traffic = st.number_input("本月 SEO 流量目标", value=100000, step=1000)

# 解析全局时间
if len(global_date_range) == 2:
    g_start, g_end = global_date_range
else:
    g_start, g_end = global_date_range[0], global_date_range[0]

# 5. 页面头部
st.markdown("<h1>Daily Analytics Board</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='subtitle'>Global Range: {g_start} to {g_end} | Real-time Daily Tracking</div>", unsafe_allow_html=True)

# ----------------- 顶部：当月进度条 -----------------
st.markdown("##### 🏆 自然月累计进度 (从本月1号至最新数据)")

# 自动计算当月数据
current_month_start = pd.to_datetime(max_date).replace(day=1)
df_current_month = df[df['日期'] >= current_month_start]

# 累计当月数值
current_sales = df_current_month['Superset SEO销售额'].sum()
current_traffic = df_current_month['SEO流量'].sum()

def create_progress_ring(actual, goal, color, prefix=""):
    rate = actual / goal if goal > 0 else 0
    display_pct = f"{rate * 100:.1f}%"
    rate_capped = min(rate, 1.0)
    fig = go.Figure(data=[go.Pie(
        values=[rate_capped, 1 - rate_capped], hole=0.75,
        marker_colors=[color, '#E2E8F0'], textinfo='none', hoverinfo='none', sort=False
    )])
    fig.update_layout(
        showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=140,
        annotations=[dict(text=f"<span style='font-size:1.5rem;font-weight:700;color:#1E3A8A'>{display_pct}</span>", x=0.5, y=0.5, showarrow=False)],
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown('<div class="metric-card"><div class="metric-title">💰 SEO 销售额进度</div>', unsafe_allow_html=True)
    st.plotly_chart(create_progress_ring(current_sales, target_sales, COLORS[0]), use_container_width=True)
    st.markdown(f"<div style='color:#64748B;font-size:0.85rem;margin-top:5px;'>已完成: ${current_sales:,.0f} / ${target_sales:,.0f}</div></div>", unsafe_allow_html=True)
with c2:
    st.markdown('<div class="metric-card"><div class="metric-title">🌐 SEO 流量进度</div>', unsafe_allow_html=True)
    st.plotly_chart(create_progress_ring(current_traffic, target_traffic, COLORS[1]), use_container_width=True)
    st.markdown(f"<div style='color:#64748B;font-size:0.85rem;margin-top:5px;'>已完成: {current_traffic:,.0f} / {target_traffic:,.0f}</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------- 图表渲染辅助函数 -----------------
# 过滤数据的函数 (根据图表的独立选择器)
def get_filtered_df(local_filter_val):
    if local_filter_val == "跟随全局":
        return df[(df['日期'].dt.date >= g_start) & (df['日期'].dt.date <= g_end)]
    elif local_filter_val == "最近7天":
        return df[df['日期'].dt.date >= (max_date - timedelta(days=6))]
    elif local_filter_val == "最近30天":
        return df[df['日期'].dt.date >= (max_date - timedelta(days=29))]
    elif local_filter_val == "本月 (自然月)":
        return df[df['日期'] >= current_month_start]
    else: # 全部
        return df

# 渲染卡片和图表的通用模板
def render_chart_container(title, cols, chart_key, is_area=False):
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    # 头部：左侧标题，右侧独立时间选择器
    head_col1, head_col2 = st.columns([7, 3])
    with head_col1:
        st.markdown(f"<span style='font-weight:600; color:#1E3A8A; font-size:1.1rem;'>{title}</span>", unsafe_allow_html=True)
    with head_col2:
        local_range = st.selectbox(" ", ["跟随全局", "最近7天", "最近30天", "本月 (自然月)", "全部"], 
                                   key=chart_key, label_visibility="collapsed")
    
    # 获取过滤后的数据
    plot_df = get_filtered_df(local_range)
    
    # 画图
    if is_area:
        fig = px.area(plot_df, x='日期', y=cols, color_discrete_sequence=COLORS)
    else:
        fig = px.line(plot_df, x='日期', y=cols, color_discrete_sequence=COLORS)
        fig.update_traces(mode='lines+markers', line=dict(width=3))
        
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_yaxes(rangemode="tozero", gridcolor='#F1F5F9')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------- 图表展示区 -----------------

# 第一排：销售额对比
row1_c1, row1_c2 = st.columns(2)
with row1_c1:
    render_chart_container("🛒 SEO 销售额对比 (Superset vs GA4)", ['Superset SEO销售额', 'GA4 SEO销售额'], "chart_seo_sales")
with row1_c2:
    render_chart_container("💰 网站总销售额对比 (Superset vs GA4)", ['Superset 总销售额', 'GA4 网站总销售额'], "chart_total_sales")

# 第二排：流量明细
row2_c1, row2_c2 = st.columns(2)
with row2_c1:
    render_chart_container("👥 SEO 流量来源结构", ['SEO流量', 'SEO 站内流量', 'SEO Blog流量'], "chart_seo_traffic")
with row2_c2:
    render_chart_container("🌐 网站总流量与跳出率", ['网站总流量', '跳出率'], "chart_total_traffic")

# 第三排：AI Assistant (特殊双轴图表，需要单独画)
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
head_col1, head_col2 = st.columns([7, 3])
with head_col1:
    st.markdown("<span style='font-weight:600; color:#1E3A8A; font-size:1.1rem;'>🤖 AI Assistant 销售额与流量</span>", unsafe_allow_html=True)
with head_col2:
    local_range_ai = st.selectbox(" ", ["跟随全局", "最近7天", "最近30天", "本月 (自然月)", "全部"], key="chart_ai", label_visibility="collapsed")

plot_df_ai = get_filtered_df(local_range_ai)
fig_ai = go.Figure()
# 柱状图：销售额
fig_ai.add_trace(go.Bar(x=plot_df_ai['日期'], y=plot_df_ai['AI Assistant 销售额'], name='销售额 (Bar)', marker_color=COLORS[0]))
# 折线图：流量
fig_ai.add_trace(go.Scatter(x=plot_df_ai['日期'], y=plot_df_ai['AI Assistant 流量'], name='流量 (Line)', yaxis='y2', line=dict(color=COLORS[1], width=3), mode='lines+markers'))

fig_ai.update_layout(
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=10, b=0),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    yaxis=dict(title='销售额', rangemode='tozero', gridcolor='#F1F5F9'),
    yaxis2=dict(title='流量', overlaying='y', side='right', rangemode='tozero', showgrid=False)
)
st.plotly_chart(fig_ai, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# 第四排：收录数据
row4_c1, row4_c2 = st.columns(2)
with row4_c1:
    render_chart_container("📑 网站收录情况", ['收录'], "chart_index", is_area=True)
with row4_c2:
    render_chart_container("📝 Blog 收录情况", ['Blog 收录'], "chart_blog_index", is_area=True)

# 第五排：外链数据
row5_c1, row5_c2 = st.columns(2)
with row5_c1:
    render_chart_container("🔗 外链总数", ['外链'], "chart_backlinks", is_area=True)
with row5_c2:
    render_chart_container("🌍 外链域名广度", ['外链域名广度'], "chart_domains", is_area=True)
