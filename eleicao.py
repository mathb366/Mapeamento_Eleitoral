import pandas as pd
import numpy as np
import folium

ARQ_SECOES = "votacao_secao_2026_MG_Ouro_Branco.csv"
ARQ_LOCAIS = "eleitorado_local_votacao_2026_MG_Ouro_Branco.csv"

df_sec = pd.read_csv(ARQ_SECOES, sep=";", encoding="latin-1", dtype=str, keep_default_na=False)
df_sec["QT_VOTOS"] = pd.to_numeric(df_sec["QT_VOTOS"], errors="coerce")
df_sec["NR_TURNO"] = pd.to_numeric(df_sec["NR_TURNO"], errors="coerce")
df_sec["NR_LOCAL_VOTACAO"] = pd.to_numeric(df_sec["NR_LOCAL_VOTACAO"], errors="coerce")
df_sec["NR_SECAO"] = pd.to_numeric(df_sec["NR_SECAO"], errors="coerce")
df_sec["NR_ZONA"] = pd.to_numeric(df_sec["NR_ZONA"], errors="coerce")

df_loc = pd.read_csv(ARQ_LOCAIS, sep=";", encoding="latin-1", dtype=str, keep_default_na=False)
df_loc["NR_LOCAL_VOTACAO"] = pd.to_numeric(df_loc["NR_LOCAL_VOTACAO"], errors="coerce")
df_loc["NR_SECAO"] = pd.to_numeric(df_loc["NR_SECAO"], errors="coerce")
df_loc["NR_ZONA"] = pd.to_numeric(df_loc["NR_ZONA"], errors="coerce")
df_loc["NR_LATITUDE"] = pd.to_numeric(df_loc["NR_LATITUDE"].str.replace(",", "."), errors="coerce")
df_loc["NR_LONGITUDE"] = pd.to_numeric(df_loc["NR_LONGITUDE"].str.replace(",", "."), errors="coerce")

locais = df_loc[["NR_ZONA","NR_SECAO","NR_LOCAL_VOTACAO","NM_LOCAL_VOTACAO","NR_LATITUDE","NR_LONGITUDE"]].copy()
locais = locais.rename(columns={"NR_LATITUDE":"LAT","NR_LONGITUDE":"LON"})
locais = locais.dropna(subset=["LAT","LON"])

cand_lula = "LUIZ INÁCIO LULA DA SILVA"
cand_bolso = "FLAVIO NANTES BOLSONARO"

sec = df_sec[(df_sec["CD_CARGO"]=="1")].copy()

def pivot_por_secao(df, turno):
    d = df[df["NR_TURNO"]==turno].copy()
    piv = d.pivot_table(
        index=["NR_ZONA","NR_SECAO"],
        columns="NM_VOTAVEL",
        values="QT_VOTOS",
        aggfunc="sum",
        fill_value=0
    )
    for col in list(piv.columns):
        if any(x in str(col).upper() for x in ["BRANCO","NULO","BRANCOS","NULOS"]):
            piv = piv.drop(columns=[col])
    piv["TOTAL_VALIDOS"] = piv.sum(axis=1)
    return piv.reset_index()

pv1 = pivot_por_secao(sec, 1)
pv2 = pivot_por_secao(sec, 2)

for c in [cand_lula, cand_bolso]:
    if c not in pv1.columns:
        pv1[c] = 0
    if c not in pv2.columns:
        pv2[c] = 0

pv1["PCT_LULA"] = np.where(pv1["TOTAL_VALIDOS"]>0, pv1[cand_lula]/pv1["TOTAL_VALIDOS"]*100, np.nan)
pv1["PCT_BOLSO"] = np.where(pv1["TOTAL_VALIDOS"]>0, pv1[cand_bolso]/pv1["TOTAL_VALIDOS"]*100, np.nan)
pv2["PCT_LULA"] = np.where(pv2["TOTAL_VALIDOS"]>0, pv2[cand_lula]/pv2["TOTAL_VALIDOS"]*100, np.nan)
pv2["PCT_BOLSO"] = np.where(pv2["TOTAL_VALIDOS"]>0, pv2[cand_bolso]/pv2["TOTAL_VALIDOS"]*100, np.nan)

pv1 = pv1.merge(locais, on=["NR_ZONA","NR_SECAO"], how="inner")
pv2 = pv2.merge(locais, on=["NR_ZONA","NR_SECAO"], how="inner")

centro_lat, centro_lon = -20.5208, -43.6919

def get_cor_vermelho(pct):
    if pct >= 70: return "#67000d"
    elif pct >= 60: return "#a50f15"
    elif pct >= 50: return "#cb181d"
    elif pct >= 40: return "#ef3b2c"
    else: return "#fcae91"

def get_cor_azul(pct):
    if pct >= 70: return "#08306b"
    elif pct >= 60: return "#2171b5"
    elif pct >= 50: return "#4292c6"
    elif pct >= 40: return "#6baed6"
    else: return "#c6dbef"

def criar_legenda_gradiente(titulo, tipo_cor, posicao="left"):
    if tipo_cor == "vermelho":
        cores = ("#67000d", "#a50f15", "#cb181d", "#ef3b2c", "#fcae91")
    else:
        cores = ("#08306b", "#2171b5", "#4292c6", "#6baed6", "#c6dbef")
    return f"""
    <div style="position: fixed; bottom: 50px; {posicao}: 50px; width: 150px; height: 120px;
                background-color: white; border:2px solid grey; z-index:9999; font-size:14px;
                padding: 10px; border-radius: 5px;">
        <b>{titulo}</b><br>
        <i style="background:{cores[0]}; width:15px; height:15px; float:left; margin-right:5px; border:1px solid black;"></i> > 70%<br>
        <i style="background:{cores[1]}; width:15px; height:15px; float:left; margin-right:5px; border:1px solid black;"></i> 60% - 70%<br>
        <i style="background:{cores[2]}; width:15px; height:15px; float:left; margin-right:5px; border:1px solid black;"></i> 50% - 60%<br>
        <i style="background:{cores[3]}; width:15px; height:15px; float:left; margin-right:5px; border:1px solid black;"></i> 40% - 50%<br>
        <i style="background:{cores[4]}; width:15px; height:15px; float:left; margin-right:5px; border:1px solid black;"></i> < 40%<br>
    </div>
    """

m1_lula = folium.Map(location=[centro_lat, centro_lon], zoom_start=12, tiles="Esri.WorldStreetMap")
for _, row in pv1.iterrows():
    if pd.isna(row["PCT_LULA"]):
        continue
    cor = get_cor_vermelho(row["PCT_LULA"])
    tooltip = (
        f"<b>Local:</b> {row['NM_LOCAL_VOTACAO']}<br>"
        f"<b>Zona:</b> {row['NR_ZONA']} | <b>Seção:</b> {row['NR_SECAO']}<br>"
        f"<b>% Lula:</b> {row['PCT_LULA']:.2f}%<br>"
        f"<b>Votos válidos:</b> {int(row['TOTAL_VALIDOS'])}"
    )
    folium.CircleMarker(
        location=[row["LAT"], row["LON"]],
        radius=12, color="black", weight=1, fill=True, fill_color=cor, fill_opacity=0.8,
        tooltip=tooltip
    ).add_to(m1_lula)
m1_lula.get_root().html.add_child(folium.Element(criar_legenda_gradiente("% Lula – 1º Turno", "vermelho")))
m1_lula.save("mapa_1t_lula_bolinhas.html")

m1_bolso = folium.Map(location=[centro_lat, centro_lon], zoom_start=12, tiles="Esri.WorldStreetMap")
for _, row in pv1.iterrows():
    if pd.isna(row["PCT_BOLSO"]):
        continue
    cor = get_cor_azul(row["PCT_BOLSO"])
    tooltip = (
        f"<b>Local:</b> {row['NM_LOCAL_VOTACAO']}<br>"
        f"<b>Zona:</b> {row['NR_ZONA']} | <b>Seção:</b> {row['NR_SECAO']}<br>"
        f"<b>% Bolsonaro:</b> {row['PCT_BOLSO']:.2f}%<br>"
        f"<b>Votos válidos:</b> {int(row['TOTAL_VALIDOS'])}"
    )
    folium.CircleMarker(
        location=[row["LAT"], row["LON"]],
        radius=12, color="black", weight=1, fill=True, fill_color=cor, fill_opacity=0.8,
        tooltip=tooltip
    ).add_to(m1_bolso)
m1_bolso.get_root().html.add_child(folium.Element(criar_legenda_gradiente("% Bolsonaro – 1º Turno", "azul")))
m1_bolso.save("mapa_1t_bolsonaro_bolinhas.html")

m2_dom = folium.Map(location=[centro_lat, centro_lon], zoom_start=12, tiles="Esri.WorldStreetMap")
for _, row in pv2.iterrows():
    if pd.isna(row["PCT_LULA"]) or pd.isna(row["PCT_BOLSO"]):
        continue
    if row["PCT_LULA"] > row["PCT_BOLSO"]:
        cor = get_cor_vermelho(row["PCT_LULA"])
        lider = cand_lula
    else:
        cor = get_cor_azul(row["PCT_BOLSO"])
        lider = cand_bolso
    tooltip = (
        f"<b>Local:</b> {row['NM_LOCAL_VOTACAO']}<br>"
        f"<b>Zona:</b> {row['NR_ZONA']} | <b>Seção:</b> {row['NR_SECAO']}<br>"
        f"<b>Líder:</b> {lider}<br>"
        f"<b>% Lula:</b> {row['PCT_LULA']:.2f}%<br>"
        f"<b>% Bolsonaro:</b> {row['PCT_BOLSO']:.2f}%"
    )
    folium.CircleMarker(
        location=[row["LAT"], row["LON"]],
        radius=12, color="black", weight=1, fill=True, fill_color=cor, fill_opacity=0.8,
        tooltip=tooltip
    ).add_to(m2_dom)

legenda_dom = """
<div style="position: fixed; bottom: 50px; left: 50px; width: 250px; height: 80px;
            background-color: white; border:2px solid grey; z-index:9999; font-size:14px;
            padding: 10px; border-radius: 5px;">
    <b>Zonas de Dominância (2º Turno)</b><br>
    <i style="background:#cb181d; width:15px; height:15px; float:left; margin-right:5px; border:1px solid black;"></i> LUIZ INÁCIO LULA DA SILVA (PT)<br>
    <i style="background:#4292c6; width:15px; height:15px; float:left; margin-right:5px; border:1px solid black;"></i> FLAVIO NANTES BOLSONARO<br>
    <small><i>(Quanto mais escuro, maior a % de votos)</i></small>
</div>
"""
m2_dom.get_root().html.add_child(folium.Element(legenda_dom))
m2_dom.save("mapa_2t_dominancia_bolinhas.html")

print("RESUMO GERAL DA APURAÇÃO - OURO BRANCO (MG)")

total_absoluto_1t = sec[sec["NR_TURNO"]==1]["QT_VOTOS"].sum()
print(f"\nTotal de Comparecimento (Votos Totais 1T): {int(total_absoluto_1t)}")
print(f"Total de Votos Válidos 1T: {int(pv1['TOTAL_VALIDOS'].sum())}")
print("Top 5 Candidatos no município:")
top_1t = pv1.drop(columns=["NR_ZONA","NR_SECAO","TOTAL_VALIDOS","PCT_LULA","PCT_BOLSO","NR_LOCAL_VOTACAO","NM_LOCAL_VOTACAO","LAT","LON"]).sum().sort_values(ascending=False)
for i, (cand, votos) in enumerate(top_1t.head(5).items(), 1):
    pct = (votos / pv1['TOTAL_VALIDOS'].sum()) * 100
    print(f"  {i}º - {cand}: {int(votos)} votos ({pct:.2f}%)")

total_absoluto_2t = sec[sec["NR_TURNO"]==2]["QT_VOTOS"].sum()
print(f"\nTotal de Comparecimento (Votos Totais 2T): {int(total_absoluto_2t)}")
print(f"Total de Votos Válidos 2T: {int(pv2['TOTAL_VALIDOS'].sum())}")
for cand in [cand_lula, cand_bolso]:
    votos = pv2[cand].sum()
    pct = (votos / pv2['TOTAL_VALIDOS'].sum()) * 100
    print(f"  {cand}: {int(votos)} votos ({pct:.2f}%)")

print("\nCONTAGEM DE SEÇÕES DOMINADAS (2º Turno)")
vitorias_lula = (pv2["PCT_LULA"] > pv2["PCT_BOLSO"]).sum()
vitorias_bolso = (pv2["PCT_BOLSO"] > pv2["PCT_LULA"]).sum()
print(f"  Seções dominadas por {cand_lula}: {vitorias_lula}")
print(f"  Seções dominadas por {cand_bolso}: {vitorias_bolso}")

print("\nMapas gerados: mapa_1t_lula_bolinhas.html, mapa_1t_bolsonaro_bolinhas.html, mapa_2t_dominancia_bolinhas.html")