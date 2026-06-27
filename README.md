# Almoxarifado — Inventário por QR Code

App web mobile para inventário de almoxarifado via leitura de QR Code. Desenvolvido para a **Audax LED**, com plano de integração futura ao ERP **Protheus (TOTVS)**.

## Acesso

- **App online:** https://almoxarifado-production-10bc.up.railway.app
- **Repositório GitHub:** https://github.com/hugo-vasconcelos-git/almoxarifado
- **Hospedagem:** Railway (deploy automático ao fazer commit no GitHub)

## Arquivos

| Arquivo | Descrição |
|---|---|
| `index.html` | App completo (frontend mobile, single-file) |
| `server.py` | Servidor Python para Railway (com header Permissions-Policy para câmera iOS) |
| `requirements.txt` | Vazio — usa só stdlib Python |

## Fluxo de uso (3 etapas)

```
1. Seleciona RUA (A–O) + PRATELEIRA (1–54) no seletor visual
2. Bipa etiquetas dos itens com a câmera (formato: SKU|quantidade)
   → mesmo SKU bipado 2x soma automaticamente
3. Fecha o endereço → exporta relatório em texto
```

## Formato das etiquetas Audax

As etiquetas físicas contêm: SKU (ex: `85000166600101`), descrição, quantidade, fornecedor, data e NF.

O QR Code deve retornar:
- `85000166600101|500` — SKU com quantidade (preferido)
- `85000166600101` — só SKU (aceito, quantidade assume 1)

O separador padrão é `|` mas pode ser configurado no código.

## Endereçamento

- **Ruas:** A até O (15 ruas)
- **Prateleiras:** 1 a 54
- Exibição no relatório: `RUA G · PRAT. 12`
- Campo Protheus futuro: `B1_LOCPAD` (tabela SB1)
- Etiquetas físicas de endereço ainda não criadas — por isso usa seletor manual

## Biblioteca de leitura QR

Usa **ZXing** (`@zxing/library@0.19.1`). Substituiu jsQR que não conseguia ler os QR Codes densos das etiquetas Audax. A câmera só funciona via **HTTPS** (por isso Railway, não file://).

## Como atualizar o app

1. Edite `index.html` localmente
2. No GitHub → `index.html` → ✏️ → Ctrl+A → Delete → cole → Commit
3. Railway faz redeploy automático em ~30s

## Futuro — Integração Protheus REST

**Base URL:** `http://servidor:porta/rest`  
**Autenticação:** Basic Auth ou Bearer Token (OAuth2)  
**Header obrigatório:** `x-totvs-filial: 01`

| Operação | Método | Endpoint |
|---|---|---|
| Consultar produto | GET | `/totvsapi/product/v1/products/{sku}` |
| Atualizar localização | PATCH | `/totvsapi/product/v1/products/{sku}` |
| Saldo em estoque | GET | `/totvsapi/stock/v1/stockBalance` |
| Registrar entrada | POST | `/totvsapi/stock/v1/stockMovements` |
| Registrar saída | POST | `/totvsapi/stock/v1/stockMovements` |
| Requisição MATA105 | POST | `/totvsapi/warehouseRequest/v1/requests` |

**Ponto crítico:** configurar TES (Tipo de Entrada/Saída) no SIGAEST antes de usar movimentações via API.

## Histórico de decisões

| Decisão | Motivo |
|---|---|
| App web (não script Python) | Roda no celular sem instalação |
| Railway + GitHub | HTTPS obrigatório para câmera no iOS |
| ZXing substituiu jsQR | jsQR não lia QR Codes densos da Audax |
| Seletor manual de rua/prateleira | Etiquetas físicas de endereço ainda não impressas |
| Exporta texto (offline) | Sem API Protheus conectada ainda — fase futura |

## Histórico de versões

| Data | Versão | Descrição |
|---|---|---|
| 27/06/2026 | v1.0 | App mobile com seletor de rua/prateleira e câmera ZXing |
