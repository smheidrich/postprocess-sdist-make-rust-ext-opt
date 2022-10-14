import subprocess as sp
import tarfile
from shutil import copytree

import pytest

from postprocess_sdist_make_rust_ext_opt import (
    one,
    postprocess_sdist,
    set_optional_true,
)


@pytest.mark.parametrize(
    "setup_py_filename",
    [
        "setup_without_rust_ext_optional_arg.py",
        "setup_with_rust_ext_optional_false.py",
        "setup_with_rust_ext_optional_true.py",
    ],
)
def test_set_optional_true(setup_py_filename, datafix_read):
    setup_py_str = datafix_read(setup_py_filename)
    expected_setup_py_str = datafix_read(
        "expected_setup_after_postprocessing.py"
    )

    post_processed = set_optional_true(setup_py_str)

    assert post_processed == expected_setup_py_str


@pytest.fixture
def dummy_sdist_archive(datafix_dir, tmp_path):
    pkg_path = tmp_path / "mypkg"
    copytree(datafix_dir / "mypkg", pkg_path)
    sp.run(["python", "setup.py", "sdist"], check=True, cwd=pkg_path)
    return one(pkg_path.glob("dist/*.tar.gz"))


def compare_sdists(sdist1, sdist2, ignore_filenames=None):
    ignore_filenames = (
        set(ignore_filenames) if ignore_filenames is not None else {}
    )
    with tarfile.open(sdist1, "r:gz") as tar_file1, tarfile.open(
        sdist2, "r:gz"
    ) as tar_file2:
        member_names1 = set(tar_file1.getnames())
        member_names2 = set(tar_file2.getnames())
        assert (
            member_names1 == member_names2
        ), member_names1.symmetric_difference(member_names2)
        for member_name in member_names1:
            if any(
                ignored_filename in member_name
                for ignored_filename in ignore_filenames
            ):
                continue
            f1 = tar_file1.extractfile(member_name)
            f2 = tar_file2.extractfile(member_name)
            assert (f1 is None and f2 is None) or (
                f1.read() == f2.read()
            ), member_name


def test_postprocess_sdist(dummy_sdist_archive):
    postprocess_sdist(dummy_sdist_archive.absolute(), create_output_dir=True)
    postprocessed_sdist_path = (
        dummy_sdist_archive.parent / "postprocessed" / dummy_sdist_archive.name
    )
    # check that everything is the same except setup.py
    compare_sdists(
        dummy_sdist_archive,
        postprocessed_sdist_path,
        ignore_filenames=["setup.py"],
    )
    # check post-processed setup.py
    with tarfile.open(postprocessed_sdist_path, "r:gz") as tar_file:
        for member_name in tar_file.getnames():
            if "setup.py" in member_name:
                content = tar_file.extractfile(member_name).read()
    assert b"optional=True" in content
