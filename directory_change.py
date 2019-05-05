import os


class files(object):
    def __init__(self):
        base_path = os.path.dirname(os.path.realpath(__file__))
        self.main_directory = base_path

    def cd(self, path):
        new_path = '\\' + (path)
        final_path = self.main_directory + new_path
        os.chdir(final_path)
        self.current_directory = final_path

    def file_list(self):
        files = os.listdir(self.current_directory)
        return files
