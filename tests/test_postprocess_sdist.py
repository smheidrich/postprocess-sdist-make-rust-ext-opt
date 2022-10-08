import pytest

from postprocess_sdist_make_rust_ext_opt import set_optional_true

setup_py_without_rust_ext_optional_arg = """\
from setuptools import setup
from setuptools_rust import Binding, RustExtension
setup(
    name="mypkg",
    version="0.1.0",
    rust_extensions=[
        RustExtension(
            "mypkg.mypkg_rs",
            binding=Binding.PyO3,
        )
    ],
    packages=["mypkg"],
    zip_safe=False,
)
"""

setup_py_with_rust_ext_optional_false = """\
from setuptools import setup
from setuptools_rust import Binding, RustExtension
setup(
    name="mypkg",
    version="0.1.0",
    rust_extensions=[
        RustExtension(
            "mypkg.mypkg_rs",
            binding=Binding.PyO3,
            optional=False,
        )
    ],
    packages=["mypkg"],
    zip_safe=False,
)
"""

expected_setup_py_after_postprocessing = """\
from setuptools import setup
from setuptools_rust import Binding, RustExtension
setup(
    name="mypkg",
    version="0.1.0",
    rust_extensions=[
        RustExtension(
            "mypkg.mypkg_rs",
            binding=Binding.PyO3,
            optional=True,
        )
    ],
    packages=["mypkg"],
    zip_safe=False,
)
"""


@pytest.mark.parametrize(
    "setup_py_str",
    [
        setup_py_without_rust_ext_optional_arg,
        setup_py_with_rust_ext_optional_false,
    ],
)
def test_set_optional_true(setup_py_str):
    post_processed = set_optional_true(setup_py_str)
    assert post_processed == expected_setup_py_after_postprocessing
