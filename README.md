# postprocess-sdist-make-rust-ext-opt

[![CI badge](https://github.com/smheidrich/postprocess-sdist-make-rust-ext-opt/actions/workflows/test-build-release.yml/badge.svg)](https://github.com/smheidrich/postprocess-sdist-make-rust-ext-opt/actions/workflows/test-build-release.yml)
[![PyPI package and version badge](https://img.shields.io/pypi/v/postprocess-sdist-make-rust-ext-opt)](https://pypi.org/project/postprocess-sdist-make-rust-ext-opt/)
[![Supported Python versions badge](https://img.shields.io/pypi/pyversions/postprocess-sdist-make-rust-ext-opt)](https://pypi.org/project/postprocess-sdist-make-rust-ext-opt/)

This is a small tool to "post-process" Python source distributions ("sdists")
containing `setuptools-rust`-based Rust extensions so that these extensions
are marked as "optional" (cf. `optional` parameter in the
[`setuptools-rust` API docs](https://setuptools-rust.readthedocs.io/en/latest/reference.html#setuptools_rust.RustExtension)).

In other words, it takes an sdist with a `setup.py` that looks like this

```python3
from setuptools import setup

setup(
    ...
    rust_extensions=[
        RustExtension(...),
    ]
    ...
)
```

and turns it into one that looks like this:

```python3
from setuptools import setup

setup(
    ...
    rust_extensions=[
        RustExtension(..., optional=True),
    ]
    ...
)
```


## What? Why?

**What does it mean for an extension to be optional?**

An extension (Rust or otherwise) being optional means that if the build fails
when installing the package, the installation of the remainder of the package
will proceed anyway and be considered successful. The package can then deal
with the extension's absence at runtime, e.g. by providing pure-Python
fallbacks for its functionality.

**Why set it as optional in a postprocessing step and not from the start?**

Because you'll probably want to build binary packages (wheels) from the project
as well, but if your extension is marked as optional, any errors during their
build will be ignored. So you don't generally want to have it set as optional
when building wheels. It only really makes sense to have it set for the sdist,
nothing else.

**Isn't there a way to do this dynamically without post-processing?**

There is, and in fact that is the [approach recommended by
cibuildwheel](https://cibuildwheel.readthedocs.io/en/stable/faq/#optional-extensions):
You just make the `optional` setting in your `setup.py` dependent on some
environment variable that tells you whether a wheel is being built or not.

I thought about similar approaches before I wrote this utility, but figured
you'd want to keep the number of "dynamic" values in `setup.py` to a minimum so
it will be easy to port it to declarative alternatives like `setup.cfg` or
`pyproject.toml` eventually.
But being able to specify *any* kind of extension (even C ones) declaratively
is [nowhere close to being implemented in setuptools](https://github.com/pypa/setuptools/issues/2220),
and once it is, this tool in its current form won't help you anyway because
it's just `setup.py` focused (although that could be changed then), so, to be
honest, it's not much of an argument.

If I had known about these things or thought them through properly, I probably
wouldn't have written it 🤷

**Back to postprocessing: Why not do it the other way round?**

Another option would be to set the extension as optional from the start but
change it to non-optional before the wheel build. But the issue with that is
that if you're using tools like `setuptools-scm` that automatically determine
your package's version from its state as determined by a version control system
(VCS) like Git, changing anything about the code will cause the version to be
considered "dirty", which will be represented in the version string. A way to
work around this would be to manipulate the VCS history in this case, but that
is even more of a hack than the postprocessing.

**Why not change it prior to building the sdist?**

The same reason as above (dirty repo when building => modified
automatically-determined version).

## Installation

```
pip install postprocess-sdist-make-rust-ext-opt
```

## Usage

```bash
$ postprocess-sdist-make-rust-ext-opt --help
Usage: postprocess-sdist-make-rust-ext-opt [OPTIONS] SDIST_PATHS...

  Post-process a Python sdist to make its Rust extensions optional

Arguments:
  SDIST_PATHS...  path(s) of sdist .tar.gz archive(s) to post-process
                  [required]

Options:
  -O, --output-dir DIRECTORY      directory in which to place the post-
                                  processed archives (default: directory named
                                  'postprocess' in input sdist directory)
  -C, --create-output-dir         whether to create the output directory (and
                                  its parents) if it does not exist
  -f, --force                     whether to overwrite existing files in the
                                  output directory
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.
```

Unless otherwise specified, a processed sdist will be written to a folder named
`postprocessed` in the same directory as the input sdist. Its filename will be
the same as that of the input sdist.

To modify sdists in-place, you can use the combination of options
`-fO dir dir/*.tar.gz`, where `dir` is the directory cotaining the sdists.

## Caveats

The `RustExtension` calls for which the `optional` argument should be set to
`True` *must* be placed directly inside the list that is assigned to the
`rust_extensions` parameter of the top-level `setup()` call like so:

```python3
from setuptools import setup

setup(
    ...
    rust_extensions=[
        RustExtension(...),
    ]
    ...
)
```

Anything more indirect than that, e.g. assigning a `RustExtension` instance to
a variable and then placing that inside the `rust_extensions` list, will cause
the tool to exit with an error.

This is because the transformation is implemented at the syntax tree level and
no static analysis is performed to trace arguments back to their origins.

## Acknowledgements

The transformation is performed using
[RedBaron](https://pypi.org/project/redbaron/)'s full syntax tree (FST)
representation of the sdist's `setup.py`.
