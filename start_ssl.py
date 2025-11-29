"""Script para generar certificados SSL autofirmados para desarrollo."""

import datetime
import os

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa

CERT_DIR = "certs"
KEY_PATH = os.path.join(CERT_DIR, "key.pem")
CERT_PATH = os.path.join(CERT_DIR, "cert.pem")

def generate_self_signed_cert():
    "Genera un certificado SSL autofirmado y una clave privada."
    if not os.path.exists(CERT_DIR):
        os.makedirs(CERT_DIR)
    if os.path.exists(KEY_PATH) and os.path.exists(CERT_PATH):
        print("Los certificados ya existen.")
        return

    print("Generando certificados autofirmados con Python...")
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).sign(key, hashes.SHA256())

    with open(KEY_PATH, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))
    with open(CERT_PATH, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    print("Certificados generados en 'certs/'.")

if __name__ == "__main__":
    generate_self_signed_cert()
