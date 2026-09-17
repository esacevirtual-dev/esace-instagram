#!/usr/bin/env python3
"""
Publica no Instagram (@esacevirtual) os posts da fila.json cuja data/hora já chegou.

Uso:
  python3 publicar.py                 # publica tudo que estiver vencido e pendente
  python3 publicar.py --post 03       # força um post específico (ignora a data)
  python3 publicar.py --dry-run       # só mostra o que faria
  python3 publicar.py --check-token   # testa o token e mostra a conta

Variáveis de ambiente (ou arquivo .env na mesma pasta):
  IG_TOKEN     token de acesso (Instagram Login, longa duração)
  IG_USER_ID   id numérico da conta @esacevirtual (opcional: descoberto via /me)
  IMG_BASE_URL URL pública onde estão as imagens JPG, ex.:
               https://raw.githubusercontent.com/<usuario>/<repo>/main/img
"""
import argparse, json, os, sys, time, urllib.parse, urllib.request
from datetime import datetime, timezone, timedelta

AQUI = os.path.dirname(os.path.abspath(__file__))
FILA = os.path.join(AQUI, "fila.json")
API = "https://graph.instagram.com/v25.0"
TZ = timezone(timedelta(hours=-3))  # America/Sao_Paulo (sem horário de verão)


def carregar_env():
    p = os.path.join(AQUI, ".env")
    if os.path.exists(p):
        for linha in open(p, encoding="utf-8"):
            linha = linha.strip()
            if linha and not linha.startswith("#") and "=" in linha:
                k, v = linha.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def api(metodo, caminho, **params):
    params["access_token"] = os.environ["IG_TOKEN"]
    dados = urllib.parse.urlencode(params).encode()
    url = f"{API}/{caminho}"
    if metodo == "GET":
        url += "?" + dados.decode(); dados = None
    req = urllib.request.Request(url, data=dados, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        corpo = e.read().decode(errors="replace")
        raise RuntimeError(f"{metodo} {caminho} -> HTTP {e.code}: {corpo}")


def ig_user_id():
    if os.environ.get("IG_USER_ID"):
        return os.environ["IG_USER_ID"]
    me = api("GET", "me", fields="user_id,username")
    print(f"Conta: @{me.get('username')} (id {me.get('user_id')})")
    return str(me["user_id"])


def esperar_container(cid):
    for _ in range(10):
        st = api("GET", cid, fields="status_code,status")
        if st.get("status_code") == "FINISHED":
            return
        if st.get("status_code") in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Container {cid} falhou: {st}")
        time.sleep(6)
    raise RuntimeError(f"Container {cid} não ficou pronto a tempo")


def publicar(post, uid, base):
    urls = [f"{base.rstrip('/')}/{img}" for img in post["imagens"]]
    if len(urls) == 1:
        c = api("POST", f"{uid}/media", image_url=urls[0], caption=post["legenda"])
        cid = c["id"]
    else:
        filhos = []
        for u in urls:
            filhos.append(api("POST", f"{uid}/media", image_url=u, is_carousel_item="true")["id"])
        for f in filhos:
            esperar_container(f)
        c = api("POST", f"{uid}/media", media_type="CAROUSEL",
                children=",".join(filhos), caption=post["legenda"])
        cid = c["id"]
    esperar_container(cid)
    pub = api("POST", f"{uid}/media_publish", creation_id=cid)
    return pub["id"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--post"); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check-token", action="store_true")
    a = ap.parse_args()
    carregar_env()
    if "IG_TOKEN" not in os.environ:
        sys.exit("Falta IG_TOKEN (variável de ambiente ou .env)")
    if a.check_token:
        print(api("GET", "me", fields="user_id,username,account_type")); return
    base = os.environ.get("IMG_BASE_URL") or sys.exit("Falta IMG_BASE_URL")
    fila = json.load(open(FILA, encoding="utf-8"))
    agora = datetime.now(TZ)
    uid = None; mudou = False
    for post in fila:
        vencido = datetime.fromisoformat(post["quando"]).replace(tzinfo=TZ) <= agora
        alvo = (a.post and post["post"] == a.post) or (not a.post and post["status"] == "pendente" and vencido)
        if not alvo:
            continue
        print(f"-> post {post['post']} ({post['quando']}, {len(post['imagens'])} imagem/ns)")
        if a.dry_run:
            continue
        try:
            uid = uid or ig_user_id()
            mid = publicar(post, uid, base)
            post["status"] = "publicado"; post["ig_media_id"] = mid
            post["publicado_em"] = datetime.now(TZ).isoformat(timespec="seconds")
            print(f"   publicado: media id {mid}")
        except Exception as e:
            post["status"] = "erro"; post["erro"] = str(e)[:500]
            print(f"   ERRO: {e}", file=sys.stderr)
        mudou = True
        json.dump(fila, open(FILA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if not mudou:
        print("Nada a publicar agora.")


if __name__ == "__main__":
    main()
