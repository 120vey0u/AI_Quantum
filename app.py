import io
import os
import folium
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# 1. Cấu hình trang Streamlit
st.set_page_config(
    page_title="AIzen HUD - Quantum Logistics",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "fullscreen" not in st.session_state:
    st.session_state.fullscreen = False

def toggle_fullscreen():
    st.session_state.fullscreen = not st.session_state.fullscreen

# 2. Nạp dữ liệu CSV
if "df" not in st.session_state:
    st.session_state.df = None
    if os.path.exists("data_input.csv"):
        try:
            st.session_state.df = pd.read_csv("data_input.csv", encoding="utf-8-sig", dtype=str)
        except Exception:
            pass

df = st.session_state.df

# 3. Tạo Bản đồ Voyager & gộp các tọa độ trùng nhau
def create_hud_map(df_data):
    map_center = [21.0285, 105.8048]
    unique_nodes_count = 0

    m = folium.Map(
        location=map_center,
        zoom_start=11,
        tiles="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
        attr='&copy; <a href="https://carto.com/">CARTO</a>',
        zoom_control=False,
    )
    
    m.get_root().html.add_child(folium.Element("""
        <style>
            html, body, .folium-map {
                width: 100% !important;
                height: 100% !important;
                margin: 0 !important;
                padding: 0 !important;
                background-color: #020813 !important;
            }
        </style>
    """))
    
    if df_data is not None:
        df_temp = df_data.copy()
        df_temp.columns = [str(col).strip() for col in df_temp.columns]
        if "Latitude" in df_temp.columns and "Longitude" in df_temp.columns:
            df_temp["Latitude"] = pd.to_numeric(df_temp["Latitude"], errors="coerce")
            df_temp["Longitude"] = pd.to_numeric(df_temp["Longitude"], errors="coerce")
            valid_coords = df_temp.dropna(subset=["Latitude", "Longitude"]).copy()
            
            if not valid_coords.empty:
                valid_coords["Lat_key"] = valid_coords["Latitude"].round(5)
                valid_coords["Lng_key"] = valid_coords["Longitude"].round(5)
                
                grouped = valid_coords.groupby(["Lat_key", "Lng_key"]).agg(
                    orders_count=("Latitude", "count"),
                    sample_id=("Order_ID", lambda x: str(x.iloc[0]) if "Order_ID" in valid_coords.columns else "N/A")
                ).reset_index()

                unique_nodes_count = len(grouped)

                map_center = [
                    grouped["Lat_key"].mean(),
                    grouped["Lng_key"].mean(),
                ]
                m.location = map_center

                for _, row in grouped.iterrows():
                    count = row["orders_count"]
                    tooltip_txt = f"NODE #{row['sample_id']}" if count == 1 else f"NODE ({count} orders)"
                    
                    folium.CircleMarker(
                        location=[row["Lat_key"], row["Lng_key"]],
                        radius=3.5,
                        color="#ffaa00",
                        weight=1,
                        fill=True,
                        fill_color="#ffcc00",
                        fill_opacity=1.0,
                        tooltip=tooltip_txt,
                    ).add_to(m)

    return m, unique_nodes_count

m_hud, visual_nodes_count = create_hud_map(df)

# =============================================================
# MODE 1: HUD FULLSCREEN
# =============================================================
if st.session_state.fullscreen:
    st.markdown(f"""<style>
html, body, [data-testid="stAppViewContainer"], .main, .block-container {{
    padding: 0 !important;
    margin: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    max-width: 100vw !important;
    max-height: 100vh !important;
    overflow: hidden !important;
    background-color: #020813 !important;
}}
header, footer, [data-testid="stHeader"], [data-testid="stToolbar"] {{
    display: none !important;
    visibility: hidden !important;
}}
.stApp {{
    background-color: #020813 !important;
    background-image: 
        linear-gradient(rgba(0, 242, 254, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 242, 254, 0.05) 1px, transparent 1px) !important;
    background-size: 40px 40px !important;
}}

.hud-overlay {{
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    pointer-events: none !important; 
    background: transparent !important;
    z-index: 9999;
}}
.hud-screen-frame {{
    position: absolute; top: 10px; left: 10px; right: 10px; bottom: 10px;
    border: 1px solid rgba(0, 242, 254, 0.25);
    pointer-events: none;
}}

.hud-info-panel {{
    position: absolute;
    top: 25px;
    left: 25px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.02), rgba(0, 242, 254, 0.01)) !important;
    backdrop-filter: blur(25px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(25px) saturate(180%) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    padding: 16px 24px;
    border-radius: 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", 'Courier New', monospace;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3), inset 0 1px 0 0 rgba(255, 255, 255, 0.15);
    pointer-events: none;
    z-index: 10000;
}}
.hud-info-title {{
    color: rgba(0, 242, 254, 0.85);
    font-size: 11px;
    letter-spacing: 2px;
    margin: 0;
    font-weight: 600;
    line-height: 1;
}}
.hud-info-value {{
    color: #00f2fe;
    font-size: 18px;
    font-weight: bold;
    text-shadow: 0 0 12px rgba(0, 242, 254, 0.6);
    letter-spacing: 1px;
    margin: 0;
    line-height: 1;
}}

.hud-ruler-top, .hud-ruler-bottom {{
    position: absolute; left: 4vw; width: 92vw; height: 5px;
    background-image: repeating-linear-gradient(90deg, rgba(0, 242, 254, 0.4) 0px, rgba(0, 242, 254, 0.4) 1px, transparent 1px, transparent 16px);
    pointer-events: none;
}}
.hud-ruler-top {{ top: 5px; }}
.hud-ruler-bottom {{ bottom: 5px; }}
.corner-tl {{ position: absolute; top: 12px; left: 12px; width: 18px; height: 18px; border-top: 2px solid #00f2fe; border-left: 2px solid #00f2fe; border-top-left-radius: 6px; box-shadow: -1px -1px 6px rgba(0,242,254,0.4); pointer-events: none; }}
.corner-tr {{ position: absolute; top: 12px; right: 12px; width: 18px; height: 18px; border-top: 2px solid #00f2fe; border-right: 2px solid #00f2fe; border-top-right-radius: 6px; box-shadow: 1px -1px 6px rgba(0,242,254,0.4); pointer-events: none; }}
.corner-bl {{ position: absolute; bottom: 12px; left: 12px; width: 18px; height: 18px; border-bottom: 2px solid #00f2fe; border-left: 2px solid #00f2fe; border-bottom-left-radius: 6px; box-shadow: -1px 1px 6px rgba(0,242,254,0.4); pointer-events: none; }}
.corner-br {{ position: absolute; bottom: 12px; right: 12px; width: 18px; height: 18px; border-bottom: 2px solid #00f2fe; border-right: 2px solid #00f2fe; border-bottom-right-radius: 6px; box-shadow: 1px 1px 6px rgba(0,242,254,0.4); pointer-events: none; }}

iframe {{
    width: 100vw !important;
    height: 100vh !important;
    border: none !important;
    outline: none !important;
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    background: #020813 !important;
    filter: invert(85%) hue-rotate(180deg) brightness(165%) contrast(145%) saturate(160%) !important;
    transform: perspective(1400px) rotateX(5deg) scale(1.06) translateY(0px) !important;
    transition: transform 0.4s ease-in-out !important;
    mask-image: radial-gradient(circle at 50% 50%, rgba(0,0,0,1) 85%, rgba(0,0,0,0) 100%) !important;
    -webkit-mask-image: radial-gradient(circle at 50% 50%, rgba(0,0,0,1) 85%, rgba(0,0,0,0) 100%) !important;
}}

div.stButton > button {{
    position: fixed !important;
    top: 20px !important;
    right: 35px !important;
    z-index: 10001 !important;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(0, 242, 254, 0.02)) !important;
    backdrop-filter: blur(20px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    color: #00f2fe !important;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", 'Courier New', monospace !important;
    font-weight: 600 !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
    border-radius: 12px !important;
    transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1) !important;
}}
div.stButton > button:hover {{
    background: rgba(0, 242, 254, 0.8) !important;
    color: #02050d !important;
    transform: scale(1.03) !important;
    box-shadow: 0 0 30px #00f2fe, inset 0 1px 0 rgba(255, 255, 255, 0.4) !important;
}}
</style>
<div class="hud-overlay">
<div class="hud-screen-frame"></div>
<div class="hud-info-panel">
    <div class="hud-info-title">SYSTEM TELEMETRY</div>
    <div class="hud-info-value">MAP NODES: {visual_nodes_count:,}</div>
</div>
<div class="hud-ruler-top"></div>
<div class="hud-ruler-bottom"></div>
<div class="corner-tl"></div>
<div class="corner-tr"></div>
<div class="corner-bl"></div>
<div class="corner-br"></div>
</div>""", unsafe_allow_html=True)

    st.button("EXIT HUD 3D FULLSCREEN", on_click=toggle_fullscreen)
    components_html = folium.Figure().add_child(m_hud)._repr_html_()
    components.html(components_html, height=1080)

# =============================================================
# MODE 2: DASHBOARD THƯỜNG
# =============================================================
else:
    st.markdown("""<style>
.stApp {
    background-color: #030611 !important;
    background-image: 
        linear-gradient(rgba(0, 242, 254, 0.08) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 242, 254, 0.08) 1px, transparent 1px) !important;
    background-size: 32px 32px !important;
    color: #e0e6ed !important;
}
h1, h2, h3, h4, label {
    color: #00f2fe !important;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", 'Courier New', monospace !important;
    text-shadow: 0 0 8px rgba(0, 242, 254, 0.5);
}

iframe {
    border-radius: 20px !important;
    border: 1px solid rgba(0, 242, 254, 0.25) !important;
    filter: invert(85%) hue-rotate(180deg) brightness(165%) contrast(145%) saturate(160%) !important;
    mask-image: radial-gradient(ellipse at center, rgba(0,0,0,1) 35%, rgba(0,0,0,0.6) 75%, rgba(0,0,0,0) 95%) !important;
    -webkit-mask-image: radial-gradient(ellipse at center, rgba(0,0,0,1) 35%, rgba(0,0,0,0.6) 75%, rgba(0,0,0,0) 95%) !important;
    transition: all 0.35s cubic-bezier(0.25, 1, 0.5, 1) !important;
}
iframe:hover {
    border-color: rgba(0, 242, 254, 0.55) !important;
    box-shadow: 0 0 32px rgba(0, 242, 254, 0.2) !important;
}

div[data-testid="stColumn"] > div, div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.025), rgba(0, 242, 254, 0.012)) !important;
    backdrop-filter: blur(30px) saturate(200%) !important;
    -webkit-backdrop-filter: blur(30px) saturate(200%) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 20px !important;
    padding: 20px !important;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.18) !important;
}

div.stButton > button {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.06), rgba(0, 242, 254, 0.03)) !important;
    backdrop-filter: blur(20px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    color: #00f2fe !important;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", 'Courier New', monospace !important;
    font-weight: bold !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 25px rgba(0, 242, 254, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
    width: 100%; height: 48px; font-size: 14px; letter-spacing: 1px;
    transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1) !important;
}
div.stButton > button:hover {
    background: rgba(0, 242, 254, 0.85) !important; color: #02050d !important;
    transform: translateY(-2px) scale(1.01) !important;
    box-shadow: 0 12px 35px rgba(0, 242, 254, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.4) !important;
}

table.table {
    width: 100%; border-collapse: collapse; 
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.025), rgba(0, 242, 254, 0.012)) !important;
    backdrop-filter: blur(30px) saturate(200%) !important;
    -webkit-backdrop-filter: blur(30px) saturate(200%) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 16px; overflow: hidden;
    color: #00f2fe; font-family: -apple-system, BlinkMacSystemFont, 'Courier New', monospace; font-size: 13px;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.18);
}
table.table th { border-bottom: 2px solid #00f2fe; padding: 12px; background: rgba(0, 242, 254, 0.12); }
table.table td { border-bottom: 1px solid rgba(0, 242, 254, 0.06); padding: 10px 12px; color: #e0e6ed; }
#MainMenu, footer, header {visibility: hidden;}
</style>""", unsafe_allow_html=True)

    col_title, col_btn = st.columns([2.8, 1.2])
    with col_title:
        st.title("AIzen HUD — Quantum Logistics Grid")
        st.caption("SYSTEM INTERFACE: ECOMMERCE TACTICAL OPTIMIZATION")
    with col_btn:
        st.write("")
        st.button("LAUNCH HUD 3D FULLSCREEN", on_click=toggle_fullscreen)

    st.divider()

    col_map, col_control = st.columns([3, 1])

    with col_control:
        st.markdown("### CONTROL MODULE")
        uploaded_file = st.file_uploader("Upload Telemetry CSV", type=["csv"])
        if uploaded_file is not None:
            try:
                file_bytes = io.BytesIO(uploaded_file.getvalue())
                st.session_state.df = pd.read_csv(file_bytes, encoding="utf-8-sig", dtype=str)
                st.success("Telemetry Stream Online")
                st.rerun()
            except Exception as e:
                st.error(f"Read Error: {e}")
        elif df is not None:
            st.info("System: Using 'data_input.csv'")
        else:
            st.warning("Pending Data Feed...")

        if df is not None:
            st.metric(label="MAP NODES", value=f"{visual_nodes_count:,} Nodes")
            st.caption(f"Total CSV Orders: {len(df):,}")

    with col_map:
        st.markdown("### TACTICAL MAP MATRIX")
        components.html(m_hud._repr_html_(), height=500)

    st.markdown("### DATA MATRIX STREAM")
    if df is not None:
        st.write(
            df.head(10).to_html(classes="table", index=False),
            unsafe_allow_html=True,
        )
    else:
        st.info("Awaiting telemetry data input...")
