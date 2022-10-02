import os
from config.conf import ConfigFile


class Converter:
    def __init__(self, book_id, src_file_path):
        self.book_id = book_id
        self.src_file_path = src_file_path

        filename_with_ext = os.path.basename(src_file_path)
        self.file_name, self.file_extension = os.path.splitext(filename_with_ext)
        self.file_extension = self.file_extension.lower()

    def convert(self):
        convert_funcs = {
            "epub": self._convert_to_pdf,
            "word": self._convert_to_pdf,
            "html": self._convert_to_txt,
            "xhtml": self._convert_to_txt,
            "txt": self._convert_to_txt,
        }

        if self.file_extension == "pdf":
            return True, self.src_file_path

        if self.file_extension not in convert_funcs:
            return False, ""

        return convert_funcs[self.file_extension]()

    def _get_pdf_file_path(self):
        return "{0}/{1}/tmp/{2}.pdf".format(ConfigFile.get_storage_address(), self.book_id, self.file_name)

    def _get_txt_file_path(self):
        return "{0}/{1}/tmp/{2}.txt".format(ConfigFile.get_storage_address(), self.book_id, self.file_name)

    def _convert_to_pdf(self):
        pdf_file_path = self._get_pdf_file_path()
        cmd = "ebook-convert '{0}' '{1}'".format(self.src_file_path, pdf_file_path)
        cmd_ret = os.system(cmd)
        return cmd_ret == 0, pdf_file_path

    def _convert_to_txt(self):
        txt_file_path = self._get_txt_file_path()
        cmd = "ebook-convert '{0}' '{1}'".format(self.src_file_path, txt_file_path)
        cmd_ret = os.system(cmd)
        return cmd_ret == 0, txt_file_path


