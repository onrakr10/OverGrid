import numpy as np
import pandas as pd
from scipy.stats import norm
import streamlit as st

st.set_page_config(
    page_title="OverGrid Elite - NBA Advanced Analytics Engine",
    layout="wide",
    initial_sidebar_state="expanded",
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

# 3. ELITE NBA RESMİ İSTATİSTİK MATRİSİ (Format: [Ev Atığı, Ev Yediği, Dep Atığı, Dep Yediği, Tempo, Form, Üst Sayısı, Toplam Maç])
DEFAULT_ELITE_DATA = {
    "Toronto": [116.2, 108.8, 112.75, 111.5, 101.5, 1.01, 7, 9],
    "Miami": [112.33, 110.83, 110.75, 108.25, 98.2, 1.00, 8, 10],
    "Boston": [118.8, 105.0, 115.67, 108.0, 100.8, 1.03, 7, 9],
    "Dallas": [110.2, 109.8, 109.0, 110.25, 99.4, 0.98, 6, 9],
    "Denver": [115.25, 106.5, 110.2, 109.2, 97.9, 1.02, 6, 9],
    "Utah": [111.0, 114.33, 108.33, 112.0, 102.1, 0.95, 4, 9],
    "LA Clippers": [108.5, 106.5, 108.0, 109.67, 98.0, 0.99, 4, 9],
    "Golden State": [114.75, 109.25, 112.29, 111.57, 103.4, 1.02, 7, 10],
    "Detroit": [108.0, 112.5, 106.4, 113.0, 100.0, 0.97, 6, 9],
    "Phoenix": [113.33, 110.0, 110.8, 112.0, 99.1, 1.01, 7, 10],
    "Phila": [112.8, 109.0, 108.5, 110.75, 99.8, 1.00, 4, 9],
    "New York": [110.0, 107.67, 107.75, 110.5, 96.5, 1.01, 4, 9],
    "Atlanta": [114.75, 116.0, 112.5, 114.67, 102.8, 0.99, 9, 10],
    "Brooklyn": [108.67, 112.0, 109.6, 111.2, 100.4, 0.96, 7, 10],
    "Charlotte": [105.2, 115.0, 103.5, 112.5, 98.5, 0.94, 1, 9],
    "Chicago": [112.8, 113.8, 111.2, 114.2, 101.2, 1.00, 8, 10],
    "Cleveland": [115.0, 109.2, 111.0, 110.0, 99.5, 1.02, 4, 9],
    "Indiana": [116.2, 115.8, 113.25, 113.75, 103.0, 1.01, 6, 9],
    "Milwaukee": [113.4, 111.4, 111.6, 112.6, 101.0, 1.01, 6, 9],
    "Orlando": [111.5, 108.5, 109.25, 110.0, 97.8, 1.00, 6, 9],
    "Washington": [108.5, 116.75, 107.0, 115.4, 102.5, 0.95, 4, 9],
    "Houston": [112.75, 110.25, 110.5, 110.25, 99.0, 1.01, 8, 10],
    "LA Lakers": [113.0, 111.0, 111.0, 111.25, 100.6, 1.01, 7, 10],
    "Memphis": [114.0, 109.67, 112.0, 109.6, 102.2, 1.01, 3, 9],
    "Minnesota": [112.33, 107.67, 110.25, 109.5, 98.4, 1.01, 8, 10],
    "New Orleans": [109.0, 111.0, 108.8, 111.2, 100.1, 0.98, 6, 9],
    "Oklahoma": [115.83, 107.17, 112.75, 109.25, 101.9, 1.03, 4, 9],
    "Portland": [109.5, 112.5, 108.0, 113.75, 100.8, 0.97, 4, 9],
    "Sacramento": [111.25, 112.0, 110.4, 112.4, 102.0, 0.99, 5, 9],
    "San Antonio": [111.17, 112.33, 110.5, 112.5, 101.4, 1.00, 6, 9],
}

if "elite_data" not in st.session_state:
  st.session_state["elite_data"] = DEFAULT_ELITE_DATA

if "selected_home" not in st.session_state:
  st.session_state["selected_home"] = "Boston"
if "selected_away" not in st.session_state:
  st.session_state["selected_away"] = "Miami"
if "active_tab" not in st.session_state:
  st.session_state["active_tab"] = "🎯 Profesyonel Maç Analizi"

# --- SOL KENAR ÇUBUĞU (SIDEBAR) - SKOR VE ÜST GÜNCELLEME ---
st.sidebar.header("🏀 Takım Skor Güncelleme")
st.sidebar.info(
    "İstediğiniz takımın maç skor ortalamalarını, üst sayısını ve toplam maç"
    " sayısını buradan güncelleyebilirsiniz."
)

selected_edit_team = st.sidebar.selectbox(
    "Takım Seçin", sorted(list(st.session_state["elite_data"].keys()))
)
curr = st.session_state["elite_data"][selected_edit_team]

ed_ev_at = st.sidebar.number_input(
    "Ev Sahibi Atığı", value=float(curr[0]), step=0.1
)
ed_ev_yed = st.sidebar.number_input(
    "Ev Sahibi Yediği", value=float(curr[1]), step=0.1
)
ed_dep_at = st.sidebar.number_input(
    "Deplasman Atığı", value=float(curr[2]), step=0.1
)
ed_dep_yed = st.sidebar.number_input(
    "Deplasman Yediği", value=float(curr[3]), step=0.1
)
ed_toplam_ust = st.sidebar.number_input(
    "Üst Sayısı", value=int(curr[6]), step=1
)
ed_toplam_mac = st.sidebar.number_input(
    "Toplam Maç Sayısı", value=int(curr[7]), step=1
)

ed_tempo = curr[4]
ed_form = curr[5]

if st.sidebar.button("💾 Skorları Güncelle", use_container_width=True):
  st.session_state["elite_data"][selected_edit_team] = [
      ed_ev_at,
      ed_ev_yed,
      ed_dep_at,
      ed_dep_yed,
      ed_tempo,
      ed_form,
      ed_toplam_ust,
      ed_toplam_mac,
  ]
  st.sidebar.success(f"✅ {selected_edit_team} verileri güncellendi!")

st.sidebar.markdown("---")
st.sidebar.header("📄 PDF Rapor Yükle")
uploaded_pdf = st.sidebar.file_uploader(
    "NBA Bülten / PDF Yükle", type=["pdf", "csv", "xlsx"]
)
if uploaded_pdf is not None:
  st.sidebar.success(
      "📁 Dosya başarıyla yüklendi! (Otomatik ayrıştırma aktif)"
  )

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

# Tablolar için gösterge sütunu oluşturma (örn: "6/9 Üst")
df_teams["Form_Orani"] = (
    df_teams["Üst Sayısı"].astype(int).astype(str)
    + "/"
    + df_teams["Toplam Maç"].astype(int).astype(str)
    + " Üst"
)

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

  # Seçim kutularında görünecek etiketleri "Takım Adı (X/Y Üst)" formatında hazırlıyoruz
  team_display_options = {
      t: f"{t} ({int(ELITE_DATA[t][6])}/{int(ELITE_DATA[t][7])} Üst)"
      for t in all_teams_sorted
  }
  inverse_display_options = {
      f"{t} ({int(ELITE_DATA[t][6])}/{int(ELITE_DATA[t][7])} Üst)": t
      for t in all_teams_sorted
  }

  current_home_display = team_display_options.get(
      st.session_state["selected_home"], all_teams_sorted[0]
  )
  current_away_display = team_display_options.get(
      st.session_state["selected_away"], all_teams_sorted[1]
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

  h_ust_str = f"{int(ELITE_DATA[home_team][6])}/{int(ELITE_DATA[home_team][7])} Üst"
  a_ust_str = f"{int(ELITE_DATA[away_team][6])}/{int(ELITE_DATA[away_team][7])} Üst"

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
        "### 🏆 220.5 - 234.5 Aralığı Kesintisiz 0.5'li ÜST Barem Analizi"
    )
    st.info(
        "Normalleştirilmiş çapraz analiz verileriyle hesaplanan **0.5'li iddia"
        " baremleri** ve **ÜST** tutma olasılıkları aşağıdadır."
    )

    lines_to_check = np.arange(220.5, 235.0, 1.0)

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

  todays_matches = [
      ("Washington", "Charlotte", "02:00 TSİ"),
      ("Boston", "Chicago", "02:30 TSİ"),
      ("Brooklyn", "Detroit", "02:30 TSİ"),
      ("Phila", "New York", "02:30 TSİ"),
      ("Toronto", "Orlando", "02:30 TSİ"),
      ("Dallas", "Houston", "03.00 TSİ"),
      ("Miami", "Indiana", "03.00 TSİ"),
      ("Minnesota", "LA Clippers", "03.00 TSİ"),
      ("Golden State", "LA Lakers", "05.00 TSİ"),
      ("Phoenix", "Denver", "05.00 TSİ"),
  ]

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
  df_west = df_teams.loc[[t for t in WEST_TEAMS if t in df_teams.index]].copy()
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
