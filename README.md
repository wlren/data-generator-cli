# Fake but Realistic Data

This is a group project for CS4221, done by Team 22.

`data-generator-cli` is a tool for generating realistic random data for entity-relationship designs, considering:

-   Participation constraints
-   Join selectivity
-   Probability distributions

Starting a new Python project involves setting up your environment and importing the necessary libraries to your project. Below is a step-by-step guide to get you started:

## Set up

1. **Clone the repository** to your local machine, ensure you have `Python 3` and `pip`` installed.

2. **Navigate to your project directory** in the terminal or command prompt.

3. **Create a virtual environment** by running:

    ```bash
    python -m venv venv
    ```

4. **Activate the virtual environment**:

    - On **Windows**, run:
        ```cmd
        .\venv\Scripts\activate
        ```
    - On **macOS and Linux**, run:
        ```bash
        source venv/bin/activate
        ```

5. **To install from `requirements.txt`** run:
    ```bash
    pip install -r requirements.txt
    ```

You can deactivate the virtual environment to return to your global Python environment by running:

```bash
deactivate
```
