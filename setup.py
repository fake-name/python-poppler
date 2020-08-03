import os
import re
import sys
import shutil
from pathlib import Path
import platform
import subprocess

from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
from distutils.version import LooseVersion

exec(Path("src/poppler/_version.py").read_text())


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(["cmake", "--version"])
        except OSError:
            raise RuntimeError(
                "CMake must be installed to build the following extensions: "
                + ", ".join(e.name for e in self.extensions)
            )

        if platform.system() == "Windows":
            cmake_version = LooseVersion(
                re.search(r"version\s*([\d.]+)", out.decode()).group(1)
            )
            if cmake_version < "3.1.0":
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = [
            "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=" + extdir,
            "-DPYTHON_EXECUTABLE=" + sys.executable,
        ]

        cfg = "Debug" if self.debug else "Release"
        build_args = ["--config", cfg]

        if platform.system() == "Windows":
            cmake_args += [
                "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}".format(cfg.upper(), extdir)
            ]
            if sys.maxsize > 2 ** 32:
                cmake_args += ["-A", "x64"]
            build_args += ["--", "/m"]
        else:
            cmake_args += ["-DCMAKE_BUILD_TYPE=" + cfg]
            build_args += ["--", "-j2"]

        env = os.environ.copy()
        env["CXXFLAGS"] = '{} -DVERSION_INFO=\\"{}\\"'.format(
            env.get("CXXFLAGS", ""), self.distribution.get_version()
        )
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call(
            ["cmake", ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env
        )
        subprocess.check_call(
            ["cmake", "--build", "."] + build_args, cwd=self.build_temp
        )


binary_deps = []

# These are pulled from conda-forge
# Conda seems to split up dependencies everywhere, which is annoying.
# poppler needs DLLs from following packages to work:
#   - poppler
#   - libiconv
#   - freetype
#   - zlib
#   - libcurl
#   - openjpeg
#   - libpng
#   - libtiff
#   - libssh2
#   - zstd
#   - xz
#   - openssl
binary_search_paths = [
    'C:\\code\\lib\\poppler-0.90.1-h5d62644_0\\Library\\bin',
    'C:\\code\\lib\\libiconv-1.15-h0c8e037_1006\\Library\\bin',
    'C:\\code\\lib\\freetype-2.10.2-hd328e21_0\\Library\\bin',
    'C:\\code\\lib\\zlib-1.2.11-h3cc03e0_1006\\Library\\bin',
    'C:\\code\\lib\\libcurl-7.71.1-h4b64cdc_4\\Library\\bin',
    'C:\\code\\lib\\openjpeg-2.3.1-h57dd2e7_3\\Library\\bin',
    'C:\\code\\lib\\libpng-1.6.37-hfe6a214_1\\Library\\bin',
    'C:\\code\\lib\\libtiff-4.1.0-h885aae3_6\\Library\\bin',
    'C:\\code\\lib\\libssh2-1.9.0-hb06d900_5\\Library\\bin',
    'C:\\code\\lib\\zstd-1.4.5-h1f3a1b7_2\\Library\\bin',
    'C:\\code\\lib\\xz-5.2.5-h62dcd97_1\\Library\\bin',
    'C:\\code\\lib\\openssl-1.1.1g-he774522_1\\Library\\bin',
]


def locate_dll(dll_name):
    '''
    Locate a dll `dll_name` in the available `binary_search_paths`, and
    return a relative path to the target DLL from the current working directory.

    A dll not being found will raise an exception.
    '''
    for spath in binary_search_paths:
        files = os.listdir(spath)
        if dll_name in files:
            return os.path.relpath(os.path.join(spath, dll_name))

    raise IOError("Could not find required DLL '%s'" % (dll_name))

def locate_rename_file(old_name, new_name):
    '''
    Locate a dll `dll_name` in the available `binary_search_paths`, and
    copy it to the same directory as `new_name`.

    A dll not being found will raise an exception.
    '''

    for spath in binary_search_paths:
        files = os.listdir(spath)
        if old_name in files:
            if os.path.exists(os.path.join(spath, new_name)):
                return
            shutil.copy(os.path.join(spath, old_name), os.path.join(spath, new_name))
            return

    raise IOError("Could not find required DLL to copy '%s'" % (dll_name))


if sys.platform == "win32":

    # I haven't tracked down why this is distributed as "libiconv.dll", but
    # linked as "iconv.dll". Anyways, make a copy of it with the name we expect.
    # This requires the lcoation where the DLL is located to be writable
    locate_rename_file("libiconv.dll", "iconv.dll")

    binary_deps.append(('poppler/cpp', [
        locate_dll('poppler-cpp.dll'),
        locate_dll('poppler.dll'),
        locate_dll('iconv.dll'),
        locate_dll('libcharset.dll'),
        locate_dll('freetype.dll'),
        locate_dll('zlib.dll'),
        locate_dll('libcurl.dll'),
        locate_dll('openjp2.dll'),
        locate_dll('libpng16.dll'),
        locate_dll('tiff.dll'),
        locate_dll('libssh2.dll'),
        locate_dll('liblzma.dll'),
        locate_dll('zstd.dll'),
        locate_dll('libcrypto-1_1-x64.dll'),
        ]))
    print("Binary deps: ", binary_deps)


setup(
    name="python-poppler",
    version=__version__,  # noqa
    author=__author__,  # noqa
    author_email="charles@cbrunet.net",
    url="https://github.com/cbrunet/python-poppler",
    description="A Python binding to poppler-cpp",
    long_description=(Path(__file__).parent / "README.md").read_text(),
    long_description_content_type="text/markdown",
    license="GPLv2",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    # keywords
    project_urls={
        "Source": "https://github.com/cbrunet/python-poppler",
        "Tracker": "https://github.com/cbrunet/python-poppler/issues",
    },
    python_requires=">=3.7",
    packages=find_packages("src"),
    package_dir={
            "": "src",
        },
    data_files=binary_deps,
    include_package_data=True,
    ext_modules=[CMakeExtension("poppler.cpp.modules")],
    cmdclass=dict(build_ext=CMakeBuild),
    zip_safe=False,
)
