# Radar Instagram DICOM - v8.3 (Pente Fino Serper)
import os
import requests
import pandas as pd
import json
import time
import re
from datetime import datetime

# Configurações
API_KEY = os.environ.get("API_SRAPER_KEY")

PERFIS = {
    "Reitoria": "ifbaiano",
    "Alagoinhas": "ifbaiano_alagoinhas",
    "Bom_Jesus_da_Lapa": "ifbaiano_lapa",
    "Catu": "ifbaianocampuscatu",
    "Governador_Mangabeira": "ifbaiano.govmangabeira",
    "Guanambi": "ifbaianoguanambi",
    "Itaberaba": "ifbaiano.itaberaba",
    "Itapetinga": "ifbaiano_itapetinga",
    "Santa_Inês": "ifbaiano.santaines",
    "Senhor_do_Bonfim": "ifbainaobonfimoficial",
    "Serrinha": "ifbaianoserrinha",
    "Teixeira_de_Freitas": "ifbaianoteixeiradefreitas",
    "Uruçuca": "ifbaiano_urucuca",
    "Valença": "ifbaiano_valenca",
    "Xique_Xique": "ifbaiano.xiquexique"
}

# DATA DE CORTE: Ignorar tudo antes de 11/05/2026
DATA_INICIO_MEMORIAL = datetime(2026, 5, 11)

def parse_serper_date(date_str):
    now = datetime.now()
    if not date_str: return now
    date_str = date_str.lower()
    try:
        if 'minute' in date_str or 'hour' in date_str: return now
        if 'ago' in date_str:
            num_match = re.search(r'\d+', date_str)
            if num_match:
                n = int(num_match.group())
                if 'day' in date_str: return now - pd.Timedelta(days=n)
                elif 'week' in date_str: return now - pd.Timedelta(weeks=n)
                elif 'month' in date_str: return now - pd.Timedelta(days=n*30)
        parsed = pd.to_datetime(date_str, errors='coerce', dayfirst=False)
        return parsed if not pd.isna(parsed) else now
    except: return now

def get_data_serper(username):
    if not API_KEY: return []
    url = "https://google.serper.dev/search"
    
    # BUSCA AMPLIADA: Procura o termo e o link direto para ser mais assertivo
    query = f"site:instagram.com \"{username}\""
    
    # Usamos SEMPRE qdr:w (última semana) para compensar o delay do Google.
    # O filtro real de data será feito pelo nosso código Python abaixo.
    payload = json.dumps({"q": query, "num": 40, "tbs": "qdr:w"})
    headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        return response.json().get('organic', [])
    except: return []

def garantir_arquivo_existente(campus, user):
    ano = datetime.now().year
    campus_limpo = campus.replace(' ', '_').replace('-', '_')
    nome_arq = f"{campus_limpo}_{ano}.csv"
    if not os.path.exists(nome_arq):
        registro = {
            "campus": campus, "unidade": user, "shortcode": "placeholder",
            "data": datetime.now().strftime('%d/%m/%Y %H:%M'),
            "legenda": "Aguardando novas publicações", "link": "#", 
            "img_url": "https://placehold.co/400x300/27ae60/white?text=Aguardando+Posts",
            "dia_semana": datetime.now().weekday(), "mes": datetime.now().month
        }
        pd.DataFrame([registro]).to_csv(nome_arq, index=False, header=True, encoding='utf-8-sig', quoting=1)

def salvar_post(item, campus, user, existentes):
    link = item.get('link', '')
    shortcode = None
    try:
        if '/p/' in link: shortcode = link.split('/p/')[1].split('/')[0]
        elif '/reels/' in link: shortcode = link.split('/reels/')[1].split('/')[0]
        elif '/reel/' in link: shortcode = link.split('/reel/')[1].split('/')[0]
        else: return False
    except: return False

    if not shortcode or shortcode in existentes: return False

    dt_objeto = parse_serper_date(item.get('date', ''))
    
    # FILTRO DE DATA (O coração do memorial)
    if dt_objeto < DATA_INICIO_MEMORIAL:
        return False

    ano = dt_objeto.year
    campus_limpo = campus.replace(' ', '_').replace('-', '_')
    nome_arq = f"{campus_limpo}_{ano}.csv"
    
    registro = {
        "campus": campus, "unidade": user, "shortcode": shortcode,
        "data": dt_objeto.strftime('%d/%m/%Y %H:%M'),
        "legenda": f'"{item.get("snippet", "").replace(chr(10), " ").replace(chr(34), chr(39))}"',
        "link": link, "img_url": "https://placehold.co/400x300/27ae60/white?text=Instagram+Post",
        "dia_semana": dt_objeto.weekday(), "mes": dt_objeto.month
    }
    
    if os.path.exists(nome_arq):
        df_atual = pd.read_csv(nome_arq)
        if not df_atual.empty and df_atual.iloc[0]['shortcode'] == "placeholder":
            pd.DataFrame([registro]).to_csv(nome_arq, index=False, header=True, encoding='utf-8-sig', quoting=1)
        else:
            pd.DataFrame([registro]).to_csv(nome_arq, mode='a', index=False, header=False, encoding='utf-8-sig', quoting=1)
    else:
        pd.DataFrame([registro]).to_csv(nome_arq, index=False, header=True, encoding='utf-8-sig', quoting=1)
    return True

def gerar_metricas():
    arquivos = [f for f in os.listdir() if '.csv' in f and '_' in f]
    if not arquivos: return
    list_df = []
    for f in arquivos:
        try:
            df_temp = pd.read_csv(f)
            df_temp = df_temp[df_temp['shortcode'] != 'placeholder']
            if not df_temp.empty: list_df.append(df_temp)
        except: continue
    if not list_df: return
    df = pd.concat(list_df, ignore_index=True)
    df['data_dt'] = pd.to_datetime(df['data'], format='%d/%m/%Y %H:%M', errors='coerce')
    df = df.dropna(subset=['data_dt'])
    stats = {
        "atualizado_em": datetime.now().strftime('%d/%m/%Y %H:%M'),
        "total_posts": len(df),
        "ranking": df['campus'].value_counts().to_dict(),
        "dias_produtivos": df['dia_semana'].value_counts().to_dict() if 'dia_semana' in df.columns else {},
        "inatividade": {}
    }
    DIAS_NOMES = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    if not df.empty: 
        try: stats["dia_mais_produtivo"] = DIAS_NOMES[int(df['dia_semana'].value_counts().idxmax())]
        except: stats["dia_mais_produtivo"] = "N/A"
    for campus in PERFIS.keys():
        posts_campus = df[df['campus'] == campus]
        if not posts_campus.empty:
            stats['inatividade'][campus] = int((datetime.now() - posts_campus['data_dt'].max()).days)
        else: stats['inatividade'][campus] = 999
    with open('metricas.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)

def executar():
    print(f"--- Radar DICOM v8.3 (Pente Fino) ---")
    print(f"Buscando posts de {DATA_INICIO_MEMORIAL.strftime('%d/%m/%Y')} em diante...")
    
    existentes = set()
    for f in os.listdir():
        if f.endswith('.csv') and '_' in f:
            try: existentes.update(pd.read_csv(f)['shortcode'].astype(str).tolist())
            except: continue
    
    for campus, user in PERFIS.items():
        print(f"Verificando @{user}...")
        resultados = get_data_serper(user)
        novos = 0
        for item in resultados:
            if salvar_post(item, campus, user, existentes):
                novos += 1
                existentes.add(item.get('link','')) 
        garantir_arquivo_existente(campus, user)
        print(f"  -> {novos} posts encontrados.")
        time.sleep(1) 

    gerar_metricas()

if __name__ == "__main__":
    executar()
