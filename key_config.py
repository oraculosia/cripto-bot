from decouple import config
import stripe


# URL base da API do Stripe
URL_BASE = "https://api.stripe.com/v1"


# Chave da API do Stripe
API_KEY_STRIPE = config("API_KEY_STRIPE")
if not API_KEY_STRIPE:
    raise ValueError("A chave da API do Stripe não está definida. Verifique o arquivo .env.")


# Chave do Webhook do Stripe
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET")
if not STRIPE_WEBHOOK_SECRET:
    raise ValueError("A chave do Webhook não foi encontrada. Verifique a configuração.")

