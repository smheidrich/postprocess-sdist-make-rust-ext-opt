import pytest

from postprocess_sdist_make_rust_ext_opt import set_optional_true


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
