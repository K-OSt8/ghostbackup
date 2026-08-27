import logging
import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from zipfile import ZIP_DEFLATED
from . import LOGGER_NAME
from .ghostfileset import GhostFileSet
from .config import BackUpConfig
from .ghostclient import GhostClient
from .ocios import OSFileArchive


class BackUp:
    def __init__(self, config:BackUpConfig):
        self.__ghost = GhostClient(accesstoken=config.getGhost()['AccessToken'], host = config.getGhost()['Host'])
        self.__fileset = GhostFileSet(ghost_installdir=Path(config.getGhost()['Dir']))
        self.__archive = OSFileArchive(bucket_name=config.getOCI()['BucketName'], 
                            name_space=config.getOCI()['NameSpace'],
                            name_prefix="ghost-backup",
                            name_postfix=".zip")
        self.__log = logging.getLogger(LOGGER_NAME)
    
    def backup(self, force=False):
        if force or self.__backup_required():
            if force: self.__log.debug("Set to force: up-to-date-check is skipped")
            archive_name = self.__backup()
            self.__log.info("Stored Backup '%s' in Archive", archive_name)
        elif not force:
            self.__log.info("Back-up not required: No modification since last archival at '%s'", self.__ghost.lastModified())


    def __backup_required(self) -> bool:
        last_edit = self.__ghost.lastModified()
        archived = self.__archive.contains(last_edit)
        self.__log.debug("Ghost last modified %s: Archive contains back-up %s", last_edit, archived)
        return not archived

    def __backup(self) -> str:

        #create temp-dir
        with TemporaryDirectory(prefix="ghost-backup") as temp_dir:
            to_pack = []
            tmp_path = Path(temp_dir)
            now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")

            #create export
            export_path = tmp_path.joinpath(f'ghost-export-{now}.json')
            with open(export_path, 'w') as export_file:
                json.dump(self.__ghost.backUp(), export_file, ensure_ascii=False)
            to_pack.append(export_path)
        
            #create file-system package
            content_path =self.__fileset.pack(tmp_path.joinpath(f"ghost-content-{now}.zip"))
            to_pack.append(content_path)
        
            #zip
            with ZipFile(tmp_path.joinpath(f"backup-{now}.zip"), 'w', ZIP_DEFLATED) as backup_package:
                for path in to_pack:
                    backup_package.write(path, arcname=path.name)
        
            #archive
            archive_name = self.__archive.store(Path(backup_package.filename))
        
        return archive_name
