# Progresso e decisões técnicas

## Decisões da Etapa 1

- **Monorepo simples** com `backend/` e `frontend/` separados, comunicando-se por HTTP.
- **Configuração** via `pydantic-settings`, lida do `.env` na raiz. Campos sensíveis
  (`secret_key`, `llm_api_key`, `youtube_api_key`) são ocultados no `repr`.
- **CORS** restrito às origens listadas em `CORS_ORIGINS`.
- **API** com prefixo `/api`. A factory `create_app()` facilita testes e extensão.
- **Frontend** usa a URL da API via `NEXT_PUBLIC_API_URL` (pública por definição).
- **Camadas do backend** já criadas (`collectors`, `ai`, `repositories` etc.) para manter
  separação de responsabilidades nas próximas etapas.

## Mini feed (antecipação parcial da Etapa 3)

- `GET /api/feed/preview?category=cs.AI&limit=10` coleta artigos **reais** do arXiv.
  `GET /api/feed/categories` lista as áreas permitidas (lista fechada, validada no backend).
- O coletor (`app/collectors/arxiv.py`) separa requisição e parse, e será reutilizado na Etapa 3.
- Cache em memória de 10 min para respeitar o limite de requisições do arXiv.
- Ainda **sem banco, sem deduplicação persistente e sem avaliação de IA**; os cards dizem isso.
- A consulta ao arXiv não pôde ser testada no ambiente de desenvolvimento (rede bloqueada, 403).
  Parser, validação, cache e tratamento de erro estão cobertos por testes; a coleta ao vivo
  precisa ser conferida na máquina do usuário.

## Feed do YouTube

- `GET /api/feed/youtube?topic=ia&limit=10` usa a YouTube Data API v3 oficial (search.list +
  videos.list), com `relevanceLanguage=pt` e `regionCode=BR`. 13 tópicos em português.
- Sem `YOUTUBE_API_KEY`, responde 503 com instrução clara; nunca devolve vídeos inventados.
- A chave nunca aparece em mensagens de erro (testado).
- Transcrições não são coletadas (a API não as fornece automaticamente).
- Não testado contra a API real neste ambiente (sem chave e sem acesso de rede): coberto por testes
  com respostas simuladas apenas do parser e do tratamento de erros.

## Pendências de ambiente

- Servidor PostgreSQL não está instalado no ambiente e o daemon do Docker não está em
  execução. A Etapa 2 vai instalar/iniciar um servidor PostgreSQL local.

## Etapas

- [x] Etapa 1 — Estrutura inicial
- [ ] Etapa 2 — Banco de dados
- [ ] Etapa 3 — Coletores
- [ ] Etapa 4 — Inteligência artificial
- [ ] Etapa 5 — Usuários e personalização
- [ ] Etapa 6 — Interface
- [ ] Etapa 7 — Testes e validação
