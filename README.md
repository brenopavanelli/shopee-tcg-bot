# shopee-tcg-bot

Bot que monitora ofertas de **TCG** (trading card games) na Shopee e publica as
melhores oportunidades no Telegram. Focado em Pokémon TCG por padrão, mas com
catalogos de keywords curados para outros jogos (ver [Niches](#niches)).

O bot roda em duas etapas:

1. **Coletor** — busca ofertas na Shopee por keyword, filtra pelas notas/vendas
   mínimas configuradas, remove duplicatas e enfileira as que passaram.
2. **Publicador** — tira o item mais antigo da fila e o envia ao Telegram (com
   foto + caption). Se a fila estiver vazia, coleta na hora.

## Como funciona

```
Shopee GraphQL → coletor → fila.json → publicador → Telegram
```

- **Dedup por título**: títulos são normalizados (minúsculo, sem acento/emoji),
  e ofertas duplicadas já publicadas nos últimos `TITLE_DEDUP_DAYS` dias são
  ignoradas.
- **Fila com validade**: itens expiram após `QUEUE_MAX_AGE_HOURS` (padrão 6h) —
  uma oferta velha nunca é publicada como se fosse nova.
- **Rotação de keywords**: as keywords são embaralhadas e percorridas de forma
  que todas aparecem antes de qualquer uma repetir (`next_keyword`).
- **Dry-run**: tanto a Shopee quanto o Telegram têm modo simulado, ideal para
  testes e integração contínua.

## Instalação

Requer **Python 3.10+**.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .          # runtime
pip install -e ".[dev]"   # + pytest/ruff (desenvolvimento)
```

Copie `.env.example` para `.env` e preencha as credenciais:

```bash
cp .env.example .env
```

## Configuração

| Variável | Padrão | Descrição |
|---|---|---|
| `SHOPEE_APP_ID` / `SHOPEE_APP_SECRET` | — | Credenciais da Open API da Shopee |
| `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` | — | Bot e chat do Telegram |
| `SHOPEE_DRY_RUN` | `true` | `false` consulta a Shopee de verdade |
| `TELEGRAM_DRY_RUN` | `true` | `false` envia ao Telegram de verdade |
| `SHOPEE_NICHE` | `pokemon` | Nome do nicho (ver [Niches](#niches)) |
| `KEYWORDS` | — | Lista de keywords (vence `SHOPEE_NICHE`) |
| `MIN_RATING_IDEAL` / `MIN_RATING_FALLBACK` | `4.8` / `4.7` | Nota mínima para os tiers |
| `MIN_SALES_IDEAL` / `MIN_SALES_FALLBACK` | `20` / `10` | Vendas mínimas para os tiers |
| `QUEUE_MAX_AGE_HOURS` | `6` | Validade dos itens na fila |
| `TITLE_DEDUP_DAYS` | `3` | Janela de dedup por título |
| `MAX_SEARCH_ATTEMPTS` | `3` | Keywords coletadas por rodada |

## Uso

```bash
# Coletar ofertas e encher a fila
tcgbot-collect          # ou: python -m tcgbot.collector
python -m tcgbot.collector   # equivalente

# Publicar a próxima oferta da fila no Telegram
tcgbot-publish
python -m tcgbot.publisher

# Verificação manual da Shopee com uma keyword arbitrária
python scripts/validate_shopee.py "Pokemon TCG"
```

Por padrão tudo roda em **dry-run** — seta `SHOPEE_DRY_RUN=false` e
`TELEGRAM_DRY_RUN=false` no `.env` para operar de verdade.

## Niches

O catálogo de keywords é separado por jogo em `src/tcgbot/niches/`. Selecione um
nicho com `SHOPEE_NICHE`:

| Niche | `SHOPEE_NICHE` |
|---|---|
| Pokemon TCG (padrão) | `pokemon` |
| Yu-Gi-Oh! | `yugioh` |
| One Piece TCG | `one-piece` |

Uma variável `KEYWORDS` explícita sempre sobrescreve o nicho. Para adicionar um
novo jogo, basta registrar um `Niche` novo em `niches/__init__.py`.

## Filtros

Uma oferta entra na fila se atende ao **tier ideal**:

- tem avaliação (`ratingStar`) `>= MIN_RATING_IDEAL`
- `sales >= MIN_SALES_IDEAL`
- é de loja oficial/preferencial (`shopType` em `1|2|4`)

Ou ao **tier fallback** (sem exigência de loja oficial):

- `ratingStar >= MIN_RATING_FALLBACK` e `sales >= MIN_SALES_FALLBACK`

Ofertas sem avaliação são sempre rejeitadas. A razão da rejeição fica no
`FilterResult.reason`.

## Testes

```bash
pip install -e ".[dev]"
pytest -v
```

Os testes são **offline** (dry-run contra fixtures locais), sem chamar a Shopee
nem o Telegram.

## Estrutura

```
src/tcgbot/
├── collector.py       # busca, filtra e enfileira ofertas
├── publisher.py       # publica a próxima oferta da fila no Telegram
├── config.py          # configuração via variáveis de ambiente
├── models.py          # dataclass Offer
├── filters.py         # tiers ideal/fallback
├── dedup.py           # normalização de título + checagem de duplicata
├── keywords.py        # rotação de keywords com estado persistido
├── queue_store.py     # fila de ofertas com validade
├── storage.py         # histórico de publicações com janela de dias
├── message.py         # montagem da mensagem do Telegram
├── telegram_client.py # envio ao Telegram
├── shopee_client.py   # consulta à Shopee (GraphQL) + assinatura
└── niches/            # catálogo de keywords por jogo
```