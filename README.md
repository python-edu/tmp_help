# Additional setup

- Set up the `history_to_md()` function in IPython.
- Download the `crypto_edu` wheel file (`.whl`).

---

# IPython

## Setup

1. Download `history_to_md.py` and save it in `~/Downloads/`.
2. Activate a virtual environment with IPython installed.
3. Locate the IPython directory and the default profile directory. Run the following commands in the terminal (Linux, macOS or Windows):

    ```bash
    ipython locate
    ipython locate profile
    ```

    The default profile directory is usually `~/.ipython/profile_default/`.

4. If the profile directory or its `startup` subdirectory does not exist, create the default profile:

    ```bash
    ipython profile create
    ```

    Check its location again:

    ```bash
    ipython locate profile
    ```

5. Copy `history_to_md.py` to the `startup` subdirectory of the profile. Use the same command on Linux, macOS and Windows (PowerShell):

    ```bash
    cp ~/Downloads/history_to_md.py "$(ipython locate profile)/startup/"
    ```

6. Start IPython and check that the function is available:

    ```bash
    ipython
    ```

    In IPython:

    ```ipython
    history_to_md?
    ```

IPython automatically loads Python files from the profile's `startup` directory. By default, all virtual environments use the same user profile. This setup is required only once per user account, not once per virtual environment.

[IPython documentation – Configuration and startup files](https://ipython.readthedocs.io/en/stable/config/intro.html)

## Usage

Save the selected history entries with expression outputs to a text file:

```ipython
%history -o -f answers.txt 10-25
```

Convert the text file to Markdown:

```python
history_to_md('answers.txt')
```

The function creates `answers.md` in the same directory. It overwrites an existing Markdown file and leaves the original text file unchanged.

- Use `#`, `##`, `###`, etc., followed by a space, at the beginning of a line to create Markdown headings.
- Output from `print()` is not included in the exported history.

---

# crypto_edu

- Download the `crypto_edu` wheel file (`.whl`).
- Install it using `pip` during class, following the instructor's instructions.
