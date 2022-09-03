# Contributing to Textual Inputs

First, thank you for taking time to contribute to open source and to this project! Here's how contributing to this project works.

## Git Workflow

1. Fork the repo and create your own branch from `main`. The branch should be named after the type of issue your are solving.

```
feat/[summary-with-dashes] (this one covers anything you can't fit in the other categories)
fix/[summary-with-dashes]
docs/[summary-with-dashes]
```

2. Setup your local development environment. Texutal Inputs currently supports CPython 3.7 - 3.10. Please test your additions with at least the Python versions at the ends of that range.

bash/zsh/sh
```bash
python3.7 -m venv venv7
source venv7/bin/activate
python -m pip install -r requirements-dev.txt
python -m pip install -e .
deactivate

python3.10 -m venv venv10
source venv10/bin/activate
python -m pip install -r requirements-dev.txt
python -m pip install -e .
pre-commit install
```

pwsh
```powershell
py -3.7 -m venv venv7
venv10/Scripts/activate
python -m pip install -r requirements-dev.txt
python -m pip install -e .
deactivate

py -3.10 -m venv venv10
venv7/Scripts/activate
python -m pip install -r requirements-dev.txt
python -m pip install -e .
pre-commit install
```

3. Make your updates, including updating the documentation if necessary.
5. Ensure your code passes our linting and formatting checks. This project uses [pre-commit](https://pre-commit.com/) to help manage code quality. It will run on `git commit`. You can also run it manually.

```bash
pre-commit run -a
```

6. Start your commit message with a similar format to the branch.

```
# Branch
feat/add-integer-widget

# Commit
feat: add integer widget

- list of changes
- contained in this commit

```

7. Create a pull request and add `sirfuzzalot` as the reviewer.
8. We'll got through a review of the code, work through any challenges we hit and then merge it in.

## Package Versioning

Version bumps will occur as separate pull requests and releases will get tagged on those commits. Please do not submit a version bump PR. Thanks!

## Contributions and Licensing

All contributions you make to this project will be licensed under the [MIT License](http://choosealicense.com/licenses/mit/).
