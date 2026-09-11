from __future__ import annotations
from pathlib import Path

import base64
import oci
import pymysql

_BATCH_SIZE = 1000  # Zeilen pro fetchmany()-Aufruf


class GhostTables:
    """
    connection_string: "host:port/database" oder "host/database"
        (Port ist optional, Default 3306), z.B. "db.example.com/app"
        oder "10.0.0.5:3307/app"
    db_user: Datenbank-Benutzername
    secret_ocid: OCID des Secrets im OCI Vault, das das DB-Passwort enthält
    """

    # Tabellenname -> optionaler WHERE-Filter (None = komplette Tabelle)
    TABLES: dict[str, str | None] = {
        "settings": None,
        "orders": "status = 'open'",
        "logs": "created_at >= '2026-01-01'",
    }

    def __init__(self, host: str, db_name: str, db_user: str, secret_ocid: str, port = 3306) -> None:
        self._db_user = db_user
        self._db_host = host
        self._db_port = port
        self._db_name = db_name
        self._password = self._read_secret_from_oci_vault(secret_ocid)


    @staticmethod
    def _read_secret_from_oci_vault(secret_ocid: str) -> str:
        config = oci.config.from_file()  # liest ~/.oci/config
        client = oci.secrets.SecretsClient(config)

        try:
            response = client.get_secret_bundle(secret_id=secret_ocid)
        except Exception as exc:  # oci wirft eigene ServiceError-Klassen
            raise RuntimeError(f"Konnte Secret {secret_ocid} nicht laden: {exc}") from exc

        content = response.data.secret_bundle_content.content
        return base64.b64decode(content).decode("utf-8")

    def export_tables(self, output_dir: str | Path) -> list[Path]:
        """
        Exportiert nur die Daten der in TABLES definierten Tabellen in das
        übergebene Verzeichnis. Pro Tabelle wird eine eigene SQL-Datei
        (<output_dir>/<tabellenname>.sql) angelegt.

        Gibt die Liste der erzeugten Dateipfade zurück.
        """

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        connection = pymysql.connect(
            host=self._db_host,
            port=self._db_port,
            user=self._db_user,
            password=self._password,
            database=self._db_name,
            charset="utf8mb4",
        )

        written_files: list[Path] = []
        try:
            for table_name, where in self.TABLES.items():
                table_file = output_path / f"{table_name}.sql"
                written_files.append(table_file)

                with connection.cursor() as cursor, table_file.open("w", encoding="utf-8") as f:
                    query = f"SELECT * FROM `{table_name}`"
                    if where:
                        query += f" WHERE {where}"
                    cursor.execute(query)

                    columns = [d[0] for d in cursor.description]
                    column_list = ", ".join(f"`{c}`" for c in columns)

                    while rows := cursor.fetchmany(_BATCH_SIZE):
                        for row in rows:
                            values = ", ".join(
                                "NULL" if v is None else connection.escape(v)
                                for v in row
                            )
                            f.write(f"INSERT INTO `{table_name}` ({column_list}) VALUES ({values});\n")
        finally:
            connection.close()

        return written_files

