from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# === Загрузка CA и пользовательского сертификата ===
with open("ca/ca.cert.pem", "rb") as f:
    ca_cert = x509.load_pem_x509_certificate(f.read(), default_backend())

with open("user/user.cert.pem", "rb") as f:
    user_cert = x509.load_pem_x509_certificate(f.read(), default_backend())

# === Проверка: совпадают ли issuer и subject ===
if user_cert.issuer == ca_cert.subject:
    print("Сертификат подтверждён: подписан доверенным CA.")
else:
    print("Сертификат НЕ подтверждён.")
