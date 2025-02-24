
# SHD-SpectreDemo

This repo provides a Visualized Simulator to demonstrate Spectre Attack on out-of-order processors.
We also implement 2 Spectre defenses, InvisiSpec and GhostMinion, and guide you to discover new Spectre variants to break them.


## Run the Repo on Binder

Run this repo in Jupyter Notebook with [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/yuhengy/SHD-SpectreDemo/HEAD?urlpath=%2Fdoc%2Ftree%2F2-attackProcessors.ipynb)


## Run the Repo locally

- `pipenv lock && pipenv sync`: Setup python environment with 
- `pipenv shell`: Activate the environment with 
- `jupyter notebook 2-attacks.ipynb`: Open Jupyter Notebook with 
- After you are done, remove the environment with `pipenv --rm`

