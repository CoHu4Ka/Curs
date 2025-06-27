# Работа с Ganache и Ethereum смарт-контрактами на Python

Привет! В этом проекте я хочу рассказать и показать, как я работал с Ganache и создавал простой смарт-контракт для цифровых сертификатов на Ethereum. Вся работа была автоматизирована с помощью Python и библиотеки `web3.py`. Ниже я описываю шаги, которые я выполнял.

---

## Шаг 1. Установка Ganache

Сначала я скачал Ganache GUI с официального сайта:  
https://trufflesuite.com/ganache/

Также можно было установить Ganache CLI через npm:

```bash
npm install -g ganache
```

После установки я запустил Ganache (GUI или CLI) для локального тестирования Ethereum.

---

## Шаг 2. Написание смарт-контракта на Solidity

Я написал простой контракт `DigitalCertificate`, который хранит цифровые сертификаты с названием, издателем и временем выпуска:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DigitalCertificate {
    struct Certificate {
        string name;
        string issuer;
        uint256 issuedAt;
    }

    mapping(address => Certificate) public certificates;

    function issueCertificate(address recipient, string memory name, string memory issuer) public {
        certificates[recipient] = Certificate(name, issuer, block.timestamp);
    }

    function getCertificate(address recipient) public view returns (string memory, string memory, uint256) {
        Certificate memory cert = certificates[recipient];
        require(cert.issuedAt != 0, "Certificate not found");
        return (cert.name, cert.issuer, cert.issuedAt);
    }
}
```

---

## Шаг 3. Компиляция и развертывание смарт-контракта из Python

Для удобства работы с Ethereum я использовал Python и библиотеку `web3.py`. Также понадобилась библиотека `solcx` для компиляции Solidity.

Установил их командой:

```bash
pip install web3 solcx
```

---

## Шаг 4. Скрипт на Python для развертывания и взаимодействия с контрактом

```python
from web3 import Web3
from solcx import compile_source

# Подключаюсь к локальному Ganache
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

if not w3.isConnected():
    raise Exception("Не удалось подключиться к Ganache")

account = w3.eth.accounts[0]

contract_source = '''
pragma solidity ^0.8.0;

contract DigitalCertificate {
    struct Certificate {
        string name;
        string issuer;
        uint256 issuedAt;
    }

    mapping(address => Certificate) public certificates;

    function issueCertificate(address recipient, string memory name, string memory issuer) public {
        certificates[recipient] = Certificate(name, issuer, block.timestamp);
    }

    function getCertificate(address recipient) public view returns (string memory, string memory, uint256) {
        Certificate memory cert = certificates[recipient];
        require(cert.issuedAt != 0, "Certificate not found");
        return (cert.name, cert.issuer, cert.issuedAt);
    }
}
'''

compiled_sol = compile_source(contract_source, output_values=['abi', 'bin'])
contract_id, contract_interface = compiled_sol.popitem()

abi = contract_interface['abi']
bytecode = contract_interface['bin']

DigitalCertificate = w3.eth.contract(abi=abi, bytecode=bytecode)

# Разворачиваю контракт в сети Ganache
tx_hash = DigitalCertificate.constructor().transact({'from': account})
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

contract_address = tx_receipt.contractAddress
print(f"Контракт развернут по адресу: {contract_address}")

contract_instance = w3.eth.contract(address=contract_address, abi=abi)

# Выдаю сертификат другому аккаунту Ganache
recipient = w3.eth.accounts[1]
tx = contract_instance.functions.issueCertificate(recipient, "Blockchain Developer", "OpenAI").transact({'from': account})
w3.eth.wait_for_transaction_receipt(tx)

# Считываю сертификат и вывожу информацию
cert = contract_instance.functions.getCertificate(recipient).call()
print(f"Сертификат для {recipient}:
Название: {cert[0]}
Издатель: {cert[1]}
Дата выдачи (timestamp): {cert[2]}")
```

---

## Что я делал в этом примере?

- Запустил локальную Ethereum-сеть через Ganache.
- Написал и скомпилировал смарт-контракт для выдачи цифровых сертификатов.
- Развернул контракт на Ganache с помощью Python и `web3.py`.
- Выдал сертификат тестовому аккаунту.
- Получил и вывел информацию о сертификате.

---

## Работа с цифровыми подписями и транзакциями

Все транзакции в Ethereum подписываются приватным ключом отправителя. Ganache создает аккаунты с приватными ключами автоматически, а `web3.py` умеет их подписывать.

Для примера я подписал произвольное сообщение:

```python
message = "Подпись цифрового сертификата"
message_hash = w3.keccak(text=message)

signed_message = w3.eth.account.signHash(message_hash, private_key='PRIVATE_KEY_ПОЛУЧЕННЫЙ_ИЗ_GANACHE')

print(f"Signature: {signed_message.signature.hex()}")
```

---

## Итоги и выводы

Ganache — отличная среда для локальной разработки и тестирования Ethereum-приложений.  
Тестовые сети Ethereum ближе к реальному миру, но транзакции там подтверждаются дольше.  
Использование Python и `web3.py` позволило мне быстро автоматизировать взаимодействие с блокчейном, управлять сертификатами, транзакциями и подписями.

Если понадобится, могу расширить проект, добавить более продвинутую работу с подписями или интеграцию с OpenSSL.

---

Спасибо за внимание!