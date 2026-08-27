
import logging
import zipfile
from pathlib import Path
from . import LOGGER_NAME


class GhostFileSet:
    __pack_name = Path("ghost_backup.zip")
    content = Path("content")
    dirs = ["data",
        "files",
        "images",
        "media",
        "settings",
        "themes"
    ]

    def __init__(self, ghost_installdir: Path):
        if not ghost_installdir: ghost_installdir = GhostFileSet.__pack_name
        self.__path_content = ghost_installdir.joinpath(GhostFileSet.content)

    def pack(self, dest=Path("backup.zip")) -> Path:
        file_path = self.__path_content.joinpath(dest)
        with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_LZMA) as zipf:
            for path in GhostFileSet.dirs:
                dir = self.__path_content.joinpath(path)
                if dir.exists() and dir.is_dir():
                    for root, dirName, fNames in dir.walk(follow_symlinks=True):
                        for fName in fNames:
                            fPath = Path(root).joinpath(fName)
                            name = fPath.relative_to(self.__path_content)
                            zipf.write(fPath, arcname=name)
                else:
                    logging.getLogger(LOGGER_NAME).warning("Invalid or inexistant dir '%s'", dir)
        return file_path
