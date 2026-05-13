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
        print("AVISO: API_SERPER_KEY não encontrada.")
        return []
    url = "https://google.serper.dev/search"
    
    # Filtro de tempo do Google: qdr:y (último ano) ou qdr:m (último mês)
    time_filter = "qdr:y" if DIAS_BUSCA > 31 else "qdr:m"
    
    # Query básica e estável
    query = f'site:instagram.com "{username}"'
    print(f"  [Serper] {query} ({time_filter})...")
    
    all_results = []
    headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}
    
    # Tentamos apenas 2 páginas para não "cansar" o buscador e evitar bloqueios
    for page in [1, 2]:
        payload = json.dumps({
            "q": query, 
            "num": 40, 
            "page": page,
            "tbs": time_filter
        })
        try:
            response = requests.post(url, headers=headers, data=payload, timeout=30)
            data = response.json()
            results = data.get('organic', [])
            if not results: break
            
            all_results.extend(results)
            if len(results) < 10: break
            time.sleep(1)
        except Exception as e:
            print(f"  [Serper] Erro: {e}")
            break
            
    print(f"  [Serper] {len(all_results)} resultados encontrados.")
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

        # 1. Busca Orgânica (Google)
        res_google = get_data_serper(user)
        # 2. Busca de Imagens (Mais rápido para indexar)
        res_images = get_data_serper_images(user)
        # 3. Busca no Bing
        res_bing = get_data_bing(user)
        # 4. Acesso Direto (Real-time)
        res_direct = get_data_direct_guest(user)

        resultados = res_google + res_images + res_bing + res_direct
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
