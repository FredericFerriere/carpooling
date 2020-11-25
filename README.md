# covoiturage

Packages

Virtual environment
conda config --prepend channels conda-forge
conda create -n covoiturage --strict-channel-priority osmnx jupyterlab
conda activate covoiturage
python -m ipykernel install --user --name covoiturage
jupyter lab

conda install geopy
conda install -c conda-forge aiohttp

http://project-osrm.org/docs/v5.23.0/api/#general-options
