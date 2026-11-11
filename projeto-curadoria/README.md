# Plataforma de Curadoria Inteligente de Conhecimento

Mecanismo de descoberta e curadoria que encontra, analisa e classifica conteúdos da internet
por **profundidade, credibilidade e relevância**, e não por popularidade.

> Status: **MVP em desenvolvimento — Etapa 1 (estrutura inicial) concluída.**
> Veja o progresso por etapa em [`docs/PROGRESSO.md`](docs/PROGRESSO.md).

## Stack

| Camada | Tecnologia |
| --- | --- |
| Frontend | Next.js, React, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI |
| Banco de dados | PostgreSQL, SQLAlchemy, Alembic (Etapa 2) |
| IA | Camada independente de provedor de LLM, saídas em JSON validado (Etapa 4) |
| Fontes | YouTube Data API, arXiv, feeds RSS (Etapa 3) |

## Estrutura

```
projeto-curadoria/
├── backend/          # API FastAPI
│   ├── app/
│   │   ├── api/          # rotas
│   │   ├── core/         # configuração
│   │   ├── models/       # modelos SQLAlchemy
│   │   ├── schemas/      # schemas Pydantic
│   │   ├── services/     # regras de negócio
│   │   ├── collectors/   # arXiv, RSS, YouTube
│   │   ├── ai/           # integração com LLM
│   │   └── repositories/ # acesso a dados
│   └── tests/
├── frontend/         # Next.js (src/app, components, services, hooks, types)
├── docs/
├── .env.example
└── README.md
```

## Pré-requisitos

- Python 3.11+ (testado com 3.13)
- Node.js 20+ (testado com 22) e npm
- PostgreSQL 16 (necessário a partir da Etapa 2)

## Como executar

### 1. Variáveis de ambiente

```bash
cp .env.example .env
```

Na Etapa 1 nenhuma chave é obrigatória. As chaves de YouTube e do LLM só serão exigidas nas
Etapas 3 e 4. Chaves ficam **somente** no backend (`.env`), nunca no frontend.

### 2. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- Saúde da API: <http://localhost:8000/api/health>
- Documentação interativa: <http://localhost:8000/docs>
- Mini feed (arXiv): <http://localhost:8000/api/feed/preview?category=cs.AI&limit=3>

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Acesse <http://localhost:3000>. A página inicial mostra se a API está online e um mini feed com
artigos reais do arXiv (ainda sem avaliação de IA).

Se a API não estiver em `http://localhost:8000`, crie `frontend/.env.local` com:

```
NEXT_PUBLIC_API_URL=http://sua-api
```

## Testes

```bash
# Backend
cd backend && source .venv/bin/activate && python -m pytest -v

# Frontend
cd frontend && npm run lint && npm run build
```

## Princípios de desenvolvimento

- Sem dados falsos: se uma fonte ou API não estiver configurada, o sistema informa o que falta.
- Respeito aos termos de uso, limites de requisição e direitos autorais de cada fonte.
- Segredos apenas em variáveis de ambiente.
- Nenhuma etapa é considerada concluída sem testes executados.
