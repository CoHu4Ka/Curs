from web3 import Web3
from solcx import compile_source, install_solc
import json

# Устанавливаем нужную версию компилятора Solidity
install_solc('0.8.0')

# Solidity-код смарт-контракта
contract_source = '''
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
'''

def main():
    # Подключаемся к локальному Ganache (по умолчанию http://127.0.0.1:8545)
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
    if not w3.isConnected():
        raise ConnectionError("Не удалось подключиться к Ganache. Проверьте, что Ganache запущен.")

    # Используем первый аккаунт Ganache для транзакций
    account = w3.eth.accounts[0]
    print(f"Используется аккаунт: {account}")

    # Компилируем контракт
    compiled_sol = compile_source(contract_source, output_values=['abi', 'bin'], solc_version='0.8.0')
    contract_id, contract_interface = compiled_sol.popitem()

    abi = contract_interface['abi']
    bytecode = contract_interface['bin']

    # Создаем контракт в web3
    DigitalCertificate = w3.eth.contract(abi=abi, bytecode=bytecode)

    # Отправляем транзакцию на развертывание контракта
    tx_hash = DigitalCertificate.constructor().transact({'from': account})
    print("Отправка транзакции развертывания контракта...")

    # Ждем подтверждения транзакции
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    contract_address = tx_receipt.contractAddress
    print(f"Контракт развернут по адресу: {contract_address}")

    # Создаем экземпляр контракта для взаимодействия
    contract_instance = w3.eth.contract(address=contract_address, abi=abi)

    # Выдаем сертификат тестовому аккаунту (например, второму аккаунту Ganache)
    recipient = w3.eth.accounts[1]
    print(f"Выдача сертификата аккаунту: {recipient}")

    tx = contract_instance.functions.issueCertificate(
        recipient,
        "Blockchain Developer",
        "OpenAI"
    ).transact({'from': account})

    w3.eth.wait_for_transaction_receipt(tx)
    print("Сертификат выдан.")

    # Считываем сертификат с блокчейна
    cert = contract_instance.functions.getCertificate(recipient).call()
    print(f"Сертификат для {recipient}:")
    print(f"  Имя: {cert[0]}")
    print(f"  Издатель: {cert[1]}")
    print(f"  Время выдачи (timestamp): {cert[2]}")

    # Пример создания цифровой подписи сообщения
    message = "Подпись цифрового сертификата"
    message_hash = w3.keccak(text=message)

    # Получаем приватный ключ (Ganache обычно выводит их в GUI или CLI)
    # Здесь нужно заменить 'PRIVATE_KEY_ПОЛУЧЕННЫЙ_ИЗ_GANACHE' на реальный приватный ключ
    private_key = '0c2cc79a689567844aa0d65cdfbc0faa3d41b3e7f4f79a376f28040b04aff00'

    signed_message = w3.eth.account.signHash(message_hash, private_key=private_key)
    print(f"Подпись сообщения: {signed_message.signature.hex()}")

if __name__ == "__main__":
    main()
