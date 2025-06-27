import os
import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# === Создание каталогов ===
os.makedirs("ca", exist_ok=True)
os.makedirs("user", exist_ok=True)

# === Генерация ключа CA ===
ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
with open("ca/ca.key.pem", "wb") as f:
    f.write(ca_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption()
    ))

# === Генерация самоподписанного сертификата CA ===
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "MD"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "MyPKI"),
    x509.NameAttribute(NameOID.COMMON_NAME, "MyPKI Root CA"),
])
ca_cert = x509.CertificateBuilder()\
    .subject_name(subject)\
    .issuer_name(issuer)\
    .public_key(ca_key.public_key())\
    .serial_number(x509.random_serial_number())\
    .not_valid_before(datetime.datetime.utcnow())\
    .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=3650))\
    .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)\
    .sign(ca_key, hashes.SHA256())

with open("ca/ca.cert.pem", "wb") as f:
    f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

# === Генерация ключа пользователя ===
user_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
with open("user/user.key.pem", "wb") as f:
    f.write(user_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption()
    ))

# === Создание CSR (запроса на сертификат) ===
csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "MD"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "User Company"),
    x509.NameAttribute(NameOID.COMMON_NAME, "user@example.com"),
])).sign(user_key, hashes.SHA256())

with open("user/user.csr.pem", "wb") as f:
    f.write(csr.public_bytes(serialization.Encoding.PEM))

# === Подписание сертификата пользователя CA ===
user_cert = x509.CertificateBuilder()\
    .subject_name(csr.subject)\
    .issuer_name(ca_cert.subject)\
    .public_key(csr.public_key())\
    .serial_number(x509.random_serial_number())\
    .not_valid_before(datetime.datetime.utcnow())\
    .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))\
    .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)\
    .sign(ca_key, hashes.SHA256())

with open("user/user.cert.pem", "wb") as f:
    f.write(user_cert.public_bytes(serialization.Encoding.PEM))

print("Сертификат пользователя успешно подписан и сохранён.")
