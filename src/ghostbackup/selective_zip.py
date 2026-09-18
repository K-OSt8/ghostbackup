from pathlib import Path
from zipfile import ZipFile, ZIP_STORED, ZIP_DEFLATED


class SelectiveZipFile(ZipFile):
    _COMPRESSED_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4", ".zip", ".gz"}

    def write(self, filename, arcname=None):

        compression_type = self.__select_compression(Path(filename))
        super().write(filename=filename, arcname=arcname, compress_type=compression_type)

    def __select_compression(self, file_path:Path):
        suffix = file_path.suffix
        return ZIP_STORED if (suffix and suffix.lower() in self._COMPRESSED_EXTENSIONS) else ZIP_DEFLATED

