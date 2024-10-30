from setuptools import setup, find_packages

setup(
    name="clinica_veterinaria", 
    version="0.1",  
    description="Sistema de gestión para una clínica veterinaria",
    author="Miguel,Laura,Beatriz,Pablo",
    packages=find_packages(),  # Encuentra automáticamente todas las carpetas con un __init__.py
    include_package_data=True,  # Incluye archivos indicados en MANIFEST.in, si es necesario
    install_requires=[
        # Lista de dependencias. Ejemplo:
        # "pandas>=1.0",
        # "numpy>=1.18",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Cambia esto si usas otra licencia
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Versión mínima de Python
)
