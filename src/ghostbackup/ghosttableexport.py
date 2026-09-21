from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from . import LOGGER_NAME

import base64
import oci
import pymysql
import logging

ZIP_EXTENSION = '.zip'

_BATCH_SIZE = 1000  # size of fetchmany()


class GhostTables:
    """
    connection_string: "host:port/database" oder "host/database"
        (Port ist optional, Default 3306), z.B. "db.example.com/app"
        oder "10.0.0.5:3307/app"
    db_user: Datenbank-Benutzername
    secret_ocid: OCID des Secrets im OCI Vault, das das DB-Passwort enthält
    """

    TABLES: list[str] = [
        # Content
        "posts",
        "posts_meta",
        "posts_tags",
        "posts_authors",
        "tags",
        # Members
        "members",
        "members_stripe_customers",
        "members_stripe_customers_subscriptions",
        "members_products",
        "members_labels",
        "labels",
        "members_newsletters",
        # UGC
        "comments",
        "comment_likes",
        "comment_reports",
        # Settings
        "settings"
    ]

    DIR_NAME: str = "db_dump"


    def __init__(self, host: str, db_name: str, db_user: str, secret_ocid: str, port = 3306) -> None:
        self._db_user = db_user
        self._db_host = host
        self._db_port = int(port)
        self._db_name = db_name
        self._password = self._read_secret_from_oci_vault(secret_ocid)
        self.__logger = logging.getLogger(LOGGER_NAME)


    @staticmethod
    def _read_secret_from_oci_vault(secret_ocid: str) -> str:
        client = oci.secrets.SecretsClient(oci.config.from_file())

        try:
            response = client.get_secret_bundle(secret_id=secret_ocid)
        except Exception as exc:  # oci wirft eigene ServiceError-Klassen
            raise RuntimeError(f"No access to secret '{secret_ocid}': {exc}") from exc

        content = response.data.secret_bundle_content.content
        return base64.b64decode(content).decode("utf-8")

    def export_tables(self, file_name: str | Path) -> Path:

        output_path = Path(file_name)
        if not output_path.suffix or output_path.suffix != ".zip": output_path = output_path.with_suffix(".zip")

        connection = pymysql.connect(
            host=self._db_host,
            port=self._db_port,
            user=self._db_user,
            password=self._password,
            database=self._db_name,
            charset="utf8mb4",
        )
        self.__logger.debug("Connected to '%s'", connection.get_host_info())
        with ZipFile(output_path, 'w', ZIP_DEFLATED) as zipf:
            try:
                for table_name in self.TABLES:
                    file_name = table_name+".sql"
                    with connection.cursor() as cursor, zipf.open(name=file_name, mode="w") as sql_file:
                        query = f"SELECT * FROM `{table_name}`"
                        cursor.execute(query)

                        columns = [d[0] for d in cursor.description]
                        column_list = ", ".join(f"`{c}`" for c in columns)

                        while rows := cursor.fetchmany(_BATCH_SIZE):
                            for row in rows:
                                sql_file.write(f"INSERT INTO `{table_name}` ({column_list}) VALUES (".encode("utf-8"))
                                for i, v in enumerate(row):
                                    if i:
                                        sql_file.write(b", ")
                                    value = "NULL" if v is None else connection.escape(v)
                                    sql_file.write(str(value).encode("utf-8"))
                                sql_file.write(b");\n")
                        self.__logger.debug("Wrote table '%s' to '%s'", table_name, file_name)
            finally:
                connection.close()

        return output_path

