// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DigitalCertificate {
    struct Certificate {
        string name;
        string issuer;
        uint256 issuedAt;
    }

    mapping(address => Certificate) public certificates;

	constructor() {
        certificates[0c2cc79a689567844aa0d65cdfbc0faa3d41b3e7f4f79a376f28040b04aff00] = Certificate(
            "Anatoly",
            "Test Certification",
            block.timestamp
        );
    }

    function issueCertificate(address recipient, string memory name, string memory issuer) public {
        certificates[recipient] = Certificate(name, issuer, block.timestamp);
    }

    function getCertificate(address recipient) public view returns (string memory, string memory, uint256) {
        Certificate memory cert = certificates[recipient];
        require(cert.issuedAt != 0, "Certificate not found");
        return (cert.name, cert.issuer, cert.issuedAt);
    }
}
