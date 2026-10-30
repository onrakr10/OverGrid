import numpy as np
import pandas as pd
from scipy.stats import norm
import streamlit as st

st.set_page_config(
    page_title="OverGrid Elite - NBA Advanced Analytics Engine",
    layout="wide",
    initial_sidebar_state="expanded",
)

# STİL TASARIMI (DARK MODE & ELITE UI)
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e222b; padding: 15px; border-radius: 10px; border: 1px solid #2e3644; }
    .badge-banko { background-color: #00c853; color: white; padding: 6px 12px; border-radius: 6px; font-weight: bold; }
    .badge-risk { background-color: #ff9800; color: white; padding: 6px 12px; border-radius: 6px; font-weight: bold; }
    </style>
""",
    unsafe_allow_html=True,
)

# 1. 30 TAKIM İÇİN KESİNTİSİZ WIKIMEDIA PNG LOGO LİSTESİ
TEAM_LOGOS = {
    "Toronto": "https://upload.wikimedia.org/wikipedia/en/thumb/7/72/Toronto_Raptors_logo.svg/100px-Toronto_Raptors_logo.svg.png",
    "Miami": "https://upload.wikimedia.org/wikipedia/en/thumb/f/fb/Miami_Heat_logo.svg/100px-Miami_Heat_logo.svg.png",
    "Boston": "https://upload.wikimedia.org/wikipedia/en/thumb/2/29/Boston_Celtics_logo.svg/100px-Boston_Celtics_logo.svg.png",
    "Dallas": "https://upload.wikimedia.org/wikipedia/en/thumb/9/97/Dallas_Mavericks_logo.svg/100px-Dallas_Mavericks_logo.svg.png",
    "Denver": "https://upload.wikimedia.org/wikipedia/en/thumb/7/76/Denver_Nuggets_logo_%282018%29.svg/100px-Denver_Nuggets_logo_%282018%29.svg.png",
    "Utah": "https://upload.wikimedia.org/wikipedia/en/thumb/b/be/Utah_Jazz_logo_%282022%29.svg/100px-Utah_Jazz_logo_%282022%29.svg.png",
    "LA Clippers": "https://upload.wikimedia.org/wikipedia/en/thumb/e/ed/Los_Angeles_Clippers_%282024%29_logo.svg/100px-Los_Angeles_Clippers_%282024%29_logo.svg.png",
    "Golden State": "https://upload.wikimedia.org/wikipedia/en/thumb/0/01/Golden_State_Warriors_logo.svg/100px-Golden_State_Warriors_logo.svg.png",
    "Detroit": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c9/Detroit_Pistons_logo_%282017%29.svg/100px-Detroit_Pistons_logo_%282017%29.svg.png",
    "Phoenix": "https://upload.wikimedia.org/wikipedia/en/thumb/d/df/Phoenix_Suns_logo.svg/100px-Phoenix_Suns_logo.svg.png",
    "Phila": "https://upload.wikimedia.org/wikipedia/en/thumb/4/46/Philadelphia_76ers_logo.svg/100px-Philadelphia_76ers_logo.svg.png",
    "New York": "https://upload.wikimedia.org/wikipedia/en/thumb/2/2b/New_York_Knicks_logo.svg/100px-New_York_Knicks_logo.svg.png",
    "Atlanta": "https://upload.wikimedia.org/wikipedia/en/thumb/2/24/Atlanta_Hawks_logo_%282020%29.svg/100px-Atlanta_Hawks_logo_%282020%29.svg.png",
    "Brooklyn": "https://upload.wikimedia.org/wikipedia/en/thumb/4/44/Brooklyn_Nets_logo.svg/100px-Brooklyn_Nets_logo.svg.png",
    "Charlotte": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c4/Charlotte_Hornets_%282014%29.svg/100px-Charlotte_Hornets_%282014%29.svg.png",
    "Chicago": "https://upload.wikimedia.org/wikipedia/en/thumb/6/67/Chicago_Bulls_logo.svg/100px-Chicago_Bulls_logo.svg.png",
    "Cleveland": "https://upload.wikimedia.org/wikipedia/en/thumb/0/04/Cleveland_Cavaliers_logo.svg/100px-Cleveland_Cavaliers_logo.svg.png",
    "Indiana": "https://upload.wikimedia.org/wikipedia/en/thumb/1/1b/Indiana_Pacers_logo_%282017%29.svg/100px-Indiana_Pacers_logo_%282017%29.svg.png",
    "Milwaukee": "https://upload.wikimedia.org/wikipedia/en/thumb/4/4a/Milwaukee_Bucks_logo.svg/100px-Milwaukee_Bucks_logo.svg.png",
    "Orlando": "https://upload.wikimedia.org/wikipedia/en/thumb/1/10/Orlando_Magic_logo.svg/100px-Orlando_Magic_logo.svg.png",
    "Washington": "https://upload.wikimedia.org/wikipedia/en/thumb/0/02/Washington_Wizards_logo.svg/100px-Washington_Wizards_logo.svg.png",
    "Houston": "https://upload.wikimedia.org/wikipedia/en/thumb/2/28/Houston_Rockets_logo_%282020%29.svg/100px-Houston_Rockets_logo_%282020%29.svg.png",
    "LA Lakers": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Los_Angeles_Lakers_logo.svg/100px-Los_Angeles_Lakers_logo.svg.png",
    "Memphis": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f1/Memphis_Grizzlies.svg/100px-Memphis_Grizzlies.svg.png",
    "Minnesota": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c2/Minnesota_Timberwolves_logo_%282017%29.svg/100px-Minnesota_Timberwolves_logo_%282017%29.svg.png",
    "New Orleans": "https://upload.wikimedia.org/wikipedia/en/thumb/0/0d/New_Orleans_Pelicans_logo.svg/100px-New_Orleans_Pelicans_logo.svg.png",
    "Oklahoma": "https://upload.wikimedia.org/wikipedia/en/thumb/5/5d/Oklahoma_City_Thunder_logo.svg/100px-Oklahoma_City_Thunder_logo.svg.png",
    "Portland": "https://upload.wikimedia.org/wikipedia/en/thumb/2/21/Portland_Trail_Blazers_logo.svg/100px-Portland_Trail_Blazers_logo.svg.png",
    "Sacramento": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c7/Sacramento_Kings_logo_%282016%29.svg/100px-Sacramento_Kings_logo_%282016%29.svg.png",
    "San Antonio": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a2/San_Antonio_Spurs_logo.svg/100px-San_Antonio_Spurs_logo.svg.png",
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

# 3. ELITE NBA RESMİ İSTATİSTİK MATRİSİ
# Format: [Ev Atığı, Ev Yediği, Dep Atığı, Dep Yediği, Tempo, Form]
DEFAULT_ELITE_DATA = {
    "Toronto": [126.2, 104.8, 112.75, 117.5, 101.5, 1.03],
    "Miami": [120.33, 123.83, 120.75, 118.25, 98.2, 1.00],
    "Boston": [124.8, 105.0, 120.67, 118.0, 100.8, 1.06],
    "Dallas": [110.2, 117.8, 119.0, 114.25, 99.4, 0.98],
    "Denver": [121.25, 126.5, 107.2, 104.2, 97.9, 1.02],
    "Utah": [114.0, 117.33, 110.33, 112.0, 102.1, 0.95],
    "LA Clippers": [108.5, 102.5, 108.0, 115.67, 98.0, 0.99],
    "Golden State": [117.75, 108.25, 114.29, 114.57, 103.4, 1.04],
    "Detroit": [114.0, 108.5, 113.4, 107.0, 100.0, 0.97],
    "Phoenix": [116.33, 113.0, 104.8, 121.0, 99.1, 1.01],
    "Phila": [114.8, 110.0, 108.5, 116.75, 99.8, 1.00],
    "New York": [108.0, 111.67, 107.75, 125.5, 96.5, 1.03],
    "Atlanta": [116.75, 123.0, 124.5, 111.67, 102.8, 0.99],
    "Brooklyn": [108.67, 118.0, 125.6, 121.2, 100.4, 0.96],
    "Charlotte": [100.2, 111.0, 97.5, 107.5, 98.5, 0.94],
    "Chicago": [120.8, 118.8, 115.2, 126.2, 101.2, 1.00],
    "Cleveland": [121.0, 117.2, 111.0, 123.0, 99.5, 1.05],
    "Indiana": [116.2, 118.8, 115.25, 109.75, 103.0, 1.02],
    "Milwaukee": [107.4, 121.4, 115.6, 122.6, 101.0, 1.01],
    "Orlando": [121.5, 119.5, 109.25, 117.0, 97.8, 1.02],
    "Washington": [116.5, 116.75, 111.0, 113.4, 102.5, 0.95],
    "Houston": [119.75, 110.25, 125.5, 110.25, 99.0, 1.03],
    "LA Lakers": [115.0, 115.0, 115.0, 109.25, 100.6, 1.02],
    "Memphis": [119.0, 107.67, 116.0, 109.6, 102.2, 1.01],
    "Minnesota": [112.33, 113.67, 120.25, 113.5, 98.4, 1.04],
    "New Orleans": [106.0, 111.0, 117.8, 119.2, 100.1, 0.98],
    "Oklahoma": [110.83, 107.17, 102.75, 113.25, 101.9, 1.07],
    "Portland": [123.5, 100.5, 123.0, 118.75, 100.8, 0.97],
    "Sacramento": [108.25, 122.0, 102.4, 120.4, 102.0, 0.99],
    "San Antonio": [118.17, 109.33, 111.5, 109.5, 101.4, 1.00],
}

if "elite_data" not in st.session_state:
  st.session_state["elite_data"] = DEFAULT_ELITE_DATA

# --- SOL KENAR ÇUBUĞU (SIDEBAR) ---
st.sidebar.header("🏀 Takım Veri Düzenleme Paneli")
st.sidebar.info(
    "Takımların iç saha ve deplasman skorlarını, temposunu ve formunu buradan"
    " güncelleyebilirsin."
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
ed_tempo = st.sidebar.number_input(
    "Tempo (Hücum Hızı)", value=float(curr[4]), step=0.1
)
ed_form = st.sidebar.number_input(
    "Son 10 Maç Form Çarpanı", value=float(curr[5]), step=0.01
)

if st.sidebar.button("💾 Verileri Kaydet", use_container_width=True):
  st.session_state["elite_data"][selected_edit_team] = [
      ed_ev_at,
      ed_ev_yed,
      ed_dep_at,
      ed_dep_yed,
      ed_tempo,
      ed_form,
  ]
  st.sidebar.success(f"✅ {selected_edit_team} güncellendi!")

# Güncel Veri Çerçevesi Oluşturma
ELITE_DATA = st.session_state["elite_data"]
df_teams = pd.DataFrame.from_dict(
    ELITE_DATA,
    orient="index",
    columns=["Ev Atığı", "Ev Yediği", "Dep Atığı", "Dep Yediği", "Tempo", "Form"],
)

# Lig Ortalamaları
league_avg_home_scored = df_teams["Ev Atığı"].mean()
league_avg_dep_scored = df_teams["Dep Atığı"].mean()
LEAGUE_AVG_SCORED = (league_avg_home_scored + league_avg_dep_scored) / 2
LEAGUE_AVG_TEMPO = df_teams["Tempo"].mean()

# ANA BAŞLIK
st.title("⚡ OverGrid Pro - Elite AI NBA Prediction Engine")
st.caption(
    "Çapraz İç/Dış Saha Analizi, Deplasman Performans Matrisi & Normal Dağılım"
    " Sistemi"
)

# SEKME YAPISI
tab1, tab2, tab3 = st.tabs(
    ["🎯 Profesyonel Maç Analizi", "📅 Maç Günü", "📊 Konferans Puan/Veri Grid'i"]
)

with tab1:
  all_teams_sorted = sorted(list(ELITE_DATA.keys()))

  c1, c2 = st.columns(2)
  with c1:
    home_team = st.selectbox("Ev Sahibi Takım", all_teams_sorted, index=0)
  with c2:
    away_team = st.selectbox("Deplasman Takım", all_teams_sorted, index=1)

  # LOGOLAR VE TAKIM BİLGİLERİ
  col_logo_h, col_logo_mid, col_logo_a = st.columns([2, 1, 2])
  with col_logo_h:
    if home_team in TEAM_LOGOS:
      st.image(TEAM_LOGOS[home_team], width=75)
    st.markdown(f"### 🏠 {home_team} (Ev Sahibi)")
  with col_logo_mid:
    st.markdown("<h2 style='text-align: center;'>VS</h2>", unsafe_allow_html=True)
  with col_logo_a:
    if away_team in TEAM_LOGOS:
      st.image(TEAM_LOGOS[away_team], width=75)
    st.markdown(f"### ✈️ {away_team} (Deplasman)")

  if home_team == away_team:
    st.error("⚠️ Lütfen iki farklı takım seçiniz.")
  else:
    # --- PRO ÇAPRAZ HESAPLAMA MOTORU (EV SAHİBİ & DEPLASMAN KARIŞIMI) ---
    h_data = df_teams.loc[home_team]
    a_data = df_teams.loc[away_team]

    # Ev sahibinin evdeki hücumu ile deplasman takımının deplasmandaki savunmasının çaprazlanması
    h_off_power = h_data["Ev Atığı"] / LEAGUE_AVG_SCORED
    a_def_power = a_data["Dep Yediği"] / LEAGUE_AVG_SCORED

    # Deplasman takımının deplasman hücumu ile ev sahibinin evdeki savunmasının çaprazlanması
    a_off_power = a_data["Dep Atığı"] / LEAGUE_AVG_SCORED
    h_def_power = h_data["Ev Yediği"] / LEAGUE_AVG_SCORED

    # Tempo ve Form Katsayısı
    match_tempo_factor = ((h_data["Tempo"] + a_data["Tempo"]) / 2) / LEAGUE_AVG_TEMPO

    # Beklenen Skorlar
    exp_home = (
        h_off_power
        * a_def_power
        * LEAGUE_AVG_SCORED
        * match_tempo_factor
        * h_data["Form"]
        * 1.01
    )
    exp_away = (
        a_off_power
        * h_def_power
        * LEAGUE_AVG_SCORED
        * match_tempo_factor
        * a_data["Form"]
    )
    exp_total = exp_home + exp_away

    std_dev = 11.2

    st.markdown("---")

    # METRİKLER
    m1, m2, m3 = st.columns(3)
    m1.metric("Ev Sahibi Skor Beklentisi", f"{exp_home:.1f}")
    m2.metric("Deplasman Skor Beklentisi", f"{exp_away:.1f}")
    m3.metric("🎯 Çapraz Optimizasyon Toplam Skor", f"{exp_total:.1f}")

    st.markdown(
        "### 🏆 220.5 - 234.5 Aralığı Kesintisiz 0.5'li ÜST Barem Analizi"
    )
    st.info(
        "İç/dış saha performansları, deplasman atıp yediği skorlar ve tempo"
        " faktörü çaprazlanarak elde edilen **0.5'li iddia baremleri** ve"
        " **ÜST** tutma olasılıkları aşağıdadır."
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

with tab2:
  st.subheader("📅 Günün Maçları & Canlı Fikstür Analiz Paneli")
  st.info(
      "Bugün oynanması planlanan öne çıkan NBA karşılaşmaları ve başlama"
      " saatleri (TSİ) aşağıdadır."
  )

  todays_matches = [
      ("Boston", "Miami", "02:30 TSİ"),
      ("Golden State", "LA Lakers", "05:00 TSİ"),
      ("Denver", "Dallas", "03:00 TSİ"),
      ("Milwaukee", "New York", "02:00 TSİ"),
      ("Phoenix", "Oklahoma", "04:30 TSİ"),
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
          st.success(f"✅ {hm} vs {aw} seçildi!")
      st.markdown("---")

with tab3:
  st.subheader("East Konferansı Puan / Veri Matrisi")
  df_east = df_teams.loc[
      [t for t in EAST_TEAMS if t in df_teams.index]
  ].copy()
  df_east["Logo"] = [TEAM_LOGOS.get(t, "") for t in df_east.index]
  df_east = df_east[
      ["Logo", "Ev Atığı", "Ev Yediği", "Dep Atığı", "Dep Yediği", "Tempo", "Form"]
  ]
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
      ["Logo", "Ev Atığı", "Ev Yediği", "Dep Atığı", "Dep Yediği", "Tempo", "Form"]
  ]
  st.dataframe(
      df_west,
      use_container_width=True,
      column_config={
          "Logo": st.column_config.ImageColumn(
              "Logo", help="Batı Logosu", width="small"
          )
      },
  )
