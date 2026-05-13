# Radar Instagram DICOM - v8.6 (Debug Edition)
import os
import requests
import pandas as pd
import json
import time
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

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

# DATA DE CORTE DINÂMICA: 7 dias atrás
DIAS_BUSCA = 7
DATA_INICIO_MEMORIAL = datetime.now() - timedelta(days=DIAS_BUSCA)

def parse_relative_date(date_str):
    now = datetime.now()
    if not date_str: return now
    date_str = date_str.lower()
    try:
        if any(x in date_str for x in ['minute', 'hour', 'minuto', 'hora']): return now
        if any(x in date_str for x in ['ago', 'atrás', 'atras']):
            num_match = re.search(r'\d+', date_str)
            if num_match:
                n = int(num_match.group())
                if any(x in date_str for x in ['day', 'dia']): return now - timedelta(days=n)
                elif any(x in date_str for x in ['week', 'semana']): return now - timedelta(weeks=n)
                elif any(x in date_str for x in ['month', 'mês', 'mes']): return now - timedelta(days=n*30)
        
        for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%b %d, %Y', '%d de %b de %Y'):
            try: return datetime.strptime(date_str, fmt)
            except: continue
            
        parsed = pd.to_datetime(date_str, errors='coerce', dayfirst=True)
        return parsed if not pd.isna(parsed) else now
    except: return now

def get_data_serper(username):
    if not API_KEY: 
        print("AVISO: API_SRAPER_KEY não encontrada.")
        return []
    url = "https://google.serper.dev/search"
    
    # Data no formato YYYY-MM-DD para o operador after:
    data_str_google = DATA_INICIO_MEMORIAL.strftime('%Y-%m-%d')
    
    # Realizamos duas buscas por unidade: uma para posts e outra para reels
    # Usando a sintaxe sugerida: site:instagram.com/perfil/p e site:instagram.com/perfil/reel
    queries = [
        f"site:instagram.com/{username}/p/ after:{data_str_google}",
        f"site:instagram.com/{username}/reels/ after:{data_str_google}",
        f"site:instagram.com/{username}/reel/ after:{data_str_google}"
    ]
    
    all_results = []
    headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}
    
    for query in queries:
        print(f"  [Serper] Buscando: {query}")
        payload = json.dumps({"q": query, "num": 20})
        try:
            response = requests.post(url, headers=headers, data=payload, timeout=30)
            results = response.json().get('organic', [])
            all_results.extend(results)
            time.sleep(1) # Delay entre queries do mesmo perfil
        except Exception as e:
            print(f"Erro no Serper query '{query}': {e}")
            
    print(f"  [Serper] {len(all_results)} resultados totais encontrados.")
    return all_results

def get_data_bing(username):
    """Busca no Bing usando sintaxe de precisão"""
    # Data para o Bing (formato aproximado no snippet ou query se suportado)
    queries = [
        f"site:instagram.com/{username}/p/",
        f"site:instagram.com/{username}/reels/"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    
    all_results = []
    for query in queries:
        print(f"  [Bing] Buscando: {query}")
        url = f"https://www.bing.com/search?q={query.replace(' ', '+')}"
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code != 200: continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            for item in soup.select('.b_algo'):
                link_tag = item.select_one('h2 a')
                if not link_tag: continue
                link = link_tag.get('href', '')
                
                if 'instagram.com' in link and any(x in link for x in ['/p/', '/reels/', '/reel/']):
                    snippet_tag = item.select_one('.b_caption p') or item.select_one('.st')
                    snippet = snippet_tag.get_text() if snippet_tag else ""
                    
                    all_results.append({
                        'link': link,
                        'snippet': snippet,
                        'date': ""
                    })
            time.sleep(1)
        except Exception as e:
            print(f"Erro no Bing query '{query}': {e}")
            
    print(f"  [Bing] {len(all_results)} resultados encontrados.")
    return all_results

def garantir_arquivo_existente(campus, user):
    ano = datetime.now().year
    campus_limpo = campus.replace(' ', '_').replace('-', '_')
    diretorio = os.path.join("data", campus_limpo)
    os.makedirs(diretorio, exist_ok=True)
    
    nome_arq = os.path.join(diretorio, f"{campus_limpo}_{ano}.csv")
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
    if not link: return False
    
    shortcode = None
    try:
        if '/p/' in link: shortcode = link.split('/p/')[1].split('/')[0]
        elif '/reels/' in link: shortcode = link.split('/reels/')[1].split('/')[0]
        elif '/reel/' in link: shortcode = link.split('/reel/')[1].split('/')[0]
        else: return False
    except: return False

    if not shortcode or shortcode in existentes: 
        return False

    date_str = item.get('date', '')
    dt_objeto = parse_relative_date(date_str)
    
    # Se não houver data, assumimos que é novo (hoje) para garantir a captura
    if not date_str:
        dt_objeto = datetime.now()

    if dt_objeto < DATA_INICIO_MEMORIAL:
        return False

    campus_limpo = campus.replace(' ', '_').replace('-', '_')
    diretorio = os.path.join("data", campus_limpo)
    os.makedirs(diretorio, exist_ok=True)
    
    nome_arq = os.path.join(diretorio, f"{campus_limpo}_{dt_objeto.year}.csv")
    
    registro = {
        "campus": campus, "unidade": user, "shortcode": shortcode,
        "data": dt_objeto.strftime('%d/%m/%Y %H:%M'),
        "legenda": f'"{item.get("snippet", "").replace(chr(10), " ").replace(chr(34), chr(39))}"',
        "link": link, "img_url": "https://placehold.co/400x300/27ae60/white?text=Instagram+Post",
        "dia_semana": dt_objeto.weekday(), "mes": dt_objeto.month
    }
    
    if os.path.exists(nome_arq):
        df_atual = pd.read_csv(nome_arq)
        if not df_atual.empty and str(df_atual.iloc[0]['shortcode']) == "placeholder":
            pd.DataFrame([registro]).to_csv(nome_arq, index=False, header=True, encoding='utf-8-sig', quoting=1)
        else:
            pd.DataFrame([registro]).to_csv(nome_arq, mode='a', index=False, header=False, encoding='utf-8-sig', quoting=1)
    else:
        pd.DataFrame([registro]).to_csv(nome_arq, index=False, header=True, encoding='utf-8-sig', quoting=1)
    
    existentes.add(shortcode)
    return True

def gerar_metricas():
    list_df = []
    if os.path.exists("data"):
        for root, dirs, files in os.walk("data"):
            for f in files:
                if f.endswith('.csv'):
                    try:
                        df_temp = pd.read_csv(os.path.join(root, f))
                        df_temp = df_temp[df_temp['shortcode'].astype(str) != 'placeholder']
                        if not df_temp.empty: list_df.append(df_temp)
                    except: continue
    
    if not list_df:
        print("AVISO: Nenhum dado de postagens encontrado para gerar métricas.")
        return
    
    df = pd.concat(list_df, ignore_index=True)
    df['data_dt'] = pd.to_datetime(df['data'], format='%d/%m/%Y %H:%M', errors='coerce')
    df = df.dropna(subset=['data_dt'])
    df = df.sort_values('data_dt', ascending=False)
    
    hoje = datetime.now()
    trinta_dias_atras = hoje - timedelta(days=30)
    ritmo_df = df[df['data_dt'] >= trinta_dias_atras]
    ritmo = ritmo_df.groupby(ritmo_df['data_dt'].dt.date).size().to_dict()
    ritmo = {str(k): v for k, v in ritmo.items()}
    mensal = df.groupby(df['data_dt'].dt.strftime('%Y-%m')).size().to_dict()

    stats = {
        "atualizado_em": hoje.strftime('%d/%m/%Y %H:%M'),
        "total_posts": len(df),
        "total_mes_atual": len(df[df['data_dt'].dt.month == hoje.month]),
        "ranking": df['campus'].value_counts().to_dict(),
        "ritmo_publicacao": ritmo,
        "mensal": mensal,
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
            stats['inatividade'][campus] = int((hoje - posts_campus['data_dt'].max()).days)
        else: stats['inatividade'][campus] = 999
        
    with open('metricas.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)
    print("Métricas geradas com sucesso.")

def executar():
    print(f"--- Radar DICOM v8.6 (Debug Mode) ---")
    print(f"Buscando posts de {DATA_INICIO_MEMORIAL.strftime('%d/%m/%Y')} em diante...")
    
    existentes = set()
    if os.path.exists("data"):
        for root, dirs, files in os.walk("data"):
            for f in files:
                if f.endswith('.csv'):
                    try: 
                        df_ex = pd.read_csv(os.path.join(root, f))
                        existentes.update(df_ex['shortcode'].astype(str).tolist())
                    except: continue
    
    print(f"Total de posts já conhecidos: {len(existentes)}")

    for campus, user in PERFIS.items():
        print(f"\nVerificando @{user} ({campus})...")
        res_google = get_data_serper(user)
        res_bing = get_data_bing(user)
        
        resultados = res_google + res_bing
        novos = 0
        for item in resultados:
            if salvar_post(item, campus, user, existentes):
                novos += 1
        
        garantir_arquivo_existente(campus, user)
        print(f"  -> {novos} novos posts únicos salvos.")
        time.sleep(2)

    gerar_metricas()

if __name__ == "__main__":
    executar()
