# Property-Based Testing for PickleDB with Hypothesis

This repository contains a Python project for implementing property-based testing on PickleDB using the Hypothesis library. It's part of the course project for University of Waterloo ECE 653 and serves as an example of advanced testing techniques in software engineering.

## Overview

[PickleDB](https://github.com/patx/pickledb) is a lightweight and simple key-value store. It is built upon Python's simplejson module and was designed to be fast and straightforward to use. This project aims to use Hypothesis, a powerful property-based testing framework for Python, to rigorously test PickleDB's functionality and uncover edge cases.

## Getting Started

### Prerequisites

- Python 3.x
- pip (Python package installer)

### Install the required packages

```
pip install -r requirements.txt
```

### Running Tests

To run the tests, use the following command:
```
python -m unittest discover
```

## Contributing

Contributions to this project are welcome. Please adhere to the following guidelines:

- Fork the repository and create a new branch for your feature or fix.
- Write clear and descriptive commit messages.
- Ensure your code adheres to the existing style of the project.
- Create a pull request with a detailed description of your changes.

## License

This project is licensed under the GNU General Public License v3.0
