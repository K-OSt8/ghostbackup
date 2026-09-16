
import logging
import zipfile
from pathlib import Path
from . import LOGGER_NAME


class GhostFileSet:

    _COMPRESSED_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4", ".zip", ".gz"}
    _PACK_NAME_DEFAULT: Path = Path("ghost_backup.zip")
    _CONTENT_PATH_DEFAULT: Path = Path("content")
    _DIRECTORIES_DEFAULT: set[str] = {"data", "files", "images", "media", "settings", "themes"}

    def __init__(self, ghost_install_dir: Path):
        if not ghost_install_dir: ghost_install_dir = self._PACK_NAME_DEFAULT
        self.__path_content = ghost_install_dir.joinpath(self._CONTENT_PATH_DEFAULT)

    def __get_compress_type(self, suffix:str):
        return zipfile.ZIP_STORED if suffix.lower() in self._COMPRESSED_EXTENSIONS else zipfile.ZIP_DEFLATED

    def pack(self, dest=Path("backup.zip")) -> Path:
        file_path = self.__path_content.joinpath(dest)
        with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_LZMA) as zipf:
            for path in self._DIRECTORIES_DEFAULT:
                dir = self.__path_content.joinpath(path)
                if dir.exists() and dir.is_dir():
                    for root, dirName, fNames in dir.walk(follow_symlinks=True):
                        for fName in fNames:
                            fPath = Path(root).joinpath(fName)
                            name = fPath.relative_to(self.__path_content)
                            zipf.write(fPath, arcname=name, compress_type=self.__get_compress_type(fPath.suffix))
                else:
                    logging.getLogger(LOGGER_NAME).warning("Invalid or non-existent dir '%s'", dir)
        return file_path


