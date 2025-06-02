#!/bin/bash
set -euo pipefail

CERT_DIR="./tls"
mkdir -p "$CERT_DIR"
cd "$CERT_DIR"

echo "Generating OpenSSL config for CA and server..."

# CA config
cat > ca_openssl.cnf <<EOF
[ req ]
default_bits       = 4096
distinguished_name = dn
x509_extensions    = v3_ca
prompt             = no

[ dn ]
CN = Redis Test CA

[ v3_ca ]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints = critical, CA:true
keyUsage = critical, keyCertSign, cRLSign
EOF

# Server config
cat > server_openssl.cnf <<EOF
[ req ]
default_bits       = 2048
distinguished_name = dn
req_extensions     = v3_req
prompt             = no

[ dn ]
CN = redis-server

[ v3_req ]
basicConstraints = CA:false
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = localhost
IP.1 = 127.0.0.1
EOF

echo "Generating CA key and certificate..."
openssl req -x509 -new -nodes \
  -keyout ca.key -out ca.crt -days 3650 \
  -config ca_openssl.cnf

echo "Generating server key and CSR..."
openssl req -new -nodes \
  -keyout redis.key -out redis.csr \
  -config server_openssl.cnf

echo "Signing server certificate with CA..."
openssl x509 -req -in redis.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out redis.crt -days 365 \
  -extfile server_openssl.cnf -extensions v3_req

echo "Certificates generated in $CERT_DIR:"
ls -l
