import json
import os
import random
import numpy as np
import pandas as pd
from scipy.stats import norm
import streamlit as st

st.set_page_config(
    page_title="OverGrid Elite - NBA Advanced Analytics Engine",
    layout="wide",
)

# PWA (Google Play / Ana Ekran) için manifest bağlantısı ve mobil meta etiketleri
st.markdown(
    """
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#0e1117">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="apple-touch-icon" href="icon-512.png">
""",
    unsafe_allow_html=True,
)

# STİL TASARIMI (DARK MODE & ELITE UI)
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e222b; padding: 15px; border-radius: 10px; border: 1px solid #2e3644; }
    </style>
""",
    unsafe_allow_html=True,
)

# 1. NBA.COM RESMİ CDN LOGO URL SİSTEMİ (30 Takım)
TEAM_LOGOS = {
    "Atlanta": "https://cdn.nba.com/logos/nba/1610612737/global/L/logo.svg",
    "Boston": "https://cdn.nba.com/logos/nba/1610612738/global/L/logo.svg",
    "Brooklyn": "https://cdn.nba.com/logos/nba/1610612751/global/L/logo.svg",
    "Charlotte": "https://cdn.nba.com/logos/nba/1610612766/global/L/logo.svg",
    "Chicago": "https://cdn.nba.com/logos/nba/1610612741/global/L/logo.svg",
    "Cleveland": "https://cdn.nba.com/logos/nba/1610612739/global/L/logo.svg",
    "Dallas": "https://cdn.nba.com/logos/nba/1610612742/global/L/logo.svg",
    "Denver": "https://cdn.nba.com/logos/nba/1610612743/global/L/logo.svg",
    "Detroit": "https://cdn.nba.com/logos/nba/1610612765/global/L/logo.svg",
    "Golden State": "https://cdn.nba.com/logos/nba/1610612744/global/L/logo.svg",
    "Houston": "https://cdn.nba.com/logos/nba/1610612745/global/L/logo.svg",
    "Indiana": "https://cdn.nba.com/logos/nba/1610612754/global/L/logo.svg",
    "LA Clippers": "https://cdn.nba.com/logos/nba/1610612746/global/L/logo.svg",
    "LA Lakers": "https://cdn.nba.com/logos/nba/1610612747/global/L/logo.svg",
    "Memphis": "https://cdn.nba.com/logos/nba/1610612763/global/L/logo.svg",
    "Miami": "https://cdn.nba.com/logos/nba/1610612748/global/L/logo.svg",
    "Milwaukee": "https://cdn.nba.com/logos/nba/1610612749/global/L/logo.svg",
    "Minnesota": "https://cdn.nba.com/logos/nba/1610612750/global/L/logo.svg",
    "New Orleans": "https://cdn.nba.com/logos/nba/1610612740/global/L/logo.svg",
    "New York": "https://cdn.nba.com/logos/nba/1610612752/global/L/logo.svg",
    "Oklahoma": "https://cdn.nba.com/logos/nba/1610612760/global/L/logo.svg",
    "Orlando": "https://cdn.nba.com/logos/nba/1610612753/global/L/logo.svg",
    "Phila": "https://cdn.nba.com/logos/nba/1610612755/global/L/logo.svg",
    "Phoenix": "https://cdn.nba.com/logos/nba/1610612756/global/L/logo.svg",
    "Portland": "https://cdn.nba.com/logos/nba/1610612757/global/L/logo.svg",
    "Sacramento": "https://cdn.nba.com/logos/nba/1610612758/global/L/logo.svg",
    "San Antonio": "https://cdn.nba.com/logos/nba/1610612759/global/L/logo.svg",
    "Toronto": "https://cdn.nba.com/logos/nba/1610612761/global/L/logo.svg",
    "Utah": "https://cdn.nba.com/logos/nba/1610612762/global/L/logo.svg",
    "Washington": "https://cdn.nba.com/logos/nba/1610612764/global/L/logo.svg",
}

# 2. KONFERANS GRUPLARI
EAST_TEAMS = [
    "Boston",
    "Milwaukee",
    "New York",
    "Cleveland",
    "Orlando",
    "Indiana",
    "Phila",
    "Miami",
    "Chicago",
    "Atlanta",
    "Brooklyn",
    "Toronto",
    "Charlotte",
    "Washington",
    "Detroit",
]
WEST_TEAMS = [
    "Oklahoma",
    "Denver",
    "Minnesota",
    "LA Clippers",
    "Dallas",
    "Phoenix",
    "New Orleans",
    "LA Lakers",
    "Sacramento",
    "Golden State",
    "Memphis",
    "Houston",
    "Utah",
    "San Antonio",
    "Portland",
]

# 3. GÜNÜN MAÇLARI LİSTESİ
todays_matches = [
    ("Washington", "Atlanta", "03:00 TSİ"),
    ("Detroit", "Phila", "03:00 TSİ"),
    ("Brooklyn", "Charlotte", "03:30 TSİ"),
    ("New York", "Chicago", "03:30 TSİ"),
    ("Boston", "Milwaukee", "03:00 TSİ"),
    ("New Orleans", "Utah", "04:00 TSİ"),
    ("Oklahoma", "Cleveland", "04:00 TSİ"),
    ("Memphis", "Indiana", "04:00 TSİ"),
    ("Houston", "Minnesota", "04:30 TSİ"),
    ("Phoenix", "Portland", "05:00 TSİ"),
    ("Denver", "Toronto", "05:00 TSİ"),
    ("San Antonio", "Dallas", "05:30 TSİ"),
    ("Sacramento", "La Lakers", "06:00 TSİ"),
    ("LA Clippers", "Miami", "06:30 TSİ"),
]

# 4. MAÇ SONU ÜST VERİ MATRİSİ
DEFAULT_ELITE_DATA = {
    "Toronto": [118.87, 110.6, 115.3, 116.7, 102.0, 1.02, 8, 11],
    "Miami": [118.7, 118.7, 116.8, 117.9, 99.0, 1.01, 9, 12],
    "Boston": [119.1, 109.8, 113.1, 112.8, 99.0, 1.02, 7, 10],
    "Dallas": [111.6, 115.1, 116.3, 114.0, 98.0, 0.97, 6, 11],
    "Denver": [116.3, 119.1, 112.1, 110.2, 97.0, 1.02, 6, 11],
    "Utah": [112.1, 115.1, 110.3, 113.7, 100.0, 0.93, 4, 10],
    "LA Clippers": [112.0, 110.3, 110.5, 116.6, 99.0, 1.00, 5, 10],
    "Golden State": [115.6, 110.6, 114.0, 114.1, 103.0, 1.03, 8, 13],
    "Detroit": [113.8, 111.1, 114.1, 108.1, 101.0, 0.98, 7, 12],
    "Phoenix": [115.5, 115.1, 109.9, 116.9, 99.0, 1.01, 8, 10],
    "Phila": [113.8, 110.4, 111.1, 113.9, 100.0, 1.01, 5, 12],
    "New York": [110.4, 110.9, 109.2, 116.8, 95.0, 1.00, 4, 12],
    "Atlanta": [114.9, 117.1, 116.4, 112.8, 101.0, 0.98, 9, 13],
    "Brooklyn": [109.3, 114.8, 115.1, 113.9, 99.0, 0.95, 7, 10],
    "Charlotte": [106.3, 113.1, 103.3, 109.3, 96.0, 0.93, 3, 12],
    "Chicago": [117.2, 116.2, 113.6, 119.7, 101.0, 1.00, 8, 12],
    "Cleveland": [116.6, 115.4, 115.5, 115.7, 100.0, 1.03, 6, 10],
    "Indiana": [112.2, 114.0, 115.4, 115.2, 102.0, 1.00, 6, 11],
    "Milwaukee": [110.8, 118.7, 114.2, 117.2, 100.0, 1.00, 7, 12],
    "Orlando": [113.3, 114.3, 112.6, 115.0, 96.0, 0.99, 6, 10],
    "Washington": [112.9, 111.4, 111.7, 111.9, 101.0, 0.94, 4, 11],
    "Houston": [115.7, 109.4, 118.1, 112.5, 100.0, 1.02, 9, 11],
    "LA Lakers": [116.7, 115.1, 112.3, 111.7, 101.0, 1.02, 8, 12],
    "Memphis": [119.4, 113.1, 115.5, 111.1, 103.0, 1.03, 5, 11],
    "Minnesota": [114.4, 112.0, 116.4, 114.0, 98.0, 1.01, 9, 14],
    "New Orleans": [113.9, 112.0, 117.1, 117.6, 102.0, 1.00, 7, 11],
    "Oklahoma": [112.3, 110.4, 108.9, 113.8, 101.0, 1.03, 6, 12],
    "Portland": [115.2, 111.0, 117.0, 113.1, 101.0, 0.98, 4, 9],
    "Sacramento": [110.9, 117.8, 110.0, 117.4, 101.0, 0.98, 6, 12],
    "San Antonio": [116.1, 110.8, 112.6, 111.6, 102.0, 1.01, 7, 12],
}

# 5. İLK YARI (İY) ÜST VERİ MATRİSİ
DEFAULT_ELITE_DATA_IY = {
    "Toronto": [65.16, 54.83, 53.83, 59.66, 102.0, 1.02, 4, 7],
    "Miami": [61.42, 62.57, 68.00, 65.20, 99.0, 1.01, 5, 7],
    "Boston": [61.16, 49.83, 58.40, 54.80, 99.0, 1.02, 3, 7],
    "Dallas": [52.28, 60.85, 56.50, 54.00, 98.0, 0.97, 2, 7],
    "Denver": [58.00, 64.40, 59.66, 54.66, 97.0, 1.02, 4, 6],
    "Utah": [58.42, 60.00, 55.50, 60.00, 100.0, 0.93, 1, 7],
    "LA Clippers": [55.00, 52.00, 53.60, 59.20, 99.0, 1.00, 4, 7],
    "Golden State": [61.71, 56.28, 53.28, 57.42, 103.0, 1.03, 5, 8],
    "Detroit": [49.50, 57.25, 58.14, 52.14, 101.0, 0.98, 1, 7],
    "Phoenix": [61.75, 58.75, 55.00, 60.33, 99.0, 1.01, 3, 5],
    "Phila": [57.42, 57.71, 54.60, 56.60, 100.0, 1.01, 4, 8],
    "New York": [55.42, 53.28, 50.80, 64.60, 95.0, 1.00, 0, 7],
    "Atlanta": [53.40, 60.40, 64.87, 58.75, 101.0, 0.98, 4, 8],
    "Brooklyn": [52.25, 58.25, 56.71, 58.28, 99.0, 0.95, 3, 7],
    "Charlotte": [54.71, 56.14, 46.60, 49.40, 96.0, 0.93, 3, 8],
    "Chicago": [60.60, 59.40, 56.71, 62.42, 101.0, 1.00, 4, 7],
    "Cleveland": [58.00, 60.50, 59.25, 52.25, 100.0, 1.03, 4, 7],
    "Indiana": [54.71, 61.85, 60.80, 59.80, 102.0, 1.00, 4, 8],
    "Milwaukee": [46.83, 62.16, 54.66, 62.66, 100.0, 1.00, 3, 7],
    "Orlando": [59.66, 60.16, 55.80, 59.60, 96.0, 0.99, 4, 7],
    "Washington": [56.40, 57.00, 56.33, 58.83, 101.0, 0.94, 2, 7],
    "Houston": [59.50, 51.66, 58.60, 46.20, 100.0, 1.02, 3, 8],
    "LA Lakers": [65.37, 58.12, 61.80, 58.00, 101.0, 1.02, 6, 8],
    "Memphis": [60.60, 53.40, 64.00, 56.00, 103.0, 1.03, 3, 7],
    "Minnesota": [55.60, 55.80, 61.55, 55.22, 98.0, 1.01, 4, 8],
    "New Orleans": [58.60, 54.60, 59.33, 61.00, 102.0, 1.00, 4, 7],
    "Oklahoma": [60.33, 54.00, 55.00, 54.83, 101.0, 1.03, 3, 7],
    "Portland": [62.33, 49.00, 61.33, 58.50, 101.0, 0.98, 3, 6],
    "Sacramento": [52.25, 66.25, 51.75, 64.00, 101.0, 0.98, 6, 7],
    "San Antonio": [62.75, 54.75, 57.75, 60.25, 102.0, 1.01, 3, 7],
}

DATA_FILE = "teams_data.json"
DATA_FILE_IY = "teams_data_iy.json"

def load_data():
  if os.path.exists(DATA_FILE):
    try:
      with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      return DEFAULT_ELITE_DATA
  else:
    return DEFAULT_ELITE_DATA

def load_data_iy():
  if os.path.exists(DATA_FILE_IY):
    try:
      with open(DATA_FILE_IY, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      return DEFAULT_ELITE_DATA_IY
  else:
    return DEFAULT_ELITE_DATA_IY

if "elite_data" not in st.session_state:
  st.session_state["elite_data"] = load_data()

if "elite_data_iy" not in st.session_state:
  st.session_state["elite_data_iy"] = load_data_iy()

if "randomized_matches" not in st.session_state:
  shuffled_list = todays_matches.copy()
  random.shuffle(shuffled_list)
  st.session_state["randomized_matches"] = shuffled_list

initial_match = st.session_state["randomized_matches"][0]

if "selected_home" not in st.session_state:
  st.session_state["selected_home"] = initial_match[0]
if "selected_away" not in st.session_state:
  st.session_state["selected_away"] = initial_match[1]
if "active_tab" not in st.session_state:
  st.session_state["active_tab"] = "🎯 Profesyonel Maç Analizi"

# ANA BAŞLIK
st.title("⚡ OverGrid Pro - Elite AI NBA Prediction Engine")
st.caption(
    "Dengelenmiş Çapraz Analiz & Gelişmiş NBA Skor Optimizasyon Sistemi"
)

# ÜST MENÜ (ANA SEKME SİSTEMİ)
tab_options = [
    "🎯 Profesyonel Maç Analizi",
    "📅 Maç Günü",
    "📊 Konferans Puan/Veri Grid'i",
]
selected_tab = st.radio(
    "Menü",
    tab_options,
    index=tab_options.index(st.session_state["active_tab"]),
    horizontal=True,
    label_visibility="collapsed",
)
st.session_state["active_tab"] = selected_tab

st.markdown("---")

# 1. BÖLÜM: PROFESYONEL MAÇ ANALİZİ
if selected_tab == "🎯 Profesyonel Maç Analizi":
  
  sub_tab_ust, sub_tab_iy_ust = st.tabs(["🔥 Üst (Maç Sonu)", "⚡ İY Üst (İlk Yarı)"])

  def get_ust_format_str(ust_sayisi, toplam_mac, mode="ust"):
    try:
      ust = float(ust_sayisi)
      top = float(toplam_mac)
      if top > 0:
        yuzde = (ust / top) * 100
        prefix = "İY " if mode == "iy" else ""
        return f"{int(ust)}/{int(top)} {prefix}Üst (%{yuzde:.1f})"
    except:
      pass
    return f"{ust_sayisi}/{toplam_mac} Üst"

  # ==========================================
  # ALT SEKME 1: ÜST (MAÇ SONU) ANALİZİ
  # ==========================================
  with sub_tab_ust:
    ELITE_DATA = st.session_state["elite_data"]
    df_teams = pd.DataFrame.from_dict(
        ELITE_DATA,
        orient="index",
        columns=[
            "Ev Atığı", "Ev Yediği", "Dep Atığı", "Dep Yediği",
            "Tempo", "Form", "Üst Sayısı", "Toplam Maç",
        ],
    )
    df_teams["Form_Orani"] = [
        get_ust_format_str(row["Üst Sayısı"], row["Toplam Maç"], mode="ust")
        for _, row in df_teams.iterrows()
    ]

    LEAGUE_AVG_SCORED = (df_teams["Ev Atığı"].mean() + df_teams["Dep Atığı"].mean()) / 2
    LEAGUE_AVG_TEMPO = df_teams["Tempo"].mean()

    all_teams_sorted = sorted(list(ELITE_DATA.keys()))
    team_display_options = {
        t: f"{t} ({get_ust_format_str(ELITE_DATA[t][6], ELITE_DATA[t][7], mode='ust')})"
        for t in all_teams_sorted
    }
    inverse_display_options = {
        f"{t} ({get_ust_format_str(ELITE_DATA[t][6], ELITE_DATA[t][7], mode='ust')})": t
        for t in all_teams_sorted
    }

    current_home_display = team_display_options.get(
        st.session_state["selected_home"], list(team_display_options.values())[0]
    )
    current_away_display = team_display_options.get(
        st.session_state["selected_away"], list(team_display_options.values())[1]
    )

    c1, c2 = st.columns(2)
    with c1:
      selected_home_display = st.selectbox(
          "Ev Sahibi Takım (Üst)",
          list(team_display_options.values()),
          index=list(team_display_options.values()).index(current_home_display),
          key="sb_home_ust",
      )
      home_team = inverse_display_options[selected_home_display]
    with c2:
      selected_away_display = st.selectbox(
          "Deplasman Takım (Üst)",
          list(team_display_options.values()),
          index=list(team_display_options.values()).index(current_away_display),
          key="sb_away_ust",
      )
      away_team = inverse_display_options[selected_away_display]

    st.session_state["selected_home"] = home_team
    st.session_state["selected_away"] = away_team

    h_ust_str = get_ust_format_str(ELITE_DATA[home_team][6], ELITE_DATA[home_team][7], mode="ust")
    a_ust_str = get_ust_format_str(ELITE_DATA[away_team][6], ELITE_DATA[away_team][7], mode="ust")

    col_logo_h, col_logo_mid, col_logo_a = st.columns([2, 1, 2])
    with col_logo_h:
      if home_team in TEAM_LOGOS:
        st.image(TEAM_LOGOS[home_team], width=75)
      st.markdown(f"### 🏠 {home_team} ({h_ust_str}) (Ev Sahibi)")
    with col_logo_mid:
      st.markdown("<h2 style='text-align: center;'>VS</h2>", unsafe_allow_html=True)
    with col_logo_a:
      if away_team in TEAM_LOGOS:
        st.image(TEAM_LOGOS[away_team], width=75)
      st.markdown(f"### ✈️ {away_team} ({a_ust_str}) (Deplasman)")

    if home_team == away_team:
      st.error("⚠️ Lütfen iki farklı takım seçiniz.")
    else:
      h_data = df_teams.loc[home_team]
      a_data = df_teams.loc[away_team]

      h_off_power = h_data["Ev Atığı"] / LEAGUE_AVG_SCORED
      a_def_power = a_data["Dep Yediği"] / LEAGUE_AVG_SCORED
      a_off_power = a_data["Dep Atığı"] / LEAGUE_AVG_SCORED
      h_def_power = h_data["Ev Yediği"] / LEAGUE_AVG_SCORED

      match_tempo_factor = ((h_data["Tempo"] + a_data["Tempo"]) / 2) / LEAGUE_AVG_TEMPO

      exp_home = ((h_off_power * a_def_power) ** 0.5 * LEAGUE_AVG_SCORED * match_tempo_factor * h_data["Form"] * 1.01)
      exp_away = ((a_off_power * h_def_power) ** 0.5 * LEAGUE_AVG_SCORED * match_tempo_factor * a_data["Form"])
      exp_total = exp_home + exp_away
      std_dev = 11.5

      st.markdown("---")
      m1, m2, m3 = st.columns(3)
      m1.metric("Ev Sahibi Skor Beklentisi", f"{exp_home:.1f}")
      m2.metric("Deplasman Skor Beklentisi", f"{exp_away:.1f}")
      m3.metric("🎯 Dengelenmiş Toplam Skor", f"{exp_total:.1f}")

      st.markdown("### 🏆 215.5 - 234.5 Aralığı Kesintisiz 0.5'li ÜST Barem Analizi")
      lines_to_check = np.arange(215.5, 235.0, 1.0)
      barem_data = []
      for line in lines_to_check:
        z = (exp_total - line) / std_dev
        over_p = norm.cdf(z) * 100
        if over_p >= 85:
          rec = "💎 BANKO ÜST (Çok Yüksek Güven)"
        elif over_p >= 70:
          rec = "🔥 Yüksek Oranlı ÜST"
        elif over_p >= 50:
          rec = "⚖️ İdeal ÜST Seçeneği"
        else:
          rec = "🛡️ Düşük İhtimal"
        barem_data.append({
            "İddia Üst Baremi": f"{line:.1f} ÜST",
            "Üst Tutma İhtimali (%)": f"%{over_p:.1f}",
            "Risk Analizi": rec,
        })
      st.dataframe(pd.DataFrame(barem_data), use_container_width=True)

  # ==========================================
  # ALT SEKME 2: İY ÜST (İLK YARI ÜST) ANALİZİ
  # ==========================================
  with sub_tab_iy_ust:
    ELITE_DATA_IY = st.session_state["elite_data_iy"]
    df_teams_iy = pd.DataFrame.from_dict(
        ELITE_DATA_IY,
        orient="index",
        columns=[
            "Ev Atığı", "Ev Yediği", "Dep Atığı", "Dep Yediği",
            "Tempo", "Form", "Üst Sayısı", "Toplam Maç",
        ],
    )
    df_teams_iy["Form_Orani"] = [
        get_ust_format_str(row["Üst Sayısı"], row["Toplam Maç"], mode="iy")
        for _, row in df_teams_iy.iterrows()
    ]

    LEAGUE_AVG_SCORED_IY = (df_teams_iy["Ev Atığı"].mean() + df_teams_iy["Dep Atığı"].mean()) / 2
    LEAGUE_AVG_TEMPO_IY = df_teams_iy["Tempo"].mean()

    team_display_options_iy = {
        t: f"{t} ({get_ust_format_str(ELITE_DATA_IY[t][6], ELITE_DATA_IY[t][7], mode='iy')})"
        for t in all_teams_sorted
    }
    inverse_display_options_iy = {
        f"{t} ({get_ust_format_str(ELITE_DATA_IY[t][6], ELITE_DATA_IY[t][7], mode='iy')})": t
        for t in all_teams_sorted
    }

    current_home_display_iy = team_display_options_iy.get(
        st.session_state["selected_home"], list(team_display_options_iy.values())[0]
    )
    current_away_display_iy = team_display_options_iy.get(
        st.session_state["selected_away"], list(team_display_options_iy.values())[1]
    )

    c1_iy, c2_iy = st.columns(2)
    with c1_iy:
      selected_home_display_iy = st.selectbox(
          "Ev Sahibi Takım (İY Üst)",
          list(team_display_options_iy.values()),
          index=list(team_display_options_iy.values()).index(current_home_display_iy),
          key="sb_home_iy",
      )
      home_team_iy = inverse_display_options_iy[selected_home_display_iy]
    with c2_iy:
      selected_away_display_iy = st.selectbox(
          "Deplasman Takım (İY Üst)",
          list(team_display_options_iy.values()),
          index=list(team_display_options_iy.values()).index(current_away_display_iy),
          key="sb_away_iy",
      )
      away_team_iy = inverse_display_options_iy[selected_away_display_iy]

    h_ust_str_iy = get_ust_format_str(ELITE_DATA_IY[home_team_iy][6], ELITE_DATA_IY[home_team_iy][7], mode="iy")
    a_ust_str_iy = get_ust_format_str(ELITE_DATA_IY[away_team_iy][6], ELITE_DATA_IY[away_team_iy][7], mode="iy")

    col_logo_h_iy, col_logo_mid_iy, col_logo_a_iy = st.columns([2, 1, 2])
    with col_logo_h_iy:
      if home_team_iy in TEAM_LOGOS:
        st.image(TEAM_LOGOS[home_team_iy], width=75)
      st.markdown(f"### 🏠 {home_team_iy} ({h_ust_str_iy}) (Ev Sahibi - İY)")
    with col_logo_mid_iy:
      st.markdown("<h2 style='text-align: center;'>VS</h2>", unsafe_allow_html=True)
    with col_logo_a_iy:
      if away_team_iy in TEAM_LOGOS:
        st.image(TEAM_LOGOS[away_team_iy], width=75)
      st.markdown(f"### ✈️ {away_team_iy} ({a_ust_str_iy}) (Deplasman - İY)")

    if home_team_iy == away_team_iy:
      st.error("⚠️ Lütfen iki farklı takım seçiniz.")
    else:
      h_data_iy = df_teams_iy.loc[home_team_iy]
      a_data_iy = df_teams_iy.loc[away_team_iy]

      h_off_power_iy = h_data_iy["Ev Atığı"] / LEAGUE_AVG_SCORED_IY
      a_def_power_iy = a_data_iy["Dep Yediği"] / LEAGUE_AVG_SCORED_IY
      a_off_power_iy = a_data_iy["Dep Atığı"] / LEAGUE_AVG_SCORED_IY
      h_def_power_iy = h_data_iy["Ev Yediği"] / LEAGUE_AVG_SCORED_IY

      match_tempo_factor_iy = ((h_data_iy["Tempo"] + a_data_iy["Tempo"]) / 2) / LEAGUE_AVG_TEMPO_IY

      exp_home_iy = (h_off_power_iy * a_def_power_iy) ** 0.5 * LEAGUE_AVG_SCORED_IY * match_tempo_factor_iy * h_data_iy["Form"] * 0.95
      exp_away_iy = (a_off_power_iy * h_def_power_iy) ** 0.5 * LEAGUE_AVG_SCORED_IY * match_tempo_factor_iy * a_data_iy["Form"] * 0.95
      exp_total_iy = exp_home_iy + exp_away_iy
      std_dev_iy = 8.5

      st.markdown("---")
      m1_iy, m2_iy, m3_iy = st.columns(3)
      m1_iy.metric("İlk Yarı Ev Skor Beklentisi", f"{exp_home_iy:.1f}")
      m2_iy.metric("İlk Yarı Deplasman Beklentisi", f"{exp_away_iy:.1f}")
      m3_iy.metric("🎯 İY Dengelenmiş Toplam Skor", f"{exp_total_iy:.1f}")

      st.markdown("### 🏆 İlk Yarı ÜST Barem Analizi (105.5 - 125.5)")
      lines_to_check_iy = np.arange(105.5, 126.0, 1.0)
      barem_data_iy = []
      for line in lines_to_check_iy:
        z = (exp_total_iy - line) / std_dev_iy
        over_p = norm.cdf(z) * 100
        if over_p >= 85:
          rec = "💎 BANKO İY ÜST"
        elif over_p >= 70:
          rec = "🔥 Yüksek Oranlı İY ÜST"
        elif over_p >= 50:
          rec = "⚖️ İdeal İY ÜST"
        else:
          rec = "🛡️ Düşük İhtimal"
        barem_data_iy.append({
            "İlk Yarı Üst Baremi": f"{line:.1f} İY ÜST",
            "Üst Tutma İhtimali (%)": f"%{over_p:.1f}",
            "Risk Analizi": rec,
        })
      st.dataframe(pd.DataFrame(barem_data_iy), use_container_width=True)

# 2. BÖLÜM: MAÇ GÜNÜ
elif selected_tab == "📅 Maç Günü":
  st.subheader("📅 Günün Maçları & Canlı Fikstür Analiz Paneli")
  st.info(
      "Bugün oynanması planlanan öne çıkan NBA karşılaşmaları ve başlama"
      " saatleri (TSİ) aşağıdadır. Maçın üzerindeki butona tıkladığınızda sistem"
      " sizi otomatik olarak analiz sayfasına yönlendirir."
  )

  for idx, (hm, aw, m_time) in enumerate(todays_matches):
    with st.container():
      col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(
          [2, 1.2, 1, 2, 2]
      )
      with col_m1:
        if hm in TEAM_LOGOS:
          st.image(TEAM_LOGOS[hm], width=35)
        st.write(f"**{hm}**")
      with col_m2:
        st.markdown(f"🕒 **{m_time}**")
      with col_m3:
        st.markdown(
            "<h4 style='text-align: center;'>VS</h4>", unsafe_allow_html=True
        )
      with col_m4:
        if aw in TEAM_LOGOS:
          st.image(TEAM_LOGOS[aw], width=35)
        st.write(f"**{aw}**")

      with col_m5:
        if st.button(
            f"🔍 Maçı Analiz Et", key=f"btn_match_{idx}", use_container_width=True
        ):
          st.session_state["selected_home"] = hm
          st.session_state["selected_away"] = aw
          st.session_state["active_tab"] = "🎯 Profesyonel Maç Analizi"
          st.rerun()
      st.markdown("---")

# 3. BÖLÜM: KONFERANS PUAN / VERİ GRİD'İ
elif selected_tab == "📊 Konferans Puan/Veri Grid'i":
  
  grid_tab_ust, grid_tab_iy_ust = st.tabs(["🔥 Üst (Maç Sonu) Grid", "⚡ İY Üst (İlk Yarı) Grid"])

  # 1. ALT SEKME: MAÇ SONU ÜST PUAN DURUMU
  with grid_tab_ust:
    st.subheader("East Konferansı Puan / Veri Matrisi (Maç Sonu Üst)")
    df_east = pd.DataFrame.from_dict(
        st.session_state["elite_data"],
        orient="index",
        columns=["Ev Atığı", "Ev Yediği", "Dep Atığı", "Dep Yediği", "Tempo", "Form", "Üst Sayısı", "Toplam Maç"]
    )
    df_east["Toplam Üst"] = [
        f"{int(r['Üst Sayısı'])}/{int(r['Toplam Maç'])} Üst (%{(r['Üst Sayısı']/r['Toplam Maç'])*100:.1f})" 
        if r['Toplam Maç'] > 0 else "0/0 Üst (%0.0)" 
        for _, r in df_east.iterrows()
    ]
    
    df_east_filtered = df_east.loc[[t for t in EAST_TEAMS if t in df_east.index]].copy()
    df_east_filtered["Logo"] = [TEAM_LOGOS.get(t, "") for t in df_east_filtered.index]
    df_east_filtered = df_east_filtered[["Logo", "Ev Atığı", "Ev Yediği", "Dep Atığı", "Dep Yediği", "Toplam Üst", "Tempo", "Form"]]
    
    st.dataframe(
        df_east_filtered,
        use_container_width=True,
        column_config={
            "Logo": st.column_config.ImageColumn(
                "Logo", help="Doğu Logosu", width="small"
            )
        },
    )

    st.markdown("---")
    st.subheader("West Konferansı Puan / Veri Matrisi (Maç Sonu Üst)")
    df_west = pd.DataFrame.from_dict(
        st.session_state["elite_data"],
        orient="index",
        columns=["Ev Atığı", "Ev Yediği", "Dep Atığı", "Dep Yediği", "Tempo", "Form", "Üst Sayısı", "Toplam Maç"]
    )
    df_west["Toplam Üst"] = [
        f"{int(r['Üst Sayısı'])}/{int(r['Toplam Maç'])} Üst (%{(r['Üst Sayısı']/r['Toplam Maç'])*100:.1f})" 
        if r['Toplam Maç'] > 0 else "0/0 Üst (%0.0)" 
        for _, r in df_west.iterrows()
    ]

    df_west_filtered = df_west.loc[[t for t in WEST_TEAMS if t in df_west.index]].copy()
    df_west_filtered["Logo"] = [TEAM_LOGOS.get(t, "") for t in df_west_filtered.index]
    df_west_filtered = df_west_filtered[["Logo", "Ev Atığı", "Ev Yediği", "Dep Atığı", "Dep Yediği", "Toplam Üst", "Tempo", "Form"]]
    
    st.dataframe(
        df_west_filtered,
        use_container_width=True,
        column_config={
            "Logo": st.column_config.ImageColumn(
                "Logo", help="Batı Konferansı Logosu", width="small"
            )
        },
    )

  # 2. ALT SEKME: İLK YARI ÜST PUAN DURUMU
  with grid_tab_iy_ust:
    st.subheader("East Konferansı Puan / Veri Matrisi (İlk Yarı Üst)")
    df_east_iy = pd.DataFrame.from_dict(
        st.session_state["elite_data_iy"],
        orient="index",
        columns=["Ev Atığı", "Ev Yediği", "Dep Atığı", "Dep Yediği", "Tempo", "Form", "Üst Sayısı", "Toplam Maç"]
    )
    df_east_iy["Toplam İY Üst"] = [
        f"{int(r['Üst Sayısı'])}/{int(r['Toplam Maç'])} İY Üst (%{(r['Üst Sayısı']/r['Toplam Maç'])*100:.1f})" 
        if r['Toplam Maç'] > 0 else "0/0 İY Üst (%0.0)" 
        for _, r in df_east_iy.iterrows()
    ]
    
    df_east_iy_filtered = df_east_iy.loc[[t for t in EAST_TEAMS if t in df_east_iy.index]].copy()
    df_east_iy_filtered["Logo"] = [TEAM_LOGOS.get(t, "") for t in df_east_iy_filtered.index]
    df_east_iy_filtered = df_east_iy_filtered[["Logo", "Ev Atığı", "Ev Yediği", "Dep Atığı", "Dep Yediği", "Toplam İY Üst", "Tempo", "Form"]]
    
    st.dataframe(
        df_east_iy_filtered,
        use_container_width=True,
        column_config={
            "Logo": st.column_config.ImageColumn(
                "Logo", help="Doğu Logosu", width="small"
            )
        },
    )

    st.markdown("---")
    st.subheader("West Konferansı Puan / Veri Matrisi (İlk Yarı Üst)")
    df_west_iy = pd.DataFrame.from_dict(
        st.session_state["elite_data_iy"],
        orient="index",
        columns=["Ev Atığı", "Ev Yediği", "Dep Atığı", "Dep Yediği", "Tempo", "Form", "Üst Sayısı", "Toplam Maç"]
    )
    df_west_iy["Toplam İY Üst"] = [
        f"{int(r['Üst Sayısı'])}/{int(r['Toplam Maç'])} İY Üst (%{(r['Üst Sayısı']/r['Toplam Maç'])*100:.1f})" 
        if r['Toplam Maç'] > 0 else "0/0 İY Üst (%0.0)" 
        for _, r in df_west_iy.iterrows()
    ]

    df_west_iy_filtered = df_west_iy.loc[[t for t in WEST_TEAMS if t in df_west_iy.index]].copy()
    df_west_iy_filtered["Logo"] = [TEAM_LOGOS.get(t, "") for t in df_west_iy_filtered.index]
    df_west_iy_filtered = df_west_iy_filtered[["Logo", "Ev Atığı", "Ev Yediği", "Dep Atığı", "Dep Yediği", "Toplam İY Üst", "Tempo", "Form"]]
    
    st.dataframe(
        df_west_iy_filtered,
        use_container_width=True,
        column_config={
            "Logo": st.column_config.ImageColumn(
                "Logo", help="Batı Konferansı Logosu", width="small"
            )
        },
    )
