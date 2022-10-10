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
