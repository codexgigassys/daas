# This class was created just to add custom logic to the CSharp decompiler,
# but you don't need to create a class for each SubprocessBasedDecompiler.
# In fact, most of the time you will not need to create a class for such decompilers.
# If you want to check how CSharp decompiler worked without a custom class,
# check on Github any commit previous to March 27th, 2019.
from .decompiler import SubprocessBasedDecompiler


class CSharpDecompiler(SubprocessBasedDecompiler):
    def clean_decompiled_content(self):
        for path in get_file_paths_recursive(self.get_tmpfs_folder_path()):
            file = open(path, 'r')
            content = file.read()
            # As I compiled the open source version of "Just Decompile" decompiler, my name appears on some files
            # when an error occurs, and that could lead to confusion.
            for name in ['lucesposito', 'lucasesposito']:
                content = content.replace(name, 'daas_generic_username')
            file.close()
            file.open(path, 'w')
            file.write(content)
            file.close()

    def get_file_paths_recursive(self, base_path):
        paths = []
        for path, subdirs, files in os.walk(base_path):
            for name in files:
                paths.append(os.path.join(path, name))
        return paths
