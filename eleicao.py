import pandas as pd
import geopandas as gpd
import folium
import random

ARQ_VOTACAO = "votacao_secao_2026_OURO_BRANCO.csv"

df = pd.read_csv(ARQ_VOTACAO, sep=';', encoding='latin1', low_memory=False)

df['DS_CARGO'] = df['DS_CARGO'].astype(str).str.strip()
df['NM_VOTAVEL'] = df['NM_VOTAVEL'].astype(str).str.strip()
df['NM_MUNICIPIO'] = df['NM_MUNICIPIO'].astype(str).str.strip().str.upper()

df_ouro = df[(df['NM_MUNICIPIO'] == 'OURO BRANCO') & 
             (df['DS_CARGO'].str.contains('Presidente', case=False, na=False))].copy()

if df_ouro.empty:
    print("ERRO: Nenhum dado encontrado.")
    exit()

df_1t = df_ouro[df_ouro['DT_ELEICAO'] == '04/10/2026'].copy()
df_2t = df_ouro[df_ouro['DT_ELEICAO'] == '25/10/2026'].copy()

def pivot_votos(df_turno):
    pv = df_turno.pivot_table(
        index=['NR_ZONA', 'NR_SECAO'],
        columns='NM_VOTAVEL',
        values='QT_VOTOS',
        aggfunc='sum'
    ).fillna(0)
    for col in list(pv.columns):
        if any(x in str(col).upper() for x in ['BRANCO', 'NULO', 'BRANCOS', 'NULOS']):
            pv = pv.drop(columns=[col])
    pv['TOTAL_VALIDOS'] = pv.sum(axis=1)
    return pv

pv1 = pivot_votos(df_1t)
pv2 = pivot_votos(df_2t)

candidatos_1t = [c for c in pv1.columns if c != 'TOTAL_VALIDOS']
top_1t = pv1[candidatos_1t].sum().sort_values(ascending=False)
CAND_1T_A = top_1t.index[0]
CAND_1T_B = top_1t.index[1]

candidatos_2t = [c for c in pv2.columns if c != 'TOTAL_VALIDOS']
CAND_2T_A = candidatos_2t[0]
CAND_2T_B = candidatos_2t[1]

centro_lat, centro_lon = -20.5208, -43.6919
random.seed(42) 

pv1_reset = pv1.reset_index()
pv1_reset['Latitude'] = [centro_lat + random.uniform(-0.03, 0.03) for _ in range(len(pv1_reset))]
pv1_reset['Longitude'] = [centro_lon + random.uniform(-0.03, 0.03) for _ in range(len(pv1_reset))]
gdf_1t = gpd.GeoDataFrame(pv1_reset, geometry=gpd.points_from_xy(pv1_reset.Longitude, pv1_reset.Latitude), crs="EPSG:4326")

pv2_reset = pv2.reset_index()
pv2_reset['Latitude'] = [centro_lat + random.uniform(-0.03, 0.03) for _ in range(len(pv2_reset))]
pv2_reset['Longitude'] = [centro_lon + random.uniform(-0.03, 0.03) for _ in range(len(pv2_reset))]
gdf_2t = gpd.GeoDataFrame(pv2_reset, geometry=gpd.points_from_xy(pv2_reset.Longitude, pv2_reset.Latitude), crs="EPSG:4326")

for cand in [CAND_1T_A, CAND_1T_B]:
    gdf_1t[f'pct_{cand}'] = (gdf_1t[cand] / gdf_1t['TOTAL_VALIDOS'] * 100).round(2)

for cand in [CAND_2T_A, CAND_2T_B]:
    gdf_2t[f'pct_{cand}'] = (gdf_2t[cand] / gdf_2t['TOTAL_VALIDOS'] * 100).round(2)

def get_cor_vermelho(pct):
    if pct >= 70: return '#67000d'
    elif pct >= 60: return '#a50f15'
    elif pct >= 50: return '#cb181d'
    elif pct >= 40: return '#ef3b2c'
    else: return '#fcae91'

def get_cor_azul(pct):
    if pct >= 70: return '#08306b'
    elif pct >= 60: return '#2171b5'
    elif pct >= 50: return '#4292c6'
    elif pct >= 40: return '#6baed6'
    else: return '#c6dbef'

def criar_legenda_gradiente(titulo, tipo_cor, posicao='left'):
    if tipo_cor == 'vermelho':
        cores = ('#67000d', '#a50f15', '#cb181d', '#ef3b2c', '#fcae91')
    else:
        cores = ('#08306b', '#2171b5', '#4292c6', '#6baed6', '#c6dbef')
        
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

m1_a = folium.Map(location=[centro_lat, centro_lon], zoom_start=12, tiles='Esri.WorldStreetMap')

for idx, row in gdf_1t.iterrows():
    cor = get_cor_vermelho(row[f'pct_{CAND_1T_A}'])
    tooltip_html = f"<b>Zona:</b> {row['NR_ZONA']} | <b>Seção:</b> {row['NR_SECAO']}<br><b>% Votos ({CAND_1T_A}):</b> {row[f'pct_{CAND_1T_A}']}%"
    
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=12, color='black', weight=1, fill=True, fill_color=cor, fill_opacity=0.8,
        tooltip=tooltip_html
    ).add_to(m1_a)

m1_a.get_root().html.add_child(folium.Element(criar_legenda_gradiente('Legenda (% Votos)', 'vermelho')))
m1_a.save('mapa_1t_Lula.html')

m1_b = folium.Map(location=[centro_lat, centro_lon], zoom_start=12, tiles='Esri.WorldStreetMap')

for idx, row in gdf_1t.iterrows():
    cor = get_cor_azul(row[f'pct_{CAND_1T_B}'])
    tooltip_html = f"<b>Zona:</b> {row['NR_ZONA']} | <b>Seção:</b> {row['NR_SECAO']}<br><b>% Votos ({CAND_1T_B}):</b> {row[f'pct_{CAND_1T_B}']}%"
    
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=12, color='black', weight=1, fill=True, fill_color=cor, fill_opacity=0.8,
        tooltip=tooltip_html
    ).add_to(m1_b)

m1_b.get_root().html.add_child(folium.Element(criar_legenda_gradiente('Legenda (% Votos)', 'azul')))
m1_b.save('mapa_1t_Flavio.html')

m_dom = folium.Map(location=[centro_lat, centro_lon], zoom_start=12, tiles='Esri.WorldStreetMap')

for idx, row in gdf_2t.iterrows():
    votos_2t_A = row[CAND_2T_A]
    votos_2t_B = row[CAND_2T_B]
    if votos_2t_A > votos_2t_B:
        cor = get_cor_azul(row[f'pct_{CAND_2T_A}'])
        lider = CAND_2T_A
    else:
        cor = get_cor_vermelho(row[f'pct_{CAND_2T_B}'])
        lider = CAND_2T_B

    tooltip_html = (
        f"<b>Zona:</b> {row['NR_ZONA']} | <b>Seção:</b> {row['NR_SECAO']}<br>"
        f"<b>Líder:</b> {lider}<br>"
        f"<b>% {CAND_2T_A}:</b> {row[f'pct_{CAND_2T_A}']}%<br>"
        f"<b>% {CAND_2T_B}:</b> {row[f'pct_{CAND_2T_B}']}%"
    )
    
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=12, color='black', weight=1, fill=True, fill_color=cor, fill_opacity=0.8,
        tooltip=tooltip_html
    ).add_to(m_dom)

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
m_dom.get_root().html.add_child(folium.Element(legenda_dom))
m_dom.save('mapa_2t_dominancia.html')

print("RESUMO GERAL DA APURAÇÃO - OURO BRANCO (MG)")

total_absoluto_1t = df_1t['QT_VOTOS'].sum()
print(f"\nTotal de Comparecimento (Votos Totais 1T): {int(total_absoluto_1t)}")
print(f"Total de Votos Válidos 1T: {int(pv1['TOTAL_VALIDOS'].sum())}")
print("Top 5 Candidatos no município:")
for i, (cand, votos) in enumerate(top_1t.head(5).items(), 1):
    pct = (votos / pv1['TOTAL_VALIDOS'].sum()) * 100
    print(f"  {i}º - {cand}: {int(votos)} votos ({pct:.2f}%)")

print(f"\nTotal de Comparecimento (Votos Totais 2T): {int(df_2t['QT_VOTOS'].sum())}")
print(f"Total de Votos Válidos 2T: {int(pv2['TOTAL_VALIDOS'].sum())}")
for cand in [CAND_2T_A, CAND_2T_B]:
    votos = pv2[cand].sum()
    pct = (votos / pv2['TOTAL_VALIDOS'].sum()) * 100
    print(f"  {cand}: {int(votos)} votos ({pct:.2f}%)")

print("\nCONTAGEM DE SEÇÕES DOMINADAS (2º Turno)")
vitorias_A = (gdf_2t[CAND_2T_A] > gdf_2t[CAND_2T_B]).sum()
vitorias_B = (gdf_2t[CAND_2T_B] > gdf_2t[CAND_2T_A]).sum()
print(f"  Seções dominadas por {CAND_2T_A}: {vitorias_A}")
print(f"  Seções dominadas por {CAND_2T_B}: {vitorias_B}")