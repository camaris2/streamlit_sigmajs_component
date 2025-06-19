# Streamlit Sigma.js Component

A streamlit component to visualize network graph data.

Combines Python, Streamlit, Vue3 and Sigma.js.

## Key Features

- Visualize network data
- Interact with the graph
- Display additional nodes & edges attributes

(screenshot)

# Installation

## pip installation

pip install streamlit-sigmajs-component

## manual installation from source

Create and activate a python virtual environment (venv, conda, ...)

Clone this repository

```bash
git clone https://github.com/camaris2/streamlit_sigmajs_component.git
```

Navigate to root directory

```bash
cd streamlit_sigmajs_component
```

Install the package in editable mode:

```bash
pip install -e .
```

# Using the component

In your streamlit app:
- import the module: 

> from vsigma_component import vsigma_component

- call the component

> graph_state = vsigma_component(my_nodes, my_edges, my_settings, key="vsigma")

- (optional) use the data returned via the graph state object (e.g. selected node or edge, ...) 

## Run Example App

- create the environment
    - pip install virtualenv (if you don't already have virtualenv installed)
    - virtualenv venv to create your new environment (called 'venv' here)
    - source venv/bin/activate to enter the virtual environment (unix)
    - venv/bin/activate to enter the virtual environment (windows)

pip install -r requirements.txt to install the requirements in the current environment
- run the streamlit example app:

```bash
cd streamlit_sigmajs_component/vsigma_component
streamlit run example.py
```

# Development

- Ensure you have Python 3.7+, Node.js, and npm installed.

## Clone project

- Clone this repository : git clone https://github.com/camaris2/streamlit_sigmajs_component.git
- Navigate to root directory

## Python Setup

Create and activate a virtual environment, then install the package in editable mode:

```bash
python3 -m venv venv # On Windows use python -m venv venv
source ./venv/bin/activate # On Windows use `.\venv\Scripts\activate`
pip install -e .
```

## Node Setup

Navigate to the frontend directory and install the necessary npm packages:

```bash
cd vsigma_component/vue_sigma
npm install
```

## Running the App (in development mode)

Change PRODUCTION flag in vsigma_component/__init__.py to False

- In one terminal start the frontend dev server

```bash
cd vsigma_component/vue_sigma
npm run dev
```

- In another terminal run the streamlit server

```bash
source ./venv/bin/activate  # Unix
.\venv\Scripts\activate  # Windows
cd vsigma_component
streamlit run example.py
```

# Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

# License

This project is licensed under the MIT License. See the LICENSE file for details.

# Acknowledgments

- [Sigma.js](https://www.sigmajs.org/)
- [Streamlit](https://www.streamlit.io/)
- [Vue3](https://vuejs.org/)
- [Python](https://www.python.org/)