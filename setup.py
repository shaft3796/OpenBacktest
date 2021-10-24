import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="open-backtest",
    version="4.0.3",
    author="Shaft3796",
    author_email="sh4ft.me@gmail.com",
    description="Open Backtest is a beginner friendly & powerful backtesting engine for crypto trading",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Shaft-3796/OpenBacktest",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
