
import logging
import zipfile
from pathlib import Path
from . import LOGGER_NAME
from .selective_zip import SelectiveZipFile


class GhostFileSet:

    _PACK_NAME_DEFAULT: Path = Path("ghost_backup.zip")
    _CONTENT_PATH_DEFAULT: Path = Path("content")
    _DIRECTORIES_DEFAULT: set[str] = {"data", "files", "images", "media", "settings", "themes"}

    def __init__(self, ghost_install_dir: Path):
        if not ghost_install_dir: ghost_install_dir = self._PACK_NAME_DEFAULT
        self.__path_content = ghost_install_dir.joinpath(self._CONTENT_PATH_DEFAULT)
        self.__logger = logging.getLogger(LOGGER_NAME)

    def pack(self, dest=Path("backup.zip")) -> Path:
        file_path = self.__path_content.joinpath(dest)
        with SelectiveZipFile(file_path, 'w', zipfile.ZIP_LZMA) as zipf:
            for path in self._DIRECTORIES_DEFAULT:
                bkp_dir = self.__path_content.joinpath(path)
                if bkp_dir.exists() and bkp_dir.is_dir():
                    for root, dirName, fNames in bkp_dir.walk(follow_symlinks=True):
                        for fName in fNames:
                            fPath = Path(root).joinpath(fName)
                            name = fPath.relative_to(self.__path_content)
                            zipf.write(fPath, arcname=name)
                    self.__logger.debug(f"Compressed Directory '{bkp_dir}'")
                else:
                    self.__logger.warning("Invalid or non-existent dir '%s'", bkp_dir)
        return file_path


