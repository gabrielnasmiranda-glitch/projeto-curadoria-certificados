"""Contexto TLS compartilhado pelos coletores.

Usa o repositório de certificados do sistema operacional (via `truststore`). Em redes
corporativas ou escolares que inspecionam HTTPS, o certificado da rede já está instalado no
sistema, mas não no pacote `certifi` usado pelo httpx por padrão. A verificação de
certificado continua ATIVA; apenas muda onde as autoridades confiáveis são lidas.
"""

import ssl
from functools import lru_cache


@lru_cache
def build_verify() -> ssl.SSLContext | bool:
    try:
        import truststore

        return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    except Exception:  # truststore indisponível: usa o padrão do httpx (certifi)
        return True
