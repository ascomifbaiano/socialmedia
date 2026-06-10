import os
import shutil

def cleanup():
    print("--- Iniciando Limpeza de Dados ---")
    
    # Pasta principal de dados e JSON de métricas
    pasta_data = "data"
    metricas = "metricas.json"
    
    removidos = 0
    
    if os.path.exists(pasta_data):
        try:
            shutil.rmtree(pasta_data)
            print(f"Diretório '{pasta_data}/' removido com sucesso.")
            removidos += 1
        except Exception as e:
            print(f"Erro ao remover diretório {pasta_data}: {e}")
            
    if os.path.exists(metricas):
        try:
            os.remove(metricas)
            print(f"Arquivo '{metricas}' removido.")
            removidos += 1
        except Exception as e:
            print(f"Erro ao remover {metricas}: {e}")
            
    if removidos == 0:
        print("Nenhum dado encontrado para limpar.")
    else:
        print(f"\nLimpeza concluída. {removidos} itens principais removidos.")

if __name__ == "__main__":
    cleanup()

if __name__ == "__main__":
    cleanup()
