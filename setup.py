from setuptools import find_packages, setup

setup(
    name="Example Robot",
    version="0.1.0",
    description="Basic example robot using TimedRobot.",
    url="https://github.com/ChaseYalon/example_robot",
    packages=find_packages(),
    install_requires=[
        'lemonlib @ git+https://github.com/FRC5113/LemonLib.git',
        'smartunits @ git+https://github.com/Mythilllian/SmartUnits.git',
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
    ],
    extras_require={
        'test': ['pytest'],
    }
)
