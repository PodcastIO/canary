import os
import platform
import shutil
import subprocess

from PIL import Image

from podcast.pkg.errors.biz_error import CommandTimeout, PDFSyntaxError
from podcast.pkg.utils.uuid import get_uuid
import podcast.pkg.client.log as logging


class Command:
    TIMEOUT = 30 * 60

    def __init__(self, args, env=None, strict=False):
        self.args = args
        self.strict = strict

        self.env = env
        if self.env is None:
            self.env = os.environ.copy()

    def run(self):
        startupinfo = None

        if platform.system() == 'Windows':
            # this startupinfo structure prevents a console window from popping up on Windows
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        proc = subprocess.Popen(self.args, env=self.env, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, startupinfo=startupinfo)
        try:
            data, err = proc.communicate(timeout=self.TIMEOUT)
        except subprocess.TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()
            logging.error(errs)
            raise CommandTimeout()

        if b"Syntax Error" in err and self.strict:
            raise PDFSyntaxError(err.decode("utf8", "ignore"))


class PDF2ImageCommand:
    def __init__(self, filepath, page_no=None, strict=False, poppler_path=None):
        self.filepath = filepath
        self.page_no = page_no
        self.output_dir = "/tmp/{0}".format(get_uuid())
        self.poppler_path = poppler_path
        self.strict = strict

    @classmethod
    def _get_command_path(cls, command, poppler_path=None):
        if platform.system() == "Windows":
            command = command + ".exe"

        if poppler_path is not None:
            command = os.path.join(poppler_path, command)

        return command

    @classmethod
    def _load_from_output_folder(cls, output_folder, output_file, ext):
        images = []
        for f in sorted(os.listdir(output_folder)):
            if f.startswith(output_file) and f.split(".")[-1] == ext:
                images.append(Image.open(os.path.join(output_folder, f)))
        return images

    def run(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        outfile = get_uuid()
        if self.page_no is not None:
            args = [self._get_command_path("pdfimages", self.poppler_path), "-l", "{0}".format(self.page_no),
                    self.filepath, "{0}/{1}".format(self.output_dir, outfile)]
        else:
            args = [self._get_command_path("pdfimages", self.poppler_path), self.filepath, self.output_dir]

        env = os.environ.copy()
        if self.poppler_path is not None:
            env["LD_LIBRARY_PATH"] = self.poppler_path + ":" + env.get("LD_LIBRARY_PATH", "")

        Command(args, env).run()

        images = self._load_from_output_folder(self.output_dir, outfile, "ppm")

        shutil.rmtree(self.output_dir)
        return images


class EBookConvertFile2PDFCommand:
    def __init__(self, input_file_path: str):
        self.input_file_path = input_file_path
        self.output_dir = "/tmp/{0}".format(get_uuid())
        self.output_file_path = "{0}/{1}.pdf".format(self.output_dir, get_uuid())

    def run(self) -> str:
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        args = ["ebook-convert", self.input_file_path, self.output_file_path]
        Command(args).run()
        return self.output_file_path


class EBookConvertBuffer2PDFCommand(EBookConvertFile2PDFCommand):
    def __init__(self, filename: str, content: bytes):
        _, name = os.path.split(filename)
        EBookConvertFile2PDFCommand.__init__(self, "/tmp/{0}_{1}".format(get_uuid(), name))

        with open(self.input_file_path, "wb") as f:
            f.write(content)