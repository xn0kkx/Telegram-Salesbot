# 🤖 Telegram Sales Bot

Este é um **bot de vendas automatizado para Telegram**, desenvolvido em Python com o framework [Aiogram](https://docs.aiogram.dev/). Ele permite apresentar produtos com mídia, integrar múltiplos gateways de pagamento e enviar mensagens personalizadas para os usuários.

---

## 🚀 Funcionalidades

- 📷 Envio de **fotos** e **vídeos** dos produtos.
- 💬 Mensagens **customizáveis** via arquivos `.txt`.
- 💳 Integração com os seguintes gateways de pagamento:
  - [Mercado Pago](https://www.mercadopago.com.br/)
  - [Hoopay](https://www.hoopay.com.br/)
  - [EFI (Gerencianet)](https://efipay.com.br/)
- 🧾 Suporte a **QR Code PIX** e **código copiado**.
- 🔁 Estratégias de **upsell** e **remarketing** integradas.
- 🗃 Banco de dados PostgreSQL com script de setup incluso.
- 🔐 Suporte a certificados para ambiente de homologação e produção.

---

## 🗂 Estrutura do Projeto

```
.
├── main.py                  # Arquivo principal do bot
├── certs/                   # Certificados para autenticação com gateways
├── database/                # Script SQL e conexão com banco PostgreSQL
├── keyboards/               # Teclados inline e de navegação
├── medias/                  # Imagens e vídeos dos produtos
├── mensagens/               # Arquivos .txt com mensagens personalizadas
├── payments/                # Integrações com APIs de pagamento
├── utils/                   # Funções auxiliares
├── requirements.txt         # Dependências do projeto
├── .env                     # Variáveis de ambiente (não incluso no repositório)
```

---

## ⚙️ Requisitos

- Python 3.8+
- Conta ativa nos gateways de pagamento utilizados
- PostgreSQL

---

## 📦 Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/telegram-sales-bot.git
   cd telegram-sales-bot
   ```

2. Crie e ative um ambiente virtual (opcional, mas recomendado):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Crie um arquivo `.env` com as variáveis exigidas (exemplo abaixo).

5. Configure o banco de dados:
   ```bash
   psql -U seu_usuario -d telegrambot -f database/setup_telegrambot.sql
   ```

6. Execute o bot:
   ```bash
   python main.py
   ```

---

## 🔐 Exemplo de `.env`

```dotenv
BOT_TOKEN=seu_token_telegram
DB_HOST=localhost
DB_PORT=5432
DB_NAME=telegrambot
DB_USER=botuser
DB_PASSWORD=sua_senha

# Gateway de pagamento (Mercado Pago, EFI ou Hoopay)
PAYMENT_PROVIDER=efi

# Configurações específicas por gateway (exemplo para EFI)
EFI_CLIENT_ID=...
EFI_CLIENT_SECRET=...
EFI_PIX_KEY=...
EFI_CERT_PATH=certs/homologacao-746298-Telegram-bot.p12


# Links personalizados por plano
LINK_BASICO=https://example.com/basico
LINK_PREMIUM=https://example.com/premium
LINK_VIP=https://example.com/vip

# Conta do telegram para informar venda
OWNER_ID=


# Planos disponíveis
PLANO_BASICO_TEXTO="Plano Básico - R$ 1"
PLANO_BASICO_VALOR=1
PLANO_PREMIUM_TEXTO="Plano Premium - R$ 2"
PLANO_PREMIUM_VALOR=2
PLANO_VIP_TEXTO="Plano VIP - R$ 3"
PLANO_VIP_VALOR=3

# Upsell (ofertas após pagamento)
UPSELL_PREMIUM_TEXTO="🎯 Upgrade para Premium - R$ 2"
UPSELL_PREMIUM_VALOR=2
UPSELL_VIP_TEXTO="🚀 Upgrade para VIP - R$ 3"
UPSELL_VIP_VALOR=3

# Remarketing (ofertas para quem não pagou)
REMARKETING_BASICO_TEXTO="📦 Reativar Plano Básico - R$ 1"
REMARKETING_BASICO_VALOR=1
REMARKETING_PREMIUM_TEXTO="🎯 Reativar Premium - R$ 2"
REMARKETING_PREMIUM_VALOR=2
REMARKETING_VIP_TEXTO="🚀 Reativar VIP - R$ 3"
REMARKETING_VIP_VALOR=3

# Mídias opcionais para envio
START_MEDIA=medias/videos/Trueno-AE86.mp4
UPSELL_MEDIA=medias/videos/upsell.mp4
REMARKETING_MEDIA=medias/videos/remarketing.mp4
```

---

## 🧠 Observações

- As mensagens são lidas dinamicamente dos arquivos `.txt` na pasta `mensagens/`.
- A pasta `medias/` contém as imagens e vídeos que o bot pode enviar para o usuário.
- Certificados `.p12` e `.pem` devem ser gerados ou obtidos nas plataformas de pagamento utilizadas.
- A escolha do provedor de pagamento é feita através da variável `PAYMENT_PROVIDER`.

---

## 📄 Licença

Este projeto está licenciado sob a licença MIT.

---

## 🙋‍♂️ Contato

Desenvolvido por **n0kk**  
📧 E-mail: n0kk@n0kk.com
