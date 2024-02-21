# docs_to_JSON

This script is designed to take a given package that has a readthedocs.io API documentation page and parse the API into JSON format.

## Usage

To use the script, run it from the command line with the following syntax:

`python docs_to_json.py <url> [<submodule_1>, ...] [-s | --silent]`

### Example

`python docs_to_json.py https://scanpy.readthedocs.io/en/stable/api.html --silent`

### Arguments

- `<url>`: URL of the module.
  - The URL should be the API page from readthedocs.io of whatever package you are using.
- `[<submodule_1>, ...]`: List of submodules (optional).
- `-s, --silent`: Optional flag to enable silent mode, where logs and error messages for unfound functions are not displayed.

## Dependencies

The script does not use any external Python or shell dependencies.

## Workflow

The script follows this workflow:

1. **Argument Parsing**: Parses command-line arguments to determine the URL, module name, list of submodules, and optional silent mode.
2. **Running `get_functions.sh`**: Executes the `get_functions.sh` shell script to retrieve list of all function information from the specified module and submodules which are linked in the given webpage.
3. **Running `module_to_pydoc.py`**: Executes the `module_to_pydoc.py` Python script to generate documentation for the module based on the extracted function information. The script supports an optional silent mode.
4. **Running `sed` Command**: Executes a `sed` command to remove empty lines from the generated documentation file. This is neccessary for parsing.
5. **Running `api_to_json.py`**: Executes the `api_to_json.py` Python script to convert the documentation file to JSON format.
6. **Cleanup**: Removes temporary files generated during the process, including the function list file and the documentation file.
7. **Completion Message**: Prints a message indicating the completion of the process along with the total execution time.
