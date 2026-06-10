# Instruções de Otimização de Prompts para Gemini CLI

Este documento contém diretrizes e templates para refinar prompts, com foco em automação, monitoramento de dados públicos e extração de informações de redes sociais.

## 🛠️ Monitoramento de Diários Oficiais (DOU)

Ao solicitar a criação de ferramentas de monitoramento para o IF Baiano ou outras instituições, utilize uma estrutura que defina o escopo técnico:

**Template Sugerido:**
> "Preciso criar uma automação via **GitHub Actions** que monitore menções ao **[Termo Completo Exato]** no portal do DOU. O script deve ser em Python, realizar o scraping da URL específica `[URL_DA_PESQUISA]` e salvar os novos resultados em um arquivo `[JSON/CSV]` no repositório. Como estruturar o seletor CSS do BeautifulSoup para os resultados dessa página e como configurar o YAML para rodar diariamente às `[HORA]`?"

**Pontos Chave:**
- Especifique a biblioteca (BeautifulSoup/Selenium).
- Defina o método de persistência (Commit no repositório).
- Solicite a configuração do Cron (agendamento).

---

## 📸 Monitoramento de Redes Sociais via Search Engines

Para buscar posts ou reels recentes utilizando operadores de busca (Google/Bing), utilize a sintaxe de precisão:

**Template Sugerido:**
> "Como posso utilizar os **Google Search Operators** para filtrar especificamente por `[reels/posts]` de um perfil do Instagram? Forneça a sintaxe para `site:instagram.com/[perfil]` combinada com o parâmetro `after:YYYY-MM-DD` para retornar apenas conteúdos publicados após `[DATA]`."

**Comandos Úteis para Referência:**
- `site:instagram.com/perfil/reel` (Filtra apenas Reels).
- `site:instagram.com/perfil/p` (Filtra apenas Posts).
- `after:YYYY-MM-DD` (Filtra por data de indexação).

---

## 🧠 Protocolo de Refinamento Contínuo

Sempre que um prompt for enviado, o modelo deve:
1. **Analisar a Intenção:** Identificar se o objetivo é automação, pesquisa ou criação.
2. **Sugerir Parâmetros Técnicos:** Indicar flags, seletores ou bibliotecas que tornem a resposta mais funcional.
3. **Propor Versão Otimizada:** Reescrever o prompt original para ser mais direto e "machine-ready".

---
*Gerado para otimização de fluxos de trabalho no GitHub e pesquisa avançada.*
