from pathlib import Path

import setuptools

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="streamlit-sigmajs-component",
    version="1.0.3",
    author="camaris",
    author_email="streamlit@camaris.be",
    description="Streamlit component to visualize network graph data using Sigma.js.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={
        "vsigma_component.vue_sigma": ["dist/**/*"],
    },
    classifiers=[],
    python_requires=">=3.7",
    install_requires=[
        "streamlit >= 0.63",
    ],
)
