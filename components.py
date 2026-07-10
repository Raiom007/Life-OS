import streamlit as st
import plotly.graph_objects as go

def render_kpi(title, value, subtext="", trend="none"):
    """
    Renders a custom HTML KPI Card mapping to the CSS in style.css.
    trend can be "positive", "negative", or "none" (affects value color).
    """
    trend_class = ""
    if trend == "positive":
        trend_class = "positive"
    elif trend == "negative":
        trend_class = "negative"

    html = f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value {trend_class}">{value}</div>
        <div class="kpi-subtext">{subtext}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_progress_bar(label, percentage, color="#6ba5ff"):
    """
    Renders a clean progress bar.
    percentage is a list/float from 0 to 100.
    """
    st.markdown(f"**{label}**")
    pct = max(0, min(100, int(percentage)))
    html = f"""
    <div style="background-color: #1a1e24; border-radius: 8px; width: 100%; height: 12px; margin-bottom: 1rem; border: 1px solid #2d3748; overflow: hidden;">
        <div style="background: linear-gradient(90deg, {color} 0%, #a485ff 100%); width: {pct}%; height: 100%; border-radius: 8px; transition: width 0.5s ease-in-out;"></div>
    </div>
    <div style="text-align: right; color: #a0aec0; font-size: 0.8rem; margin-top: -0.8rem; margin-bottom: 1rem;">{pct}%</div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_xp_bar(level, total_xp, progress_pct):
    """
    Specialized progress bar for XP leveling up.
    """
    html = f"""
    <div style="background-color: #15181d; padding: 1.5rem; border-radius: 8px; border: 1px solid #2d3748; margin-bottom: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.5rem;">
            <span style="font-size: 1.5rem; font-weight: bold; color: #e2e8f0;">Level {level}</span>
            <span style="font-size: 1rem; color: #6ba5ff; font-weight: bold;">{total_xp} XP Total</span>
        </div>
        <div style="background-color: #0b0e14; border-radius: 12px; width: 100%; height: 18px; border: 1px solid #1a202c; overflow: hidden;">
            <div style="background: linear-gradient(90deg, #facc15 0%, #fbbf24 100%); width: {progress_pct}%; height: 100%; border-radius: 12px; transition: width 0.5s ease-in-out; box-shadow: 0 0 10px rgba(250, 204, 21, 0.5);"></div>
        </div>
        <div style="text-align: right; color: #a0aec0; font-size: 0.85rem; margin-top: 0.5rem; font-style: italic;">{progress_pct}% to next level</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def plotly_dark_theme(fig):
    """
    Applies the custom dark theme to a plotly figure.
    """
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0", family="Inter"),
        title_font=dict(color="#ffffff", size=18, family="Inter"),
        legend=dict(font=dict(color="#a0aec0")),
        xaxis=dict(showgrid=True, gridcolor="#2d3748", zerolinecolor="#2d3748"),
        yaxis=dict(showgrid=True, gridcolor="#2d3748", zerolinecolor="#2d3748"),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def render_section_header(title, subtitle=None):
    st.markdown(f"<h2>{title}</h2>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<p style='color: #a0aec0; margin-top: -0.5rem; margin-bottom: 2rem;'>{subtitle}</p>", unsafe_allow_html=True)
