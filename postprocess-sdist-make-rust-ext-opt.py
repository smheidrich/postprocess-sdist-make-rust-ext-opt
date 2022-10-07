import tarfile
from pathlib import Path
from tempfile import TemporaryDirectory

import typer
from redbaron import RedBaron

app = typer.Typer()


def one(iterable):
    iterator = iter(iterable)
    x = next(iterator)
    ok = False
    try:
        next(iterator)
    except StopIteration:
        ok = True
    if not ok:
        raise ValueError("more than one element")
    return x


@app.command()
def postprocess(
    sdist_path: str = typer.Argument(
        "path of the sdist .tar.gz archive to post-process"
    ),
):
    sdist_path = Path(sdist_path)
    output_sdist_path = sdist_path.parent / "postprocessed" / sdist_path.name
    with TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        with tarfile.open(sdist_path, "r:gz") as tar_file:
            tar_file.extractall(tmpdir_path)
        main_folder_path = one(tmpdir_path.iterdir())
        setup_py_path = main_folder_path / "setup.py"
        setup_py_path.write_text(set_optional_true(setup_py_path.read_text()))
        output_sdist_path.parent.mkdir(exist_ok=True)
        with tarfile.open(output_sdist_path, "w:gz") as tar_file:
            for path in tmpdir_path.iterdir():
                tar_file.add(path, arcname=str(path.relative_to(tmpdir_path)))


def set_optional_true(setup_py_str: str) -> str:
    rb = RedBaron(setup_py_str)
    setup_call_node = rb.find(
        "atomtrailers",
        value=lambda value: len(value) == 2
        and value[0].type == "name"
        and value[0].value == "setup"
        and value[1].type == "call",
        recursive=False,
    ).value[1]
    rust_extensions_argument_node = setup_call_node.value.find(
        "call_argument",
        target=lambda target: target is not None
        and target.type == "name"
        and target.value == "rust_extensions",
        recursive=False,
    )
    rust_extensions_list_node = rust_extensions_argument_node.value
    assert rust_extensions_list_node.type in ("list", "tuple")
    for rust_extension_entry_node in rust_extensions_list_node.value:
        assert rust_extension_entry_node.type == "atomtrailers"
        assert rust_extension_entry_node.value[0].type == "name"
        assert rust_extension_entry_node.value[0].value == "RustExtension"
        rust_extension_call_node = rust_extension_entry_node.value[1]
        assert rust_extension_call_node.type == "call"
        optional_arg_node = rust_extension_call_node.value.find(
            "call_argument",
            target=lambda target: target is not None
            and target.type == "name"
            and target.value == "optional",
            recursive=False,
        )
        if optional_arg_node is None:
            rust_extension_call_node.value.append("optional=True")
        else:
            optional_arg_node.value.value = "True"
    return rb.dumps()


if __name__ == "__main__":
    app()
