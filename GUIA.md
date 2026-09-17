# Agendamento do @esacevirtual pela API do Instagram

Esta pasta é um repositório pronto: 36 imagens em JPG (`img/`), a fila de 22 posts com data, hora e legenda (`fila.json`), o script que publica (`publicar.py`) e um workflow do GitHub Actions que roda a cada 30 minutos e publica o que estiver vencido.

A API da Meta não tem "agendar": ela publica na hora. Por isso o agendamento é o GitHub rodando o script no horário. Nada é publicado antes da data/hora que está em `fila.json`.

## O que você precisa fazer (uma vez só)

### 1. Criar o app na Meta (≈10 min)

1. Entre em https://developers.facebook.com/apps com o Facebook/Instagram da ESACE e clique em **Criar app**.
2. Caso de uso: **"Gerenciar tudo no seu perfil"** / opção com **Instagram** (a que menciona "Instagram API with Instagram Login"). Nome: `ESACE Publicador`.
3. No painel do app, menu **Instagram → API setup with Instagram login**.
4. Em **Generate access tokens**, clique **Add account**, entre com o **@esacevirtual** (conta profissional — já é) e autorize.
5. Clique **Generate token** ao lado da conta. Marque as permissões, pelo menos:
   `instagram_business_basic` e `instagram_business_content_publish`.
6. Copie o token (é de longa duração, 60 dias — cobre outubro inteiro) e o **Instagram user ID** que aparece ao lado da conta.

Não precisa de revisão do app: para a própria conta adicionada como tester/administrador funciona em modo de desenvolvimento.

### 2. Criar o repositório no GitHub (≈5 min)

1. https://github.com/new → nome `esace-instagram`, **Público** (as imagens precisam de URL pública — só as artes ficam públicas, o token não).
2. Suba todo o conteúdo desta pasta (pode arrastar no site, ou `git push`).
3. **Settings → Secrets and variables → Actions → New repository secret**:
   - `IG_TOKEN` = o token do passo 1.6
   - `IG_USER_ID` = o ID numérico do passo 1.6
4. **Settings → Actions → General → Workflow permissions**: marque **Read and write permissions** (para o robô salvar o status na fila).

### 3. Testar (≈2 min)

- Aba **Actions → Publicar no Instagram → Run workflow**, deixe o campo vazio → Run. Deve terminar verde com "Nada a publicar agora." (nenhum post venceu ainda).
- Para testar de verdade, no campo *post* digite `01` e rode: ele publica o post 01 na hora. Se preferir não publicar de teste, pule.

Pronto. A partir daí o GitHub publica cada post até 30 min após o horário da fila (01/10 12:30, 02/10 17:00, …).

## Rodar no seu Mac em vez do GitHub

```bash
cd esace-ig-api
cat > .env <<EOF
IG_TOKEN=cole_o_token
IG_USER_ID=1784...
IMG_BASE_URL=https://raw.githubusercontent.com/SEU_USUARIO/esace-instagram/main/img
EOF
python3 publicar.py --check-token   # deve mostrar username esacevirtual
python3 publicar.py --dry-run       # lista o que publicaria agora
```

As imagens ainda precisam estar em URL pública (a Meta baixa de lá), então o repo continua necessário — ou troque `IMG_BASE_URL` por uma pasta no esacevirtual.com.

## Editar a fila / próximas campanhas

`fila.json` é a única fonte: cada item tem `post`, `quando` (`AAAA-MM-DDTHH:MM:00`, horário de Brasília), `imagens` (1 = foto, 2–10 = carrossel), `legenda` e `status` (`pendente` → `publicado` ou `erro`). Para uma campanha nova: coloque os JPG em `img/`, acrescente os itens e faça push.

Limites da Meta: só JPEG, até 100 publicações por 24 h, proporção entre 4:5 e 1.91:1 (as artes são 4:5, ok).

## Horários definidos

| Post | Data | Hora | Lâminas |
|---|---|---|---|
| 01 | qui 01/10 | 12:30 | 1 |
| 02 | sex 02/10 | 17:00 | 3 |
| 03 | seg 05/10 | 18:30 | 3 |
| 04 | ter 06/10 | 12:00 | 1 |
| 05 | qua 07/10 | 18:00 | 1 |
| 06 | qui 08/10 | 12:30 | 1 |
| 07 | sex 09/10 | 17:00 | 1 |
| 08 | seg 12/10 | 18:30 | 1 |
| 09 | ter 13/10 | 12:00 | 1 |
| 10 | qua 14/10 | 18:00 | 1 |
| 11 | qui 15/10 | 12:30 | 3 |
| 12 | sex 16/10 | 17:00 | 1 |
| 13 | seg 19/10 | 18:30 | 1 |
| 14 | ter 20/10 | 12:00 | 3 |
| 15 | qua 21/10 | 18:00 | 1 |
| 16 | qui 22/10 | 12:30 | 1 |
| 17 | sex 23/10 | 17:00 | 1 |
| 18 | seg 26/10 | 18:30 | 3 |
| 19 | ter 27/10 | 12:00 | 1 |
| 20 | qua 28/10 | 18:00 | 3 |
| 21 | qui 29/10 | 12:30 | 1 |
| 22 | sex 30/10 | 17:00 | 3 |

Atenção: o post 01 (Dia da Pessoa Idosa) já está agendado também no Meta Business Suite para 01/10 12:30. Para não sair duplicado, apague um dos dois: ou o do Planner (business.facebook.com → Planner → 1 de out → excluir), ou mude o `status` do post 01 em `fila.json` para `"publicado"`.
