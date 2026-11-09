# Relatório de Mapeamento Eleitoral e Visualização Geospacial - Ouro Branco (MG)

## 1. Obtenção e Tratamento Inicial dos Dados

Os dados brutos foram obtidos do portal de dados abertos do Tribunal Superior Eleitoral (TSE), referentes à votação por seção eleitoral para o cargo de Presidente da República nas eleições de 2026.

Inicialmente, foi disponibilizado o arquivo nacional com todos os municípios do Brasil. Para garantir a eficiência do processamento e atender aos requisitos de armazenamento do projeto, foi realizada uma filtragem prévia.

### 1.1 Redução e Filtragem do Arquivo CSV (Otimização para o GitHub)

O arquivo original do TSE possui milhões de linhas e dezenas de colunas, ultrapassando em muito o limite de tamanho de arquivo aceito pelo GitHub (100 MB). Para resolver esse problema e permitir que os dados brutos fossem versionados no repositório, foi criado um script em Python (`reduzir_arquivo.py`) que realizou duas ações:

*   **Filtro Geográfico:** Manteve apenas as linhas onde o município era "OURO BRANCO".
*   **Filtro de Colunas:** Removeu todas as colunas que não seriam utilizadas na análise (como `DT_GERACAO`, `CD_TIPO_ELEICAO`, `SQ_CANDIDATO`, `DS_LOCAL_VOTACAO_ENDERECO`, etc.), mantendo apenas 7 colunas essenciais: `NM_MUNICIPIO`, `DS_CARGO`, `NM_VOTAVEL`, `DT_ELEICAO`, `NR_ZONA`, `NR_SECAO` e `QT_VOTOS`.

Com isso, foi gerado o arquivo `votacao_secao_2026_OURO_BRANCO.csv`, reduzindo o tamanho de mais de 1 GB para poucos KBs, possibilitando a submissão no GitHub sem perda de integridade dos dados analisados.

## 2. Limpeza, Filtragem e Unificação no Pandas

No script de geração dos mapas (`eleicao.py`), o arquivo reduzido foi carregado no `pandas`. O filtro foi realizado novamente para garantir a seleção do cargo de "Presidente". Os dados foram separados entre 1º Turno (data `04/10/2026`) e 2º Turno (data `25/10/2026`). Votos brancos e nulos foram removidos da base para o cálculo dos percentuais válidos. A chave geográfica (Zona e Seção) foi padronizada para garantir a unificação com os dados geográficos.

## 3. Análise do 1º Turno (Mapas Cloropléticos)

Para atender ao requisito de mapear os principais candidatos, foram gerados dois mapas separados, um para **Lula** e outro para **Flávio Bolsonaro**.

*   **O Fato (Análise):** No 1º turno em Ouro Branco, o candidato Lula foi o mais votado no município. Os mapas revelam uma heterogeneidade espacial: enquanto algumas seções eleitorais apresentam forte dominância de um candidato, outras seções vizinhas demonstram preferência pelo adversário. Isso indica que o eleitorado do município não é homogêneo e as preferências variam conforme a região.
*   **O Design (Justificativa Gráfica):**
    *   **Cores e Escala:** Foi utilizada uma paleta sequencial para cada candidato. Lula foi representado em tons de **Vermelho** (`#67000d` a `#fcae91`) e Flávio em tons de **Azul** (`#08306b` a `#c6dbef`).
    *   **Classes:** Os percentuais foram divididos em 5 classes (acima de 70%, 60-70%, 50-60%, 40-50% e abaixo de 40%), permitindo uma leitura rápida das áreas de maior e menor concentração de votos.
    *   **Opacidade:** Foi aplicada opacidade de 0.8 nas bolhas para garantir que o mapa de ruas (mapa base) permanecesse legível por baixo dos dados eleitorais.

## 4. Análise do 2º Turno e Comparação Espacial

*   **O Fato (Análise):** No 2º turno, a disputa entre os dois finalistas se acirrou. Através do mapa de dominância, é possível observar as "zonas de disputa". Em determinadas seções, Flávio Bolsonaro lidera, enquanto em outras, Lula leva a vantagem. A cor de cada bolinha no mapa muda de acordo com o candidato vencedor em cada seção, facilitando a visualização geográfica dessa divisão.
*   **O Design (Justificativa Gráfica):**
    *   **Mapa de Dominância:** Para atender exatamente à exigência do PDF, foi criado um mapa temático único onde a cor da bolinha indica o líder da seção. Se o líder é Lula, a bolinha é **Vermelha**; se é Flávio, é **Azul**.
    *   **Paleta de Cores:** Além da cor indicar o vencedor, a intensidade da cor (mais claro ou mais escuro) indica a porcentagem de votos daquele líder na seção, seguindo o mesmo gradiente do 1º turno.

## 5. Recursos Interativos e Tooltips Customizados

Para atender ao requisito de interatividade, todos os mapas foram exportados em HTML.

*   **O Design:**
    *   **Tooltip Customizado:** Foi utilizado o `folium.CircleMarker` com um `tooltip` HTML customizado via CSS. Ao passar o mouse sobre qualquer bolinha, o usuário visualiza:
        *   **No 1º Turno:** O número da Zona, o número da Seção e a porcentagem exata de votos daquele candidato.
        *   **No 2º Turno:** O número da Zona, o número da Seção, qual é o **Candidato Líder** naquela seção e o percentual relativo de votos de cada um dos dois finalistas.
    *   **Legendas Customizadas:** Foram inseridas legendas em HTML/JS no canto dos mapas para explicar o significado das escalas de cores.
    *   **Controle de Camadas:** Nos mapas comparativos, foi utilizado o `LayerControl` para que o usuário possa ligar/desligar as camadas e visualizar as áreas de dominância de forma isolada.

## 6. Limitações Técnicas e a Técnica de Dispersão Geográfica (Jittering)

Uma limitação importante encontrada nos dados abertos do TSE é a **ausência de coordenadas geográficas** (latitude e longitude) para cada seção eleitoral. O TSE fornece apenas o endereço em texto (ex: "ESCOLA ESTADUAL MANOEL CORREIA").

Para contornar essa limitação sem comprometer a análise estatística dos votos, foi adotada a técnica de **dispersão geográfica (Jittering)**. Os dados de votação foram plotados em um raio aproximado de 3 km em torno do centroide do município de Ouro Branco. Embora as posições exatas das seções não sejam mostradas, a distribuição proporcional de votos e a comparação entre os candidatos foram preservadas com precisão estatística.

## 7. Conclusão e Instruções de Ambiente

A biblioteca `folium` integrada ao `pandas` e `geopandas` mostrou-se extremamente eficiente para a visualização de dados eleitorais. A interatividade dos mapas HTML permite ao usuário explorar os dados de forma muito mais rica do que tabelas estáticas.

Para a correta execução deste projeto, foi criado um ambiente Conda (`environment.yml`) contendo as versões exatas das bibliotecas utilizadas (Python 3.10, Pandas, GeoPandas, Folium), garantindo a reprodutibilidade do código. Todo o projeto, incluindo os scripts, os arquivos HTML gerados e o CSV reduzido, está hospedado em um repositório público no GitHub.
