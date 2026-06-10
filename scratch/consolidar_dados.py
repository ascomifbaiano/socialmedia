import os
import shutil
import pandas as pd
import sys

# Import the scraper functions to run metric generation
sys.path.append(os.getcwd())
import radar_insta

MAP_CAMPUS = {
    "Alagoinhas": "Alagoinhas",
    "Catu": "Catu",
    "Guanambi": "Guanambi",
    "Itaberaba": "Itaberaba",
    "Itapetinga": "Itapetinga",
    "Lapa": "Bom_Jesus_da_Lapa",
    "Mangabeira": "Governador_Mangabeira",
    "Reitoria": "Reitoria",
    "Santa_Inês": "Santa_Inês",
    "Serrinha": "Serrinha",
    "Teixeira": "Teixeira_de_Freitas",
    "Uruçuca": "Uruçuca",
    "Valença": "Valença",
    "Xique_Xique": "Xique_Xique"
}

def consolidar():
    print("--- Iniciando Consolidação de Dados com Normalização ---")
    os.makedirs("data", exist_ok=True)
    
    consolidated_count = 0
    for f in os.listdir("."):
        if f.endswith(".csv") and not f.startswith("publicacoes"):
            parts = f.split("_")
            if len(parts) >= 2:
                ano_part = parts[-1].replace(".csv", "")
                campus_part = "_".join(parts[:-1])
                
                target_campus = MAP_CAMPUS.get(campus_part)
                if not target_campus:
                    for k, v in MAP_CAMPUS.items():
                        if k.replace("í", "i").replace("ê", "e").replace("á", "a").lower() in campus_part.lower():
                            target_campus = v
                            break
                
                if target_campus:
                    target_dir = os.path.join("data", target_campus)
                    os.makedirs(target_dir, exist_ok=True)
                    target_file = os.path.join(target_dir, f"{target_campus}_{ano_part}.csv")
                    
                    print(f"Processando {f} -> {target_file}")
                    
                    try:
                        df = pd.read_csv(f)
                        
                        # Normalizar o nome do campus na coluna 'campus'
                        df['campus'] = target_campus
                        
                        # Limpar img_url para economia de carregamento
                        df['img_url'] = ""
                        
                        # Garantir que a coluna 'tipo' existe
                        if 'tipo' not in df.columns:
                            df['tipo'] = 'Post'
                        df['tipo'] = df['tipo'].fillna('Post')
                        
                        # Determinar tipo com base no link
                        for idx, row in df.iterrows():
                            link = str(row['link'])
                            if '/reel/' in link or '/reels/' in link:
                                df.at[idx, 'tipo'] = 'Reel'
                            elif '/stories/' in link or '/story/' in link:
                                df.at[idx, 'tipo'] = 'Story'
                            elif row['tipo'] == 'N/A' or pd.isna(row['tipo']):
                                df.at[idx, 'tipo'] = 'Post'
                        
                        # Salvar
                        df.to_csv(target_file, index=False, header=True, encoding='utf-8-sig', quoting=1)
                        consolidated_count += 1
                    except Exception as e:
                        print(f"Erro ao processar {f}: {e}")
                else:
                    print(f"Aviso: Não foi possível mapear o arquivo '{f}' para um campus conhecido.")
                    
    print(f"\n{consolidated_count} arquivos consolidados com sucesso.")
    
    # Gerar as métricas atualizadas
    print("Regerando metricas.json...")
    radar_insta.gerar_metricas()
    print("Consolidação concluída.")

if __name__ == "__main__":
    consolidar()
