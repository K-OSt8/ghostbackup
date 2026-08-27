import datetime
from pathlib import Path
from oci.object_storage import ObjectStorageClient 
from oci.config import from_file


class OSFileArchive:

    def __init__(self, bucket_name, name_space, name_prefix="package", name_postfix=""):
        self.__client = ObjectStorageClient(from_file()) #~/.oci/config
        self.__b_name = bucket_name
        self.__name_space = name_space
        self.__name_format = name_prefix + "-{date}" + name_postfix

    def contains(self, date: datetime.datetime):

        """
            API doesn't allow for a search.
            But the Object list is ordred alphanumerically. 
            Either go by -start of list -> requires a name and date pattern
            

        """
        if (not isinstance(date, datetime.datetime)):
            raise TypeError(f"date argument must be a datetime got '{type(date).__name__}'")
        resp = self.__client.list_objects(namespace_name=self.__name_space, bucket_name=self.__b_name, 
                                        start=self.__name_format.format(date=date))
        if resp:
            return len(resp.data.objects) > 0
        else:
            return False

    def store(self, path: Path) -> str:
        name = self.__name_format.format(date=datetime.datetime.now(datetime.timezone.utc))
        with path.open('rb') as input:
            self.__client.put_object(namespace_name=self.__name_space, 
                                     bucket_name=self.__b_name, 
                                     object_name=name,
                                     storage_tier= "InfrequentAccess", 
                                     put_object_body=input.read())
        return name