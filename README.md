# Fake but Realistic Data

`data-generator-cli` is a tool for generating realistic random data for entity-relationship designs, considering:

-   Participation constraints
-   Join selectivity
-   Probability distributions

## Set up & Quick Start

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

6. **Run the CLI** by running:

    ```bash
    python main.py main.py -i input/sample.json -o output
    ```

    This command will generate data based on the input file `input/sample.json` and output the generated data to the `output` directory.

    You can refer to our [User Guide](document/UserGuide.md) for more information on how to use the CLI.

You can deactivate the virtual environment to return to your global Python environment by running:

```bash
deactivate
```

## Developer Guide

For more information on how to contribute to this project, please refer to our [Developer Guide](document/DeveloperGuide.md).

You can find a detailed project [paper](document/ProjectPaper.pdf) in the document folder. Along with a [video](document/video.mp4) introducing the project.

## Credits

This is a group project for CS4221, done by Team 22.

Team Members:

-   Neo Jing Xuan
-   Ren Weilin
-   Ryan Cheung
-   Zhang Shilin
-   Winston Cahya

Speical thanks to Professor Stephane Bressan for teaching the module and our mentor Mehdi Yaminli for guiding us throughout the project.
