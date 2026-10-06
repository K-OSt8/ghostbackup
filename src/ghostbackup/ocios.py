# -*- coding: utf-8 -*-
# ocios.py
"""
Copyright (c) 2026 K-OS Christian Keller
All rights reserved.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""
import datetime
import logging
from oci.object_storage import ObjectStorageClient, UploadManager
from oci.config import from_file

from . import LOGGER_NAME


class OSFileArchive:

    def __init__(self, bucket_name, name_space, name_prefix="package", name_postfix=""):
        self.__client = ObjectStorageClient(from_file()) #~/.oci/config
        self.__b_name = bucket_name
        self.__name_space = name_space
        self.__name_format = name_prefix + "-{date}" + name_postfix
        self.__logger = logging.getLogger(LOGGER_NAME)

    def contains(self, date: datetime.datetime):

        """
            API doesn't allow for a search.
            But the Object list is ordered alphanumerically.
            Either go by -start of list -> requires a name and date pattern
            

        """
        if not isinstance(date, datetime.datetime):
            raise TypeError(f"date argument must be a datetime got '{type(date).__name__}'")
        resp = self.__client.list_objects(namespace_name=self.__name_space, bucket_name=self.__b_name, 
                                        start=self.__name_format.format(date=date))
        if resp:
            return len(resp.data.objects) > 0
        else:
            return False

    def store(self, path: str) -> str:
        name = self.__name_format.format(date=datetime.datetime.now(datetime.timezone.utc))
        upload_manager =  UploadManager(
            object_storage_client=self.__client,
            allow_multipart_uploads=True,
            allow_parallel_uploads=True,
        )
        resp = upload_manager.upload_file(
            namespace_name=self.__name_space,
            bucket_name=self.__b_name,
            object_name=name,
            file_path=path,
            storage_tier="InfrequentAccess"
        )
        self.__logger.debug("Stored '%s' with %s", name, resp.status)
        return name