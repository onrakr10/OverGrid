import numpy as np
import pandas as pd
from scipy.stats import norm
import streamlit as st

st.set_page_config(
    page_title="OverGrid - NBA Analytics Engine",
    layout="wide",
    initial_sidebar_state="expanded",
)

# STİL TASARIMI
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e222b; padding: 15px; border-radius: 10px; border: 1px solid #2e3644; }
    .badge-over { background-color: #00c853; color: white; padding: 6px 12px; border-radius: 6px; font-weight: bold; }
    .badge-under { background-color: #d50000; color: white; padding: 6px 12px; border-radius: 6px; font-weight: bold; }
    </style>
""",
    unsafe_allow_html=True,
)

# 1. ESPN HIZLI CDN TAKIM LOGO URL EŞLEŞTİRMELERİ
TEAM_LOGOS = {
    "Toronto": "https://a.espncdn.com/i/teamlogos/nba/50/tor.png",
    "Miami": "https://a.espncdn.com/i/teamlogos/nba/50/mia.png",
    "Boston": "https://a.espncdn.com/i/teamlogos/nba/50/bos.png",
    "Dallas": "https://a.espncdn.com/i/teamlogos/nba/50/dal.png",
    "Denver": "https://a.espncdn.com/i/teamlogos/nba/50/den.png",
    "Utah": "https://a.espncdn.com/i/teamlogos/nba/50/uta.png",
    "LA Clippers": "https://a.espncdn.com/i/teamlogos/nba/50/lac.png",
    "Golden State": "https://a.espncdn.com/i/teamlogos/nba/50/gs.png",
    "Detroit": "https://a.espncdn.com/i/teamlogos/nba/50/det.png",
    "Phoenix": "https://a.espncdn.com/i/teamlogos/nba/50/phx.png",
    "Phila": "https://a.espncdn.com/i/teamlogos/nba/50/phi.png",
    "New York": "https://a.espncdn.com/i/teamlogos/nba/50/nyk.png",
    "Atlanta": "https://a.espncdn.com/i/teamlogos/nba/50/atl.png",
    "Brooklyn": "https://a.espncdn.com/i/teamlogos/nba/50/bkn.png",
    "Charlotte": "https://a.espncdn.com/i/teamlogos/nba/50/cha.png",
    "Chicago": "https://a.espncdn.com/i/teamlogos/nba/50/chi.png",
    "Cleveland": "https://a.espncdn.com/i/teamlogos/nba/50/cle.png",
    "Indiana": "https://a.espncdn.com/i/teamlogos/nba/50/ind.png",
    "Milwaukee": "https://a.espncdn.com/i/teamlogos/nba/50/mil.png",
    "Orlando": "https://a.espncdn.com/i/teamlogos/nba/50/orl.png",
    "Washington": "https://a.espncdn.com/i/teamlogos/nba/50/wsh.png",
    "Houston": "https://a.espncdn.com/i/teamlogos/nba/50/hou.png",
    "LA Lakers": "https://a.espncdn.com/i/teamlogos/nba/50/lal.png",
    "Memphis": "https://a.espncdn.com/i/teamlogos/nba/50/mem.png",
    "Minnesota": "https://a.espncdn.com/i/teamlogos/nba/50/min.png",
    "New Orleans": "https://a.espncdn.com/i/teamlogos/nba/50/no.png",
    "Oklahoma": "https://a.espncdn.com/i/teamlogos/nba/50/okc.png",
    "Portland": "https://a.espncdn.com/i/teamlogos/nba/50/por.png",
    "Sacramento": "https://a.espncdn.com/i/teamlogos/nba/50/sac.png",
    "San Antonio": "https://a.espncdn.com/i/teamlogos/nba/50/sas.png",
}

# 2. PDF SENSÖR VERİLERİ (Sistemdeki 30 Takım Verisi)
RAW_DATA = {
    "Toronto": [126.2, 104.8, 112.75, 117.5],
    "Miami": [120.33, 123.83, 120.75, 118.25],
    "Boston": [124.8, 105.0, 120.67, 118.0],
    "Dallas": [110.2, 117.8, 119.0, 114.25],
    "Denver": [121.25, 126.5, 107.2, 104.2],
    "Utah": [114.0, 117.33, 110.33, 112.0],
    "LA Clippers": [108.5, 102.5, 108.0, 115.67],
    "Golden State": [117.75, 108.25, 114.29, 114.57],
    "Detroit": [114.0, 108.5, 113.4, 107.0],
    "Phoenix": [116.33, 113.0, 104.8, 121.0],
    "Phila": [114.8, 110.0, 108.5, 116.75],
    "New York": [108.0, 111.67, 107.75, 125.5],
    "Atlanta": [116.75, 123.0, 124.5, 111.67],
    "Brooklyn": [108.67, 118.0, 125.6, 121.2],
    "Charlotte": [100.2, 111.0, 97.5, 107.5],
    "Chicago": [120.8, 118.8, 115.2, 126.2],
    "Cleveland": [121.0, 117.2, 111.0, 123.0],
    "Indiana": [116.2, 118.8, 115.25, 109.75],
    "Milwaukee": [107.4, 121.4, 115.6, 122.6],
    "Orlando": [121.5, 119.5, 109.25, 117.0],
    "Washington": [116.5, 116.75, 111.0, 113.4],
    "Houston": [119.75, 110.25, 125.5, 110.25],
    "LA Lakers": [115.0, 115.0, 115.0, 109.25],
    "Memphis": [119.0, 107.67, 116.0, 109.6],
    "Minnesota": [112.33, 113.67, 120.25, 113.5],
    "New Orleans": [106.0, 111.0, 117.8, 119.2],
    "Oklahoma": [110.83, 107.17, 102.75, 113.25],
    "Portland": [123.5, 100.5, 123.0, 118.75],
    "Sacramento": [108.25, 122.0, 102.4, 120.4],
    "San Antonio": [118.17, 109.33, 111.5, 109.5],
}

df_teams = pd.DataFrame.from_dict(
    RAW_DATA,
    orient="index",
    columns=["Ev Attığı", "Ev Yediği", "Dep Attığı", "Dep Yediği"],
)

# Lig Ortalamaları
LEAGUE_AVG_SCORED = df_teams[["Ev Attığı", "Dep Attığı"]].values.mean()

# BAŞLIK
st.title("⚡ OverGrid Pro - High Precision NBA Predictor")
st.caption("Veri Analitiği & Normal Dağılım Odaklı İddia Tahmin Motoru")

# SEKME YAPISI
tab1, tab2 = st.tabs(["🎯 Profesyonel Maç Analizi", "📊 Takım Puan/Veri Grid'i"])

with tab1:
  col_h, col_a, col_b = st.columns(3)
  with col_h:
    home_team = st.selectbox("Ev Sahibi Takım", df_teams.index, index=0)
  with col_a:
    away_team = st.selectbox("Deplasman Takımı", df_teams.index, index=1)
  with col_b:
    barem = st.number_input(
        "İddia Baremi (Örn: 228.5)", value=224.5, step=0.5
    )

  # SEÇİLEN TAKIMLARIN LOGOLARINI GÖSTERME ALANI
  col_logo_h, col_logo_a = st.columns(2)
  with col_logo_h:
    if home_team in TEAM_LOGOS:
      st.image(TEAM_LOGOS[home_team], width=60)
    st.markdown(f"**Ev Sahibi:** {home_team}")
  with col_logo_a:
    if away_team in TEAM_LOGOS:
      st.image(TEAM_LOGOS[away_team], width=60)
    st.markdown(f"**Deplasman:** {away_team}")

  if home_team == away_team:
    st.error("⚠️ Lütfen iki farklı takım seçiniz.")
  else:
    # --- PROFESYONEL HESAPLAMA MOTORU ---
    h_off = df_teams.loc[home_team, "Ev Attığı"] / LEAGUE_AVG_SCORED
    h_def = df_teams.loc[home_team, "Ev Yediği"] / LEAGUE_AVG_SCORED
    a_off = df_teams.loc[away_team, "Dep Attığı"] / LEAGUE_AVG_SCORED
    a_def = df_teams.loc[away_team, "Dep Yediği"] / LEAGUE_AVG_SCORED

    # Beklenen Skorlar
    exp_home = h_off * a_def * LEAGUE_AVG_SCORED
    exp_away = a_off * h_def * LEAGUE_AVG_SCORED
    exp_total = exp_home + exp_away

    # Tahmin Sapma Payı
    std_dev = 12.5
    z_score = (exp_total - barem) / std_dev
    over_prob = norm.cdf(z_score) * 100
    under_prob = 100 - over_prob

    # Güven İndeksi
    edge = abs(exp_total - barem)
    if edge > 8:
      confidence = "YÜKSEK 🔥"
    elif edge > 4:
      confidence = "ORTA ⚖️"
    else:
      confidence = "DÜŞÜK (RİSKLİ) ⚠️"

    st.markdown("---")

    # METRİKLER
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tahmini Ev Skoru", f"{exp_home:.1f}")
    m2.metric("Tahmini Dep Skoru", f"{exp_away:.1f}")
    m3.metric("Tahmini Toplam Skor", f"{exp_total:.1f}")
    m4.metric("Güven Seviyesi", confidence)

    st.markdown("### 🎲 Olasılık ve Karar Matrisi")

    c_rec, c_prob = st.columns([2, 3])

    with c_rec:
      if exp_total > barem:
        st.success(
            f"### 🎯 TAHMİN: ÜST ({barem})\nFark: +{edge:.1f} Sayı Beklentisi"
        )
      else:
        st.error(
            f"### 🛡️ TAHMİN: ALT ({barem})\nFark: -{edge:.1f} Sayı Beklentisi"
        )

    with c_prob:
      st.write(f"**Üst Bitiş Olasılığı:** %{over_prob:.1f}")
      st.progress(int(over_prob))
      st.write(f"**Alt Bitiş Olasılığı:** %{under_prob:.1f}")
      st.progress(int(under_prob))

with tab2:
  st.subheader("Takım İstatistik Veri Matrisi")

  # DataFrame'e Logo sütununu ekle
  df_display = df_teams.copy()
  df_display["Logo"] = [TEAM_LOGOS.get(t, "") for t in df_display.index]

  # Sütun sırasını düzenle (Logo en başta olsun)
  cols = ["Logo"] + [c for c in df_teams.columns]
  df_display = df_display[cols]

  # Streamlit yerel ImageColumn bileşeni ile logoları göster
  st.dataframe(
      df_display,
      use_container_width=True,
      column_config={
          "Logo": st.column_config.ImageColumn(
              "Logo", help="Takım Logosu", width="small"
          )
      },
  )
