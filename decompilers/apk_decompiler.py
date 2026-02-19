import os
import subprocess
import logging
import shutil
from zipfile import BadZipFile

from .decompiler import SubprocessBasedDecompiler
from .utils import unzip_into, remove
from .utils_apk import apk_to_jar, jar_to_java, merge_folders
from .exceptions import CantDecompileJavaException, CorruptAPKException


class APKDecompiler(SubprocessBasedDecompiler):
    def __init__(self, *args, **kwargs):
        self.directories_to_remove_before_zipping = []
        self.files_to_remove_before_zipping = []
        super().__init__(*args, **kwargs)

    def decompile(self):
        result = b''
        # Step 1: Unzip APK
        self.unzip()
        # Step 2A: *.apk -> *.jar, *.jar -> multiple *.java
        source_code_obtained, output = self.apk_to_java_files()
        result += (output + b'\n'*10)
        # Step 2B:
        apktool_succedded, output = self.decompile_with_apktools()
        result += output
        self.process_clean()
        return result

    @property
    def classes_dex_found(self):
        logging.error('self.get_tmpfs_folder_path()')
        logging.error(self.get_tmpfs_folder_path())
        return 'classes.dex' in os.listdir(self.get_tmpfs_folder_path())

    def unzip(self):
        try:
            unzip_into(zip_file_path=self.get_tmpfs_file_path(), extraction_path=self.get_tmpfs_folder_path())
        except BadZipFile:
            logging.error('[APK] File is corrupt (BadZipFile). Marking as failed.')
            raise CorruptAPKException("APK file is corrupt and cannot be extracted as ZIP")

    def apk_to_java_files(self):
        decompiled = False
        apk_to_jar_output = b'Empty output placeholder'
        jar_to_java_output = b'Empty output placeholder'
        logging.error(f'self.classes_dex_found={self.classes_dex_found}')
        if self.classes_dex_found:
            try:
                java_base_path = f'{self.get_tmpfs_folder_path()}/source_code/'
                os.mkdir(java_base_path)
                self.directories_to_remove_before_zipping.append(java_base_path)
                jar_path, apk_to_jar_output = apk_to_jar(self.get_tmpfs_file_path())
                jar_to_java_output = jar_to_java(jar_path, java_base_path)
                decompiled = True
                remove(jar_path)
            except CantDecompileJavaException:
                logging.error('[apk -> jar] Known error of dex2jar. Marking file as not decompilable.')
            except Exception as e:
                logging.error('apk -> jar or jar -> java error.')
                logging.exception(e)
        output = b'APK TO JAR OUTPUT:\n' + apk_to_jar_output + b'\n'*10 + b'JAR TO JAVA OUTPUT:\n' + jar_to_java_output
        return decompiled, output

    def decompile_with_apktools(self):
        decompiled = False
        apktools_dirirectory = '/tmpfs/apktools'
        output = b'Empty output placeholder'
        self.directories_to_remove_before_zipping.append(apktools_dirirectory)
        try:
            output = subprocess.check_output(["apktool", "d", self.get_tmpfs_file_path(), "-s", "-f", "-o", apktools_dirirectory])
            merge_folders(source_directory=apktools_dirirectory, destination_directory=self.get_tmpfs_folder_path())
            decompiled = True
        except Exception as e:
            logging.error(e)
        return decompiled, b'APKTOOL OUTPUT:\n' + output
