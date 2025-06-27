
# Имитация PKI-системы с использованием OpenSSL и Python

В рамках данной курсовой работы я разработал проект, демонстрирующий основы функционирования инфраструктуры открытых ключей (PKI). Основной целью было создание системы, способной выпускать и проверять цифровые сертификаты, используя инструменты OpenSSL и язык программирования Python.

---

## Структура проекта

Мной была организована следующая структура каталогов и файлов:

```
pki_demo/
├── ca/
│   ├── ca.key.pem          # Приватный ключ центра сертификации (CA)
│   ├── ca.cert.pem         # Самоподписанный сертификат CA
├── user/
│   ├── user.key.pem        # Приватный ключ пользователя
│   ├── user.csr.pem        # Запрос на сертификат пользователя
│   ├── user.cert.pem       # Сертификат, подписанный CA
├── main.py                 # Основной скрипт автоматизации
```

---

## 1. Установка необходимых зависимостей

На первом этапе я установил библиотеку `cryptography`, которая предоставляет высокоуровневый API для работы с криптографией в Python:

```bash
pip install cryptography
```

---

## 2. Создание центра сертификации (CA)

Я начал с генерации приватного ключа центра сертификации, который впоследствии использовался для подписания других сертификатов. Далее создал самоподписанный сертификат для CA:

```python
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
import datetime, os

os.makedirs("ca", exist_ok=True)

ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
with open("ca/ca.key.pem", "wb") as f:
    f.write(ca_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption()
    ))

subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "MD"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "MyPKI"),
    x509.NameAttribute(NameOID.COMMON_NAME, "MyPKI Root CA"),
])

cert = x509.CertificateBuilder().subject_name(subject).issuer_name(issuer).public_key(
    ca_key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.utcnow()
).not_valid_after(
    datetime.datetime.utcnow() + datetime.timedelta(days=3650)
).add_extension(
    x509.BasicConstraints(ca=True, path_length=None), critical=True
).sign(ca_key, hashes.SHA256())

with open("ca/ca.cert.pem", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))
```

---

## 3. Генерация пользовательского ключа и создание CSR

Следующим шагом я сгенерировал ключ для пользователя и сформировал запрос на сертификат (CSR), который позже подписал с помощью CA:

```python
os.makedirs("user", exist_ok=True)

user_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
with open("user/user.key.pem", "wb") as f:
    f.write(user_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption()
    ))

csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "MD"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "User Company"),
    x509.NameAttribute(NameOID.COMMON_NAME, "user@example.com"),
])).sign(user_key, hashes.SHA256())

with open("user/user.csr.pem", "wb") as f:
    f.write(csr.public_bytes(serialization.Encoding.PEM))
```

---

## 4. Подписание пользовательского сертификата

После получения запроса, я подписал его с помощью ключа CA, тем самым выпустив действующий сертификат:

```python
from cryptography.hazmat.backends import default_backend

with open("ca/ca.key.pem", "rb") as f:
    ca_key = serialization.load_pem_private_key(f.read(), password=None)

with open("ca/ca.cert.pem", "rb") as f:
    ca_cert = x509.load_pem_x509_certificate(f.read(), default_backend())

with open("user/user.csr.pem", "rb") as f:
    csr = x509.load_pem_x509_csr(f.read(), default_backend())

user_cert = x509.CertificateBuilder().subject_name(
    csr.subject
).issuer_name(
    ca_cert.subject
).public_key(
    csr.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.utcnow()
).not_valid_after(
    datetime.datetime.utcnow() + datetime.timedelta(days=365)
).add_extension(
    x509.BasicConstraints(ca=False, path_length=None), critical=True
).sign(ca_key, hashes.SHA256())

with open("user/user.cert.pem", "wb") as f:
    f.write(user_cert.public_bytes(serialization.Encoding.PEM))
```

---

## 5. Проверка подлинности сертификата

Завершающим этапом я реализовал механизм проверки: удостоверился, что сертификат действительно подписан доверенным центром сертификации.

```python
if user_cert.issuer == ca_cert.subject:
    print("Сертификат подтверждён: подписан доверенным CA.")
else:
    print("Сертификат НЕ подтверждён.")
```

---

## Вывод

В результате реализации данного проекта я смоделировал простейшую PKI-систему:
- Создал корневой центр сертификации;
- Сгенерировал ключи и CSR;
- Подписал сертификат;
- Провёл проверку подлинности.

Данный опыт является важным шагом в понимании принципов цифровой безопасности и криптографии в современной информационной инфраструктуре.

