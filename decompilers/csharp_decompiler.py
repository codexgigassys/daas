# This class was created just to add custom logic to the CSharp decompiler,
# but you don't need to create a class for each SubprocessBasedDecompiler.
# In fact, most of the time you will not need to create a class for such decompilers.
# If you want to check how CSharp decompiler worked without a custom class,
# check on Github any commit previous to March 27th, 2019.
import os
from typing import List

from .decompiler import SubprocessBasedDecompiler


class CSharpDecompiler(SubprocessBasedDecompiler):
    def clean_decompiled_content(self) -> None:
        """ Cleans the content to avoid misleading stuff in decompiled source code files.
            There is no need to return anything because the source code files themselves will be modified. """
        for file_path in self.get_file_paths_recursive():
            content = self.get_clean_content(file_path)
            self.overwrite_content(file_path, content)

    def get_clean_content(self, file_path: str) -> bytes:
        with open(file_path, 'rb') as file:
            content = file.read()
            # As I compiled the open source version of "Just Decompile" decompiler, my name appears on some files
            # when an error occurs, and that could lead to confusion.
            for name in [b'lucesposito', b'lucasesposito']:
                content = content.replace(name, b'daas_generic_username')
        return content

    def overwrite_content(self, file_path: str, content: bytes) -> None:
        with open(file_path, 'wb') as file:
            file.write(content)

    def get_file_paths_recursive(self) -> List[str]:
        paths = []
        for path, _, files in os.walk(self.get_tmpfs_folder_path()):
            for file_name in files:
                paths.append(os.path.join(path, file_name))
        return paths
