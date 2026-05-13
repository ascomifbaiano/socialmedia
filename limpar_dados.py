import os
import glob

def cleanup():
    print("--- Iniciando Limpeza de Dados ---")
    
    # Lista todos os arquivos CSV (campi) e o JSON de métricas
    arquivos_csv = glob.glob("*.csv")
    metricas = "metricas.json"
    
    files_to_delete = arquivos_csv + ([metricas] if os.path.exists(metricas) else [])
    
    if not files_to_delete:
        print("Nenhum arquivo de dados encontrado para deletar.")
        return

    for f in files_to_delete:
        try:
            os.remove(f)
            print(f"Removido: {f}")
        except Exception as e:
            print(f"Erro ao remover {f}: {e}")
            
    print(f"\nTotal de {len(files_to_delete)} arquivos removidos.")
    print("O repositório está limpo localmente. Para limpar no GitHub, faça um commit das exclusões.")

if __name__ == "__main__":
    cleanup()
