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
    ("Utah", "Portland", "22:00 TSİ"),
    ("Charlotte", "Phila", "01:00 TSİ"),
    ("New Orleans", "Atlanta", "02:00 TSİ"),
    ("Memphis", "Sacramento", "03:00 TSİ"),
    ("Milwaukee", "Cleveland", "03:00 TSİ"),
    ("San Antonio", "Minnesota", "03.00 TSİ"),
    ("Houston", "Oklahoma", "03.30 TSİ"),
]

# 4. ELITE NBA RESMİ İSTATİSTİK MATRİSİ
DEFAULT_ELITE_DATA = {
    "Toronto": [118.8, 110.6, 113.2, 115.6, 101.5, 1.01, 7, 10],
    "Miami": [118.7, 118.7, 117.2, 116.0, 98.2, 1.00, 8, 11],
    "Boston": [119.1, 109.8, 117.1, 115.8, 100.8, 1.03, 7, 9],
    "Dallas": [112.4, 115.2, 116.3, 114.0, 99.4, 0.98, 6, 10],
    "Denver": [117.4, 119.9, 112.1, 110.2, 97.9, 1.02, 6, 10],
    "Utah": [113.8, 115.5, 112.0, 112.8, 102.1, 0.95, 4, 9],
    "LA Clippers": [111.1, 108.0, 109.9, 116.1, 98.0, 0.99, 4, 8],
    "Golden State": [115.1, 109.6, 114.0, 114.1, 103.4, 1.02, 7, 12],
    "Detroit": [113.8, 111.1, 113.3, 109.2, 100.0, 0.97, 6, 11],
    "Phoenix": [115.5, 115.1, 109.2, 117.3, 99.1, 1.01, 7, 9],
    "Phila": [112.8, 110.4, 111.1, 115.2, 99.8, 1.00, 4, 10],
    "New York": [110.8, 112.4, 109.2, 116.8, 96.5, 1.01, 4, 11],
    "Atlanta": [114.9, 117.1, 119.0, 112.7, 102.8, 0.99, 9, 11],
    "Brooklyn": [109.3, 114.8, 119.5, 117.4, 100.4, 0.96, 7, 9],
    "Charlotte": [106.7, 112.3, 103.3, 109.3, 98.5, 0.94, 1, 10],
    "Chicago": [117.2, 116.2, 114.1, 119.7, 101.2, 1.00, 8, 11],
    "Cleveland": [117.3, 115.4, 112.3, 116.8, 99.5, 1.02, 4, 8],
    "Indiana": [114.9, 116.2, 115.4, 115.2, 103.0, 1.01, 6, 10],
    "Milwaukee": [110.5, 117.5, 114.6, 118.1, 101.0, 1.01, 6, 10],
    "Orlando": [117.5, 116.6, 112.6, 115.0, 97.8, 1.00, 6, 9],
    "Washington": [112.9, 111.4, 112.3, 113.5, 102.5, 0.95, 4, 10],
    "Houston": [116.7, 112.0, 118.1, 112.5, 99.0, 1.01, 8, 9],
    "LA Lakers": [114.3, 114.3, 112.3, 111.7, 100.6, 1.01, 7, 11],
    "Memphis": [116.3, 110.6, 115.5, 111.1, 102.2, 1.01, 3, 9],
    "Minnesota": [114.8, 112.1, 116.9, 113.6, 98.4, 1.01, 8, 12],
    "New Orleans": [113.1, 113.5, 115.7, 116.4, 100.1, 0.98, 6, 9],
    "Oklahoma": [112.3, 110.4, 108.1, 113.5, 101.9, 1.03, 4, 10],
    "Portland": [115.2, 111.0, 118.3, 116.2, 100.8, 0.97, 4, 7],
    "Sacramento": [110.9, 117.8, 109.4, 117.9, 102.0, 0.99, 5, 10],
    "San Antonio": [115.9, 111.5, 112.6, 111.6, 101.4, 1.00, 6, 10],
}

DATA_FILE = "teams_data.json"


def load_data():
  if os.path.exists(DATA_FILE):
    try:
      with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      return DEFAULT_ELITE_DATA
  else:
    return DEFAULT_ELITE_DATA


if "elite_data" not in st.session_state:
  st.session_state["elite_data"] = load_data()

# Uygulama her açıldığında günün maçları rastgele karıştırılır
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

ELITE_DATA = st.session_state["elite_data"]
df_teams = pd.DataFrame.from_dict(
    ELITE_DATA,
    orient="index",
    columns=[
        "Ev Atığı",
        "Ev Yediği",
        "Dep Atığı",
        "Dep Yediği",
        "Tempo",
        "Form",
        "Üst Sayısı",
        "Toplam Maç",
    ],
)


# YÜZDE FORMAT FONKSİYONU
def get_ust_format_str(ust_sayisi, toplam_mac):
  try:
    ust = float(ust_sayisi)
    top = float(toplam_mac)
    if top > 0:
      yuzde = (ust / top) * 100
      return f"{int(ust)}/{int(top)} Üst (%{yuzde:.1f})"
  except:
    pass
  return f"{ust_sayisi}/{toplam_mac} Üst"


df_teams["Form_Orani"] = [
    get_ust_format_str(row["Üst Sayısı"], row["Toplam Maç"])
    for _, row in df_teams.iterrows()
]

LEAGUE_AVG_SCORED = (
    df_teams["Ev Atığı"].mean() + df_teams["Dep Atığı"].mean()
) / 2
LEAGUE_AVG_TEMPO = df_teams["Tempo"].mean()

# ANA BAŞLIK
st.title("⚡ OverGrid Pro - Elite AI NBA Prediction Engine")
st.caption(
    "Dengelenmiş Çapraz Analiz & Gerçekçi NBA Skor Optimizasyon Sistemi"
)

# ÜST MENÜ (SEKME SİSTEMİ)
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

if selected_tab == "🎯 Profesyonel Maç Analizi":
  all_teams_sorted = sorted(list(ELITE_DATA.keys()))

  team_display_options = {
      t: f"{t} ({get_ust_format_str(ELITE_DATA[t][6], ELITE_DATA[t][7])})"
      for t in all_teams_sorted
  }
  inverse_display_options = {
      f"{t} ({get_ust_format_str(ELITE_DATA[t][6], ELITE_DATA[t][7])})": t
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
        "Ev Sahibi Takım",
        list(team_display_options.values()),
        index=list(team_display_options.values()).index(current_home_display),
        key="sb_home",
    )
    home_team = inverse_display_options[selected_home_display]
  with c2:
    selected_away_display = st.selectbox(
        "Deplasman Takım",
        list(team_display_options.values()),
        index=list(team_display_options.values()).index(current_away_display),
        key="sb_away",
    )
    away_team = inverse_display_options[selected_away_display]

  st.session_state["selected_home"] = home_team
  st.session_state["selected_away"] = away_team

  h_ust_str = get_ust_format_str(ELITE_DATA[home_team][6], ELITE_DATA[home_team][7])
  a_ust_str = get_ust_format_str(ELITE_DATA[away_team][6], ELITE_DATA[away_team][7])

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

    match_tempo_factor = (
        (h_data["Tempo"] + a_data["Tempo"]) / 2
    ) / LEAGUE_AVG_TEMPO

    exp_home = (
        (h_off_power * a_def_power) ** 0.5
        * LEAGUE_AVG_SCORED
        * match_tempo_factor
        * h_data["Form"]
        * 1.01
    )
    exp_away = (
        (a_off_power * h_def_power) ** 0.5
        * LEAGUE_AVG_SCORED
        * match_tempo_factor
        * a_data["Form"]
    )
    exp_total = exp_home + exp_away

    std_dev = 11.5

    st.markdown("---")

    m1, m2, m3 = st.columns(3)
    m1.metric("Ev Sahibi Skor Beklentisi", f"{exp_home:.1f}")
    m2.metric("Deplasman Skor Beklentisi", f"{exp_away:.1f}")
    m3.metric("🎯 Dengelenmiş Toplam Skor", f"{exp_total:.1f}")

    st.markdown(
        "### 🏆 215.5 - 234.5 Aralığı Kesintisiz 0.5'li ÜST Barem Analizi"
    )
    st.info(
        "Normalleştirilmiş çapraz analiz verileriyle hesaplanan **215.5 - 234.5"
        " arası 0.5'li iddia baremleri** ve **ÜST** tutma olasılıkları"
        " aşağıdadır."
    )

    # 215.5 ile 234.5 arasındaki 0.5'li tüm baremleri kapsayacak aralık (215.5 - 234.5 dahil)
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

    df_barem = pd.DataFrame(barem_data)
    st.dataframe(df_barem, use_container_width=True)

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

elif selected_tab == "📊 Konferans Puan/Veri Grid'i":
  st.subheader("East Konferansı Puan / Veri Matrisi")
  df_east = df_teams.loc[
      [t for t in EAST_TEAMS if t in df_teams.index]
  ].copy()
  df_east["Logo"] = [TEAM_LOGOS.get(t, "") for t in df_east.index]
  df_east = df_east[
      [
          "Logo",
          "Ev Atığı",
          "Ev Yediği",
          "Dep Atığı",
          "Dep Yediği",
          "Form_Orani",
          "Tempo",
          "Form",
      ]
  ]
  df_east = df_east.rename(columns={"Form_Orani": "Toplam Üst"})
  st.dataframe(
      df_east,
      use_container_width=True,
      column_config={
          "Logo": st.column_config.ImageColumn(
              "Logo", help="Doğu Logosu", width="small"
          )
      },
  )

  st.markdown("---")
  st.subheader("West Konferansı Puan / Veri Matrisi")
  df_west = df_teams.loc[
      [t for t in WEST_TEAMS if t in df_teams.index]
  ].copy()
  df_west["Logo"] = [TEAM_LOGOS.get(t, "") for t in df_west.index]
  df_west = df_west[
      [
          "Logo",
          "Ev Atığı",
          "Ev Yediği",
          "Dep Atığı",
          "Dep Yediği",
          "Form_Orani",
          "Tempo",
          "Form",
      ]
  ]
  df_west = df_west.rename(columns={"Form_Orani": "Toplam Üst"})
  st.dataframe(
      df_west,
      use_container_width=True,
      column_config={
          "Logo": st.column_config.ImageColumn(
              "Logo", help="Batı Logosu", width="small"
          )
      },
  )
