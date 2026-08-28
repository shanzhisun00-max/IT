import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 页面与全局设置
st.set_page_config(page_title="周报数据看板", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600&display=swap');
    .stApp { background-color: #FDF9FA; font-family: 'Inter', sans-serif; }
    h1 { font-family: 'Playfair Display', serif; color: #1A1A1A; font-size: 2.8rem !important; margin-bottom: 0px !important; padding-bottom: 0px !important; }
    .subtitle { color: #666666; font-size: 1rem; margin-bottom: 2rem; }
    
    /* 核心修改：卡片尺寸缩小，上下间距增大 */
    .metric-card { 
        background-color: #FFFFFF; 
        border-radius: 16px; 
        padding: 12px; /* 内部留白缩小 */
        box-shadow: 0 4px 20px rgba(0,0,0,0.03); 
        border: 1px solid rgba(0,0,0,0.02); 
        margin-bottom: 20px; /* 卡片上下的间距变大 */
        max-width: 200px; /* 强制限制卡片最大宽度，让它显得更小 */
        display: flex;
        flex-direction: column;
        justify-content: center; 
    }
    /* 对应调小内部字号，防止溢出 */
    .metric-title { color: #7A7A7A; font-size: 0.75rem; font-weight: 500; display: flex; align-items: center; gap: 4px; margin-bottom: 6px;}
    .metric-value { color: #1A1A1A; font-size: 1.2rem; font-weight: 700; margin: 0 0 6px 0; line-height: 1.2;}
    .metric-trend { font-size: 0.7rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# 色板定义
COLORS = ["#FF5E8E", "#9B72F0", "#FFB6C1", "#C1A3FF", "#FFA07A"]

# 2. 读取并处理 Google 表格数据
@st.cache_data(ttl=600)
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1eOy9c2EIAD1mGmy7LqF5O_9ITQNga21F4fWJ24Bztwc/export?format=csv&gid=0"
    df = pd.read_csv(sheet_url)
    
    df = df.set_index(df.columns[0]).T
    df.reset_index(inplace=True)
    df.rename(columns={'index': '日期'}, inplace=True)
    
    for col in df.columns:
        if col != '日期':
            df[col] = df[col].astype(str).str.replace('$', '', regex=False)
            df[col] = df[col].str.replace(',', '', regex=False)
            df[col] = df[col].str.replace('%', '', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

df = load_data()
dates = df['日期'].tolist()

# 3. 侧边栏与时间筛选
with st.sidebar:
    st.markdown("### ⚙️ 数据看板控制台")
    st.divider()
    
    st.markdown("#### 📌 核心指标设置")
    selected_week = st.selectbox("选择要查看的单周", dates, index=len(dates)-1)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📈 趋势图时间范围")
    start_week, end_week = st.select_slider(
        "滑动选择图表展示周期",
        options=dates,
        value=(dates[0], dates[-1])
    )
    
    st.markdown("<br><br><span style='color:gray;font-size:0.8rem;'>Data auto-synced from Google Sheets</span>", unsafe_allow_html=True)

# 过滤图表数据
start_idx = dates.index(start_week)
end_idx = dates.index(end_week)
df_filtered = df.iloc[start_idx:end_idx+1]

current_idx = dates.index(selected_week)
current_data = df.iloc[current_idx]
prev_data = df.iloc[current_idx - 1] if current_idx > 0 else None

# 4. 主视觉区头部
st.markdown("<h1>Weekly Analytics Dashboard</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='subtitle'>Track. Analyze. Optimize. Grow. ✨ | 当前指标周：{selected_week}</div>", unsafe_allow_html=True)


# 5. 核心指标卡片区
st.markdown("##### 💡 核心指标总览")

def create_compare_card(title, current_val, prev_val, is_currency=False, is_percent=False, icon="👁️"):
    prefix = "$" if is_currency else ""
    suffix = "%" if is_percent else ""
    fmt_curr = f"{current_val:.2f}" if isinstance(current_val, float) else f"{int(current_val)}"
    
    if prev_val is not None:
        diff = current_val - prev_val
        trend_symbol = "↑" if diff > 0 else ("↓" if diff < 0 else "-")
        trend_color = "#4CAF50" if diff >= 0 else "#F44336"
        
        if is_percent:
            trend_text = f"{trend_symbol} {abs(diff):.2f}% vs 上周"
        else:
            pct_change = (diff / prev_val * 100) if prev_val != 0 else 0
            trend_text = f"{trend_symbol} {abs(pct_change):.1f}% vs 上周"
    else:
        trend_color = "#999999"
        trend_text = "无上周数据"

    return f"""
    <div class="metric-card">
        <div class="metric-title">{icon} {title}</div>
        <div class="metric-value">{prefix}{fmt_curr}{suffix}</div>
        <div class="metric-trend" style="color: {trend_color};">{trend_text}</div>
    </div>
    """

# 核心修改：在 st.columns 中加入 gap="large"，让左右间距彻底拉开
# --- 第一排 ---
r1 = st.columns(5, gap="large")
with r1[0]: st.markdown(create_compare_card("销售额 (Superset)", current_data['销售额(superset)'], prev_data['销售额(superset)'] if prev_data is not None else None, is_currency=True, icon="💰"), unsafe_allow_html=True)
with r1[1]: st.markdown(create_compare_card("流量 (GA4)", current_data['流量(GA4)'], prev_data['流量(GA4)'] if prev_data is not None else None, icon="🌐"), unsafe_allow_html=True)
with r1[2]: st.markdown(create_compare_card("流量 (Blog)", current_data['流量(Blog)'], prev_data['流量(Blog)'] if prev_data is not None else None, icon="📝"), unsafe_allow_html=True)
with r1[3]: st.markdown(create_compare_card("流量 (站内)", current_data['流量(站内)'], prev_data['流量(站内)'] if prev_data is not None else None, icon="🏠"), unsafe_allow_html=True)

# --- 第二排 ---
r2 = st.columns(5, gap="large")
with r2[0]: st.markdown(create_compare_card("点击 (GSC)", current_data['点击(GSC)'], prev_data['点击(GSC)'] if prev_data is not None else None, icon="🖱️"), unsafe_allow_html=True)
with r2[1]: st.markdown(create_compare_card("点击 (非品牌词)", current_data['点击(非品牌词)'], prev_data['点击(非品牌词)'] if prev_data is not None else None, icon="🔍"), unsafe_allow_html=True)
with r2[2]: st.markdown(create_compare_card("点击 (Blog)", current_data['点击(Blog)'], prev_data['点击(Blog)'] if prev_data is not None else None, icon="📝"), unsafe_allow_html=True)
with r2[3]: st.markdown(create_compare_card("点击 (非Blog)", current_data['点击(非Blog)'], prev_data['点击(非Blog)'] if prev_data is not None else None, icon="🏠"), unsafe_allow_html=True)
with r2[4]: st.markdown(create_compare_card("非品牌词BlogUTM", current_data['点击(非品牌词BlogUTM)'], prev_data['点击(非品牌词BlogUTM)'] if prev_data is not None else None, icon="🔗"), unsafe_allow_html=True)

# --- 第三排 ---
r3 = st.columns(5, gap="large")
with r3[0]: st.markdown(create_compare_card("销售额 (AI Assis)", current_data['销售额(AI Assistant)'], prev_data['销售额(AI Assistant)'] if prev_data is not None else None, is_currency=True, icon="🤖💰"), unsafe_allow_html=True)
with r3[1]: st.markdown(create_compare_card("流量 (AI Assis)", current_data['流量(AI Assistant)'], prev_data['流量(AI Assistant)'] if prev_data is not None else None, icon="🤖👥"), unsafe_allow_html=True)

# --- 第四排 ---
r4 = st.columns(5, gap="large")
with r4[0]: st.markdown(create_compare_card("AI Perf (总展示)", current_data['AI Performance(总展示)'], prev_data['AI Performance(总展示)'] if prev_data is not None else None, icon="✨"), unsafe_allow_html=True)
with r4[1]: st.markdown(create_compare_card("AI Perf (非Blog)", current_data['AI Performance(非Blog)'], prev_data['AI Performance(非Blog)'] if prev_data is not None else None, icon="🏠"), unsafe_allow_html=True)
with r4[2]: st.markdown(create_compare_card("AI Perf (Blog)", current_data['AI Performance(Blog)'], prev_data['AI Performance(Blog)'] if prev_data is not None else None, icon="📝"), unsafe_allow_html=True)


# 6. 通用图表设置函数
def apply_chart_style(fig):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", 
        margin=dict(l=0, r=0, t=50, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_yaxes(rangemode="tozero", gridcolor='rgba(0,0,0,0.05)')
    return fig


# 7. 全量图表展示区
st.markdown("<br>", unsafe_allow_html=True)

# -- 第一张图：Superset 销售额 (带标签的柱状图) --
st.markdown("##### 🛒 销售额趋势 (Superset)")
fig_sales = px.bar(df_filtered, x='日期', y='销售额(superset)', color_discrete_sequence=[COLORS[0]], text='销售额(superset)')
fig_sales.update_traces(texttemplate='$%{text:.2f}', textposition='outside', cliponaxis=False)
st.plotly_chart(apply_chart_style(fig_sales), use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# -- 第二张图：各环节转化率 --
st.markdown("##### 🔄 各环节转化率 (Superset)")
rates_cols = ['转化率(superset)', '加购率(superset)', 'checkout率(superset)', '订单提交率(superset)', '支付成功率(superset)']
fig_rates = px.line(df_filtered, x='日期', y=rates_cols, color_discrete_sequence=COLORS)
fig_rates.update_traces(mode='lines+markers')
st.plotly_chart(apply_chart_style(fig_rates), use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# -- 第三张图：GA4流量与GSC点击 --
st.markdown("##### 🌐 GA4流量与GSC点击")
fig_traffic = px.line(df_filtered, x='日期', y=['流量(GA4)', '点击(GSC)'], color_discrete_sequence=COLORS)
fig_traffic.update_traces(mode='lines+markers')
st.plotly_chart(apply_chart_style(fig_traffic), use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# -- 第四张图：流量结构 --
st.markdown("##### 👥 流量结构 (Blog vs 站内)")
fig_source = px.line(df_filtered, x='日期', y=['流量(Blog)', '流量(站内)'], color_discrete_sequence=COLORS)
fig_source.update_traces(mode='lines+markers')
st.plotly_chart(apply_chart_style(fig_source), use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# -- 第五张图：细分点击趋势 --
st.markdown("##### 🖱️ 细分点击趋势")
clicks_cols = ['点击(非品牌词)', '点击(Blog)', '点击(非Blog)', '点击(非品牌词BlogUTM)']
fig_clicks = px.line(df_filtered, x='日期', y=clicks_cols, color_discrete_sequence=COLORS)
fig_clicks.update_traces(mode='lines+markers')
st.plotly_chart(apply_chart_style(fig_clicks), use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# -- 第六张图：AI Performance 展示量 --
st.markdown("##### 🤖 AI Performance 展示量")
ai_perf_cols = ['AI Performance(总展示)', 'AI Performance(非Blog)', 'AI Performance(Blog)']
fig_ai_perf = px.line(df_filtered, x='日期', y=ai_perf_cols, color_discrete_sequence=COLORS)
fig_ai_perf.update_traces(mode='lines+markers')
st.plotly_chart(apply_chart_style(fig_ai_perf), use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# -- 第七张图：AI Assistant (带标签柱状图+折线图双轴) --
st.markdown("##### 💬 AI Assistant 销售额与流量对比")
fig_ai = go.Figure()

# 柱状图部分增加数据标签
fig_ai.add_trace(go.Bar(
    x=df_filtered['日期'], 
    y=df_filtered['销售额(AI Assistant)'], 
    name='销售额 (Bar)', 
    marker_color=COLORS[0],
    text=df_filtered['销售额(AI Assistant)'],
    texttemplate='$%{text:.2f}',
    textposition='outside',
    cliponaxis=False
))

# 折线图部分
fig_ai.add_trace(go.Scatter(
    x=df_filtered['日期'], 
    y=df_filtered['流量(AI Assistant)'], 
    name='流量 (Line)', 
    yaxis='y2', 
    line=dict(color=COLORS[1], width=3), 
    mode='lines+markers'
))

fig_ai.update_layout(
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0, r=0, t=50, b=0),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    yaxis=dict(title='销售额', rangemode='tozero', gridcolor='rgba(0,0,0,0.05)'),
    yaxis2=dict(title='流量', overlaying='y', side='right', rangemode='tozero', showgrid=False)
)
st.plotly_chart(fig_ai, use_container_width=True)
