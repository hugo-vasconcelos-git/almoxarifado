"""
deploy.py — Envia o index.html para o GitHub e aciona o deploy no Railway.

Como usar:
  1. Gere um token em: https://github.com/settings/tokens/new
     Marque apenas: repo (acesso completo ao repositório)
  2. Cole o token na variável GITHUB_TOKEN abaixo
  3. Execute: python deploy.py
"""

import urllib.request
import urllib.error
import json
import base64
import os

# ─── CONFIGURAÇÃO ────────────────────────────────────────────────────────────
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")   # Lê do env, ou coloque aqui
REPO_OWNER   = "hugo-vasconcelos-git"
REPO_NAME    = "almoxarifado"
ARQUIVO      = "index.html"            # arquivo a enviar
# ─────────────────────────────────────────────────────────────────────────────


def cabecalhos():
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "almoxarifado-deploy/1.0",
    }


def buscar_sha():
    """Busca o SHA atual do arquivo no GitHub (necessário para atualizar)."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{ARQUIVO}"
    req = urllib.request.Request(url, headers=cabecalhos())
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            return data["sha"]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None  # arquivo ainda não existe no repo
        raise


def enviar_arquivo(sha):
    """Envia o arquivo local para o GitHub."""
    caminho = os.path.join(os.path.dirname(__file__), ARQUIVO)

    if not os.path.exists(caminho):
        print(f"❌ Arquivo não encontrado: {caminho}")
        return False

    with open(caminho, "rb") as f:
        conteudo = base64.b64encode(f.read()).decode()

    payload = {
        "message": f"deploy: atualiza {ARQUIVO}",
        "content": conteudo,
    }
    if sha:
        payload["sha"] = sha  # obrigatório ao atualizar arquivo existente

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{ARQUIVO}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=cabecalhos(), method="PUT")

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            commit = result["commit"]["sha"][:7]
            print(f"✅ GitHub atualizado — commit {commit}")
            print(f"🚀 Railway iniciando deploy automático...")
            print(f"🌐 App: https://almoxarifado-production-10bc.up.railway.app")
            return True
    except urllib.error.HTTPError as e:
        corpo = e.read().decode()
        print(f"❌ Erro {e.code}: {corpo}")
        return False


DEPLOY_YML = """\
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Railway CLI
        run: npm install -g @railway/cli
      - name: Deploy to Railway
        run: railway up --service almoxarifado
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
"""


def buscar_sha_path(path):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}"
    req = urllib.request.Request(url, headers=cabecalhos())
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())["sha"]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def enviar_conteudo(path, conteudo_bytes, mensagem):
    sha = buscar_sha_path(path)
    payload = {
        "message": mensagem,
        "content": base64.b64encode(conteudo_bytes).decode(),
    }
    if sha:
        payload["sha"] = sha
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}"
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=cabecalhos(), method="PUT")
    try:
        with urllib.request.urlopen(req) as resp:
            commit = json.loads(resp.read())["commit"]["sha"][:7]
            print(f"  ✅ {path} — commit {commit}")
            return True
    except urllib.error.HTTPError as e:
        print(f"  ❌ {path} — erro {e.code}: {e.read().decode()}")
        return False


def main():
    if GITHUB_TOKEN == "ghp_SEU_TOKEN_AQUI":
        print("⚠️  Configure o GITHUB_TOKEN no deploy.py antes de usar.")
        return

    print("📦 Enviando arquivos para GitHub...")

    # 1. index.html
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), ARQUIVO)
    if os.path.exists(caminho):
        with open(caminho, "rb") as f:
            enviar_conteudo(ARQUIVO, f.read(), f"deploy: atualiza {ARQUIVO}")
    else:
        print(f"  ❌ {ARQUIVO} não encontrado")

    # 2. deploy.yml corrigido
    enviar_conteudo(
        ".github/workflows/deploy.yml",
        DEPLOY_YML.encode(),
        "fix: corrige deploy.yml Railway CLI"
    )

    print(f"🚀 Railway iniciando deploy automático...")
    print(f"🌐 https://almoxarifado-production-10bc.up.railway.app")


if __name__ == "__main__":
    main()
