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
API_KEY = os.environ.get("API_SERPER_KEY")
SESSION_ID = os.environ.get("INSTAGRAM_SESSION_ID")

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

# DATA DE CORTE DINÂMICA
def calcular_data_inicio():
    # Se a pasta data não existe ou está vazia, é a primeira execução (1 ano)
    primeira_vez = True
    if os.path.exists("data"):
        for root, dirs, files in os.walk("data"):
            if any(f.endswith('.csv') for f in files):
                primeira_vez = False
                break
    
    if primeira_vez:
        print("!!! Primeira execução detectada: Buscando histórico de 1 ano !!!")
        return datetime.now() - timedelta(days=365), 365
    else:
        print("--- Atualização diária: Buscando posts dos últimos 30 dias ---")
        return datetime.now() - timedelta(days=30), 30

DATA_INICIO_MEMORIAL, DIAS_BUSCA = calcular_data_inicio()

def parse_relative_date(date_str):
    now = datetime.now()
    if not date_str: return now
    date_str = date_str.lower()
    
    # Traduzir meses de português para inglês para aumentar compatibilidade
    meses_pt = {
        'janeiro': 'january', 'fevereiro': 'february', 'março': 'march',
        'abril': 'april', 'maio': 'may', 'junho': 'june',
        'julho': 'july', 'agosto': 'august', 'setembro': 'september',
        'outubro': 'october', 'novembro': 'november', 'dezembro': 'december',
        'ago': 'aug', 'set': 'sep', 'dez': 'dec'
    }
    for pt, en in meses_pt.items():
        date_str = date_str.replace(pt, en)
        
    try:
        if any(x in date_str for x in ['minute', 'minuto']): return now
        if any(x in date_str for x in ['ago', 'atrás', 'atras', 'há', 'ha']) or re.search(r'\d+\s*[dhmws]', date_str):
            num_match = re.search(r'\d+', date_str)
            if num_match:
                n = int(num_match.group())
                if any(x in date_str for x in ['day', 'dia', 'd']) and not any(x in date_str for x in ['dez', 'dec', 'december', 'dezembro']):
                    if 'dia' in date_str or 'day' in date_str or re.search(r'\b\d+d\b', date_str) or 'há' in date_str or 'ago' in date_str:
                        return now - timedelta(days=n)
                elif any(x in date_str for x in ['week', 'semana', 'w']):
                    return now - timedelta(weeks=n)
                elif any(x in date_str for x in ['month', 'mês', 'mes']):
                    return now - timedelta(days=n*30)
                elif any(x in date_str for x in ['hour', 'hora', 'h']):
                    return now - timedelta(hours=n)
        
        # Limpar conectores comuns em português
        date_str = date_str.replace(' de ', ' ')
        
        for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%b %d, %Y', '%B %d, %Y', '%d %b %Y', '%d %B %Y', '%d de %b de %Y'):
            try: return datetime.strptime(date_str.strip(), fmt)
            except: continue
            
        parsed = pd.to_datetime(date_str, errors='coerce', dayfirst=True)
        return parsed if not pd.isna(parsed) else now
    except: return now

def get_data_serper(username):
    if not API_KEY: 
        print("AVISO: API_SERPER_KEY não encontrada.")
        return []
    url = "https://google.serper.dev/search"
    
    # Em vez de site:, vamos buscar pelo nome da unidade + instagram
    # Isso é muito mais "natural" para o Google e traz mais resultados
    query = f"Instagram {username} IF Baiano"
    print(f"  [Serper] Pesquisando: {query}")
    
    all_results = []
    headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}
    
    for page in [1, 2, 3]:
        payload = json.dumps({
            "q": query, 
            "num": 40, 
            "page": page
        })
        try:
            response = requests.post(url, headers=headers, data=payload, timeout=30)
            data = response.json()
            organic = data.get('organic', [])
            if not organic: break
            
            # Filtramos manualmente apenas o que for link de post ou reel
            for item in organic:
                link = item.get('link', '')
                if 'instagram.com' in link and any(x in link for x in ['/p/', '/reels/', '/reel/']):
                    all_results.append(item)
            
            if len(organic) < 10: break
            time.sleep(1)
        except Exception as e:
            print(f"  [Serper] Erro: {e}")
            break
            
    print(f"  [Serper] {len(all_results)} posts filtrados de {username}.")
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
            "img_url": "",
            "dia_semana": datetime.now().weekday(), "mes": datetime.now().month,
            "tipo": "N/A"
        }
        pd.DataFrame([registro]).to_csv(nome_arq, index=False, header=True, encoding='utf-8-sig', quoting=1)

def get_data_authenticated(username):
    """Obtém dados usando a API oficial do Instagram Web com o sessionid do usuário"""
    if not SESSION_ID:
        print("  [Auth] INSTAGRAM_SESSION_ID não configurado. Pulando método autenticado.")
        return []
        
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "X-IG-App-ID": "936619743392459",
        "Referer": f"https://www.instagram.com/{username}/",
        "X-Requested-With": "XMLHttpRequest",
        "Cookie": f"sessionid={SESSION_ID}"
    }
    
    print(f"  [Auth] Carregando perfil @{username} via API autenticada...")
    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"  [Auth] Erro ao carregar perfil: Código {response.status_code}")
            return []
            
        data = response.json()
        user_data = data.get('data', {}).get('user', {})
        if not user_data:
            print("  [Auth] Dados do usuário não encontrados no JSON.")
            return []
            
        edges = user_data.get('edge_owner_to_timeline_media', {}).get('edges', [])
        results = []
        for edge in edges:
            node = edge.get('node', {})
            shortcode = node.get('shortcode', '')
            if not shortcode: continue
            
            caption_edges = node.get('edge_media_to_caption', {}).get('edges', [])
            caption = caption_edges[0].get('node', {}).get('text', '') if caption_edges else ""
            
            is_video = node.get('is_video', False)
            tipo = "Reel" if is_video else "Post"
            
            timestamp = node.get('taken_at_timestamp', 0)
            dt = datetime.fromtimestamp(timestamp)
            date_str = dt.strftime('%Y-%m-%d %H:%M')
            
            link = f"https://www.instagram.com/p/{shortcode}/"
            img_url = node.get('display_url', '')
            
            results.append({
                'link': link,
                'snippet': caption,
                'date': date_str,
                'tipo': tipo,
                'shortcode': shortcode,
                'img_url': img_url
            })
            
        print(f"  [Auth] {len(results)} posts coletados via API oficial.")
        return results
    except Exception as e:
        print(f"  [Auth] Erro inesperado: {e}")
        return []

def salvar_post(item, campus, user, existentes):
    link = item.get('link', '')
    if not link: return False
    
    shortcode = item.get('shortcode')
    tipo = item.get('tipo', 'Post')
    
    if not shortcode:
        try:
            if '/p/' in link: 
                shortcode = link.split('/p/')[1].split('/')[0]
                tipo = "Post"
            elif '/reels/' in link: 
                shortcode = link.split('/reels/')[1].split('/')[0]
                tipo = "Reel"
            elif '/reel/' in link: 
                shortcode = link.split('/reel/')[1].split('/')[0]
                tipo = "Reel"
            elif '/stories/' in link or '/story/' in link:
                parts = link.split('/stories/')[1].split('/')
                shortcode = parts[1] if parts[0] == 'highlights' else parts[0]
                tipo = "Story"
            else: 
                return False
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
    
    img_url = ""
    
    registro = {
        "campus": campus, "unidade": user, "shortcode": shortcode,
        "data": dt_objeto.strftime('%d/%m/%Y %H:%M'),
        "legenda": f'"{item.get("snippet", "").replace(chr(10), " ").replace(chr(34), chr(39))}"',
        "link": link, "img_url": img_url,
        "dia_semana": dt_objeto.weekday(), "mes": dt_objeto.month,
        "tipo": tipo
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
        print("Aviso: Nenhum dado de postagens encontrado. Gerando métricas vazias padrão.")
        hoje = datetime.now()
        publicacoes_recentes = {}
        ranking_detalhado = {}
        for campus in PERFIS.keys():
            publicacoes_recentes[campus] = {
                "hoje": {"Post": 0, "Reel": 0, "Story": 0, "links": []},
                "ontem": {"Post": 0, "Reel": 0, "Story": 0, "links": []}
            }
            ranking_detalhado[campus] = {"Post": 0, "Reel": 0, "Story": 0}
            
        stats = {
            "atualizado_em": hoje.strftime('%d/%m/%Y %H:%M'),
            "total_posts": 0,
            "total_mes_atual": 0,
            "ranking": {campus: 0 for campus in PERFIS.keys()},
            "ranking_detalhado": ranking_detalhado,
            "publicacoes_recentes": publicacoes_recentes,
            "tipo_geral": {"Post": 0, "Reel": 0, "Story": 0},
            "ritmo_publicacao": {},
            "mensal": {},
            "dias_produtivos": {},
            "inatividade": {campus: 999 for campus in PERFIS.keys()},
            "dia_mais_produtivo": "N/A"
        }
        with open('metricas.json', 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=4)
        return
    
    df = pd.concat(list_df, ignore_index=True)
    if 'tipo' not in df.columns:
        df['tipo'] = 'Post'
    df['tipo'] = df['tipo'].fillna('Post')
    
    df['data_dt'] = pd.to_datetime(df['data'], format='%d/%m/%Y %H:%M', errors='coerce')
    df = df.dropna(subset=['data_dt'])
    df = df.sort_values('data_dt', ascending=False)
    
    hoje = datetime.now()
    trinta_dias_atras = hoje - timedelta(days=30)
    ritmo_df = df[df['data_dt'] >= trinta_dias_atras]
    ritmo = ritmo_df.groupby(ritmo_df['data_dt'].dt.date).size().to_dict()
    ritmo = {str(k): v for k, v in ritmo.items()}
    mensal = df.groupby(df['data_dt'].dt.strftime('%Y-%m')).size().to_dict()

    # Ranking geral e ranking por tipo
    tipo_geral = df['tipo'].value_counts().to_dict()
    
    # Detalhamento por campus
    ranking_detalhado = {}
    for campus in PERFIS.keys():
        posts_campus = df[df['campus'] == campus]
        counts = posts_campus['tipo'].value_counts().to_dict()
        ranking_detalhado[campus] = {
            "Post": int(counts.get("Post", 0)),
            "Reel": int(counts.get("Reel", 0)),
            "Story": int(counts.get("Story", 0))
        }
        
    # Publicações Recentes (Ontem e Hoje)
    hoje_date = hoje.date()
    ontem_date = (hoje - timedelta(days=1)).date()
    
    publicacoes_recentes = {}
    for campus in PERFIS.keys():
        publicacoes_recentes[campus] = {
            "hoje": {"Post": 0, "Reel": 0, "Story": 0, "links": []},
            "ontem": {"Post": 0, "Reel": 0, "Story": 0, "links": []}
        }
        
    df['data_date'] = df['data_dt'].dt.date
    df_recentes = df[df['data_date'].isin([hoje_date, ontem_date])]
    
    for idx, row in df_recentes.iterrows():
        campus = row['campus']
        tipo = row['tipo']
        date_only = row['data_date']
        link = row['link']
        
        periodo = "hoje" if date_only == hoje_date else "ontem"
        
        if campus in publicacoes_recentes:
            if tipo in publicacoes_recentes[campus][periodo]:
                publicacoes_recentes[campus][periodo][tipo] += 1
            publicacoes_recentes[campus][periodo]["links"].append({
                "link": link,
                "tipo": tipo,
                "data": row['data']
            })

    stats = {
        "atualizado_em": hoje.strftime('%d/%m/%Y %H:%M'),
        "total_posts": len(df),
        "total_mes_atual": len(df[df['data_dt'].dt.month == hoje.month]),
        "ranking": df['campus'].value_counts().to_dict(),
        "ranking_detalhado": ranking_detalhado,
        "publicacoes_recentes": publicacoes_recentes,
        "tipo_geral": tipo_geral,
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

def get_data_serper_images(username):
    """Busca no Serper Images, que costuma indexar fotos mais rápido que o Web Search"""
    if not API_KEY: return []
    url = "https://google.serper.dev/images"
    query = f"site:instagram.com \"{username}\""
    print(f"  [Serper Images] Buscando: {query}")
    payload = json.dumps({"q": query, "num": 30})
    headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        results = response.json().get('images', [])
        formatted = []
        for img in results:
            link = img.get('link', '') # Link da página onde a imagem está
            if 'instagram.com' in link and any(x in link for x in ['/p/', '/reels/', '/reel/']):
                formatted.append({
                    'link': link,
                    'snippet': img.get('title', ''),
                    'date': "" # Imagens raramente têm data
                })
        print(f"  [Serper Images] {len(formatted)} posts encontrados via imagens.")
        return formatted
    except: return []

def get_data_direct_guest(username):
    """Tenta ler o perfil diretamente via 'Guest Browsing' (HTML público)"""
    url = f"https://www.instagram.com/{username}/"
    print(f"  [Direct] Acessando perfil: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200: return []

        # O Instagram carrega os posts via JS, mas os últimos posts costumam 
        # estar em meta tags ou em scripts de JSON (LD-JSON)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []

        # Tenta achar links de posts no HTML
        links = re.findall(r'/(?:p|reels|reel)/([A-Za-z0-9_-]+)/', response.text)
        for code in set(links):
            results.append({
                'link': f"https://www.instagram.com/p/{code}/",
                'snippet': f"Post de @{username} (detectado via acesso direto)",
                'date': datetime.now().strftime('%Y-%m-%d')
            })
        print(f"  [Direct] {len(results)} links detectados no perfil.")
        return results
    except: return []

def executar():
    print(f"--- Radar DICOM v8.8 (Modo Real-Time) ---")
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

        # 0. Busca Autenticada (API Oficial via sessionid, 100% garantido)
        res_auth = get_data_authenticated(user)
        # 1. Busca Orgânica (Google)
        res_google = get_data_serper(user)
        # 2. Busca no Bing
        res_bing = get_data_bing(user)
        # 3. Acesso Direto (Real-time)
        res_direct = get_data_direct_guest(user)

        resultados = res_auth + res_google + res_bing + res_direct
        novos = 0
        for item in resultados:
            if salvar_post(item, campus, user, existentes):
                novos += 1

        garantir_arquivo_existente(campus, user)
        print(f"  -> {novos} novos posts únicos salvos.")
        time.sleep(3) # Pausa estratégica

    gerar_metricas()


if __name__ == "__main__":
    executar()
