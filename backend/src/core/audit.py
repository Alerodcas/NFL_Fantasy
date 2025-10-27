import csv
import os
import uuid
from datetime import datetime, timezone
import hashlib
from typing import Optional

# Archivo de auditoría (CSV)
# keep audit log next to project root as before; adjust path relative to this file
AUDIT_CSV_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'audit_log.csv')

CSV_HEADERS = [
    'event_id',
    'timestamp',
    'user_id',
    'action',
    'entity_type',
    'entity_id',
    'source_ip',
    'user_agent',
    'status',
    'details',
    'masked_data',
    'signature'
]


def _ensure_file():
    # Crear archivo con cabecera si no existe
    if not os.path.exists(AUDIT_CSV_PATH):
        dirpath = os.path.dirname(AUDIT_CSV_PATH)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)
        with open(AUDIT_CSV_PATH, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)


def _compute_signature(row_values: list[str]) -> str:
    # Firma simple SHA256 sobre la concatenación de los valores (no criptográficamente robusta)
    m = hashlib.sha256()
    joined = '|'.join(row_values)
    m.update(joined.encode('utf-8'))
    return 'SHA256:' + m.hexdigest()


def log_event(
    action: str,
    user_id: Optional[str],
    status: str,
    details: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    source_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    masked_data: bool = False,
):
    """Escribe una fila en el CSV de auditoría.

    Nota: el CSV debe considerarse inmutable. Este método solo añade líneas; no modifica.
    """
    _ensure_file()

    event_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    row = [
        event_id,
        timestamp,
        user_id or '',
        action,
        entity_type or '',
        entity_id or '',
        source_ip or '',
        user_agent or '',
        status,
        details or '',
        'true' if masked_data else 'false',
        ''  # placeholder for signature
    ]

    signature = _compute_signature(row[:-1])
    row[-1] = signature

    # Append-only write
    with open(AUDIT_CSV_PATH, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(row)

    return event_id
