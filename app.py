import numpy as np
import pandas as pd
from scipy.stats import norm
import streamlit as st

st.set_page_config(
    page_title="OverGrid Pro - Advanced NBA Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

# STİL TASARIMI
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e222b; padding: 15px; border-radius: 10px; border: 1px solid #2e3644; }
    .badge-high { background-color: #00c853; color: white; padding: 6px 12px; border-radius: 6px; font-weight: bold; }
    .badge-mid { background-color: #ff9800; color: white; padding: 6px 12px; border-radius: 6px; font-weight: bold; }
    .badge-low { background-color: #d50000; color: white; padding: 6px 12px; border-radius: 6px; font-weight: bold; }
    </style>
""",
    unsafe_allow_html=True,
)

# 1. 30 TAKIM İÇİN KESİNTİSİZ WIKIMEDIA PNG LOGO LİSTESİ
TEAM_LOGOS = {
    "Toronto": "https://upload.wikimedia.org/wikipedia/en/thumb/7/72/Toronto_Raptors_logo.svg/80px-Toronto_Raptors_logo.svg.png",
    "Miami": "https://upload.wikimedia.org/wikipedia/en/thumb/f/fb/Miami_Heat_logo.svg/80px-Miami_Heat_logo.svg.png",
    "Boston": "https://upload.wikimedia.org/wikipedia/en/thumb/2/29/Boston_Celtics_logo.svg/80px-Boston_Celtics_logo.svg.png",
    "Dallas": "https://upload.wikimedia.org/wikipedia/en/thumb/9/97/Dallas_Mavericks_logo.svg/80px-Dallas_Mavericks_logo.svg.png",
    "Denver": "https://upload.wikimedia.org/wikipedia/en/thumb/7/76/Denver_Nuggets_logo_%282018%29.svg/80px-Denver_Nuggets_logo_%282018%29.svg.png",
    "Utah": "https://upload.wikimedia.org/wikipedia/en/thumb/b/be/Utah_Jazz_logo_%282022%29.svg/80px-Utah_Jazz_logo_%282022%29.svg.png",
    "LA Clippers": "https://upload.wikimedia.org/wikipedia/en/thumb/e/ed/Los_Angeles_Clippers_%282024%29_logo.svg/80px-Los_Angeles_Clippers_%282024%29_logo.svg.png",
    "Golden State": "https://upload.wikimedia.org/wikipedia/en/thumb/0/01/Golden_State_Warriors_logo.svg/80px-Golden_State_Warriors_logo.svg.png",
    "Detroit": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c9/Detroit_Pistons_logo_%282017%29.svg/80px-Detroit_Pistons_logo_%282017%29.svg.png",
    "Phoenix": "https://upload.wikimedia.org/wikipedia/en/thumb/d/df/Phoenix_Suns_logo.svg/80px-Phoenix_Suns_logo.svg.png",
    "Phila": "https://upload.wikimedia.org/wikipedia/en/thumb/4/46/Philadelphia_76ers_logo.svg/80px-Philadelphia_76ers_logo.svg.png",
    "New York": "https://upload.wikimedia.org/wikipedia/en/thumb/2/2b/New_York_Knicks_logo.svg/80px-New_York_Knicks_logo.svg.png",
    "Atlanta": "https://upload.wikimedia.org/wikipedia/en/thumb/2/24/Atlanta_Hawks_logo_%282020%29.svg/80px-Atlanta_Hawks_logo_%282020%29.svg.png",
    "Brooklyn": "https://upload.wikimedia.org/wikipedia/en/thumb/4/44/Brooklyn_Nets_logo.svg/80px-Brooklyn_Nets_logo.svg.png",
    "Charlotte": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c4/Charlotte_Hornets_%282014%29.svg/80px-Charlotte_Hornets_%282014%29.svg.png",
    "Chicago": "https://upload.wikimedia.org/wikipedia/en/thumb/6/67/Chicago_Bulls_logo.svg/80px-Chicago_Bulls_logo.svg.png",
    "Cleveland": "https://upload.wikimedia.org/wikipedia/en/thumb/0/04/Cleveland_Cavaliers_logo.svg/80px-Cleveland_Cavaliers_logo.svg.png",
    "Indiana": "https://upload.wikimedia.org/wikipedia/en/thumb/1/1b/Indiana_Pacers_logo_%282017%29.svg/80px-Indiana_Pacers_logo_%282017%29.svg.png",
    "Milwaukee": "https://upload.wikimedia.org/wikipedia/en/thumb/4/4a/Milwaukee_Bucks_logo.svg/80px-Milwaukee_Bucks_logo.svg.png",
    "Orlando": "https://upload.wikimedia.org/wikipedia/en/thumb/1/10/Orlando_Magic_logo.svg/80px-Orlando_Magic_logo.svg.png",
    "Washington": "https://upload.wikimedia.org/wikipedia/en/thumb/0/02/Washington_Wizards_logo.svg/80px-Washington_Wizards_logo.svg.png",
    "Houston": "https://upload.wikimedia.org/wikipedia/en/thumb/2/28/Houston_Rockets_logo_%282020%29.svg/80px-Houston_Rockets_logo_%282020%29.svg.png",
    "LA Lakers": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Los_Angeles_Lakers_logo.svg/80px-Los_Angeles_Lakers_logo.svg.png",
    "Memphis": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f1/Memphis_Grizzlies.svg/80px-Memphis_Grizzlies.svg.png",
    "Minnesota": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c2/Minnesota_Timberwolves_logo_%282017%29.svg/80px-Minnesota_Timberwolves_logo_%282017%29.svg.png",
    "New Orleans": "https://upload.wikimedia.org/wikipedia/en/thumb/0/0d/New_Orleans_Pelicans_logo.svg/80px-New_Orleans_Pelicans_logo.svg.png",
    "Oklahoma": "https://upload.wikimedia.org/wikipedia/en/thumb/5/5d/Oklahoma_City_Thunder_logo.svg/80px-Oklahoma_City_Thunder_logo.svg.png",
    "Portland": "https://upload.wikimedia.org/wikipedia/en/thumb/2/21/Portland_Trail_Blazers_logo.svg/80px-Portland_Trail_Blazers_logo.svg.png",
    "Sacramento": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c7/Sacramento_Kings_logo_%282016%29.svg/80px-Sacramento_Kings_logo_%282016%29.svg.png",
    "San Antonio": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a2/San_Antonio_Spurs_logo.svg/80px-San_Antonio_Spurs_logo.svg.png",
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

# 3. PDF SENSÖR VERİLERİ
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
    columns=["Ev Sahibi Atığı", "Ev Sahibi Yediği", "Dep Atığı", "Dep Yediği"],
)
LEAGUE_AVG_SCORED = df_teams[["Ev Sahibi Atığı", "Dep Atığı"]].values.mean()

# BAŞLIK
st.title("⚡ OverGrid Pro - Professional AI Betting Engine")
st.caption(
    "Normal Dağılım & Alt Barem Odakli Profesyonel Analiz ve Maç Günü Sistemi"
)

# SEKME YAPISI (Üç Sekme: Maç Analizi, Maç Günü, Konferans Grid)
tab1, tab2, tab3 = st.tabs(
    ["🎯 Profesyonel Maç Analizi", "📅 Maç Günü", "📊 Konferans Puan/Veri Grid'i"]
)

with tab1:
  all_teams_sorted = sorted(list(RAW_DATA.keys()))

  c1, c2 = st.columns(2)
  with c1:
    home_team = st.selectbox("Ev Sahibi Takım", all_teams_sorted, index=0)
  with c2:
    away_team = st.selectbox("Deplasman Takım", all_teams_sorted, index=1)

  # LOGOLAR VE TAKIM BİLGİLERİ
  col_logo_h, col_logo_mid, col_logo_a = st.columns([2, 1, 2])
  with col_logo_h:
    if home_team in TEAM_LOGOS:
      st.image(TEAM_LOGOS[home_team], width=70)
    st.markdown(f"### 🏠 {home_team} (Ev Sahibi)")
  with col_logo_mid:
    st.markdown("<h2 style='text-align: center;'>VS</h2>", unsafe_allow_html=True)
  with col_logo_a:
    if away_team in TEAM_LOGOS:
      st.image(TEAM_LOGOS[away_team], width=70)
    st.markdown(f"### ✈️ {away_team} (Deplasman)")

  if home_team == away_team:
    st.error("⚠️ Lütfen iki farklı takım seçiniz.")
  else:
    # --- PROFESYONEL HESAPLAMA MOTORU ---
    h_off = df_teams.loc[home_team, "Ev Sahibi Atığı"] / LEAGUE_AVG_SCORED
    h_def = df_teams.loc[home_team, "Ev Sahibi Yediği"] / LEAGUE_AVG_SCORED
    a_off = df_teams.loc[away_team, "Dep Atığı"] / LEAGUE_AVG_SCORED
    a_def = df_teams.loc[away_team, "Dep Yediği"] / LEAGUE_AVG_SCORED

    exp_home = h_off * a_def * LEAGUE_AVG_SCORED
    exp_away = a_off * h_def * LEAGUE_AVG_SCORED
    exp_total = exp_home + exp_away

    std_dev = 12.0  # NBA standart sapma katsayısı

    st.markdown("---")

    # ÜST DÜZEY METRİKLER
    m1, m2, m3 = st.columns(3)
    m1.metric("Tahmini Ev Sahibi Skoru", f"{exp_home:.1f}")
    m2.metric("Tahmini Deplasman Skoru", f"{exp_away:.1f}")
    m3.metric("🎯 Model Beklenen Toplam Skor", f"{exp_total:.1f}")

    # EN YÜKSEK TUTMA İHTİMALİNE GÖRE UZMAN ÖNERİSİ
    base_line = round(exp_total * 2) / 2
    z_opt = (exp_total - base_line) / std_dev
    best_over_p = norm.cdf(z_opt) * 100

    st.markdown("### 🏆 Yapay Zeka En Yüksek Olasılıklı Ana Tahmin")
    if best_over_p >= 50:
      primary_pick = f"{base_line} ÜST"
      primary_prob = best_over_p
      st.success(
          f"🔥 **Optimum Güvenli Tercih:** **{primary_pick}** | Gerçekleşme"
          f" İhtimali: **%{primary_prob:.1f}**"
      )
    else:
      primary_pick = f"{base_line} ALT"
      primary_prob = 100 - best_over_p
      st.error(
          f"🛡️ **Optimum Güvenli Tercih:** **{primary_pick}** | Gerçekleşme"
          f" İhtimali: **%{primary_prob:.1f}**"
      )

    st.markdown("### 📊 Tahmini Skorun Altındaki İddia Baremleri")
    st.info(
        "Aşağıdaki tabloda, modelin beklenen toplam skorunun **tamamen altında"
        " kalan** sayı baremleri ve bu baremlerin istatistiksel tutma"
        " olasılıkları listelenmiştir."
    )

    lines_to_check = [
        base_line - 1.5,
        base_line - 3.0,
        base_line - 4.5,
        base_line - 6.0,
        base_line - 7.5,
        base_line - 9.0,
        base_line - 10.5,
        base_line - 12.0,
        base_line - 13.5,
        base_line - 15.0,
    ]

    barem_data = []
    for line in lines_to_check:
      z = (exp_total - line) / std_dev
      over_p = norm.cdf(z) * 100
      under_p = 100 - over_p

      if over_p >= 85:
        rec = "🔥🔥 Kesin ÜST"
      elif over_p >= 70:
        rec = "🔥 Yüksek Oranlı ÜST"
      elif over_p >= 55:
        rec = "⚖️ İdeal ÜST"
      else:
        rec = "⚠️ Takip Edilmeli"

      barem_data.append({
          "İddia Baremi": f"{line:.1f}",
          "Üst İhtimali (%)": f"%{over_p:.1f}",
          "Alt İhtimali (%)": f"%{under_p:.1f}",
          "Analist Durumu": rec,
      })

    df_barem = pd.DataFrame(barem_data)
    st.dataframe(df_barem, use_container_width=True)

with tab2:
  st.subheader("📅 Günün Maçları & Canlı Fikstür Analiz Paneli")
  st.info(
      "Bugün oynanması planlanan öne çıkan NBA karşılaşmaları aşağıdadır."
      " İstediğiniz maçın üzerine tıklayarak veya hızlı analiz başlatarak"
      " detaylı yapay zeka tahminlerine ulaşabilirsiniz."
  )

  # Örnek Günün Maçları Fikstürü
  todays_matches = [
      ("Boston", "Miami"),
      ("Golden State", "LA Lakers"),
      ("Denver", "Dallas"),
      ("Milwaukee", "New York"),
      ("Phoenix", "Oklahoma"),
  ]

  for idx, (hm, aw) in enumerate(todays_matches):
    with st.container():
      col_m1, col_m2, col_m3, col_m4 = st.columns([2, 1, 2, 2])
      with col_m1:
        if hm in TEAM_LOGOS:
          st.image(TEAM_LOGOS[hm], width=35)
        st.write(f"**{hm}**")
      with col_m2:
        st.markdown(
            "<h4 style='text-align: center;'>VS</h4>", unsafe_allow_html=True
        )
      with col_m3:
        if aw in TEAM_LOGOS:
          st.image(TEAM_LOGOS[aw], width=35)
        st.write(f"**{aw}**")

      with col_m4:
        # Hızlı Analiz Butonu
        if st.button(
            f"🔍 Maçı Analiz Et", key=f"btn_match_{idx}", use_container_width=True
        ):
          st.session_state["sel_home"] = hm
          st.session_state["sel_away"] = aw
          st.success(
              f"✅ {hm} vs {aw} seçildi! (Üst sekmeden detayları"
              " inceleyebilirsiniz)"
          )
      st.markdown("---")

with tab3:
  st.subheader("East Konferansı Puan / Veri Matrisi")
  df_east = df_teams.loc[
      [t for t in EAST_TEAMS if t in df_teams.index]
  ].copy()
  df_east["Logo"] = [TEAM_LOGOS.get(t, "") for t in df_east.index]
  df_east = df_east[["Logo"] + [c for c in df_teams.columns]]
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
  df_west = df_west[["Logo"] + [c for c in df_teams.columns]]
  st.dataframe(
      df_west,
      use_container_width=True,
      column_config={
          "Logo": st.column_config.ImageColumn(
              "Logo", help="Batı Logosu", width="small"
          )
      },
  )
