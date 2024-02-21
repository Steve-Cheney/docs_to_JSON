import subprocess
import time
import argparse
import re

def extract_module_from_domain(url):
    # Define a regular expression pattern to match the domain
    pattern = r"https://([^\.]+)\."

    # Use re.search() to find the first occurrence of the pattern
    match = re.search(pattern, url)

    if match:
        # Extract the matched domain from the URL
        domain = match.group(1)
        return domain
    else:
        return None


def main():
    pydoc_file_path = "pydoc_file.txt"
    functions_file_path = "list_of_functions.txt"
    
    start_time = time.perf_counter()

    # Argument parsing
    parser = argparse.ArgumentParser(description="Run scripts with optional silent mode.")
    parser.add_argument('url', help='URL of the module')
    parser.add_argument('submodules', nargs='*', help='List of explicit submodules')
    parser.add_argument('-s', '--silent', action='store_true', help='Silent mode')
    args = parser.parse_args()

    url = args.url
    module = extract_module_from_domain(url)
    submodules = args.submodules

    # Run get_functions.sh
    subprocess.run(["bash", "get_functions.sh"] + [functions_file_path, url] + submodules)

    # Run module_to_pydoc.py
    module_to_pydoc_command = ["python", "module_to_pydoc.py"]
    if args.silent:
        module_to_pydoc_command.append("-s")  # Append the silent option
    module_to_pydoc_command.extend([functions_file_path, pydoc_file_path, module])
    subprocess.run(module_to_pydoc_command)

    
    subprocess.run(["bash", "-c", "sed -i '/^[[:space:]]*$/d' " + pydoc_file_path])

    # Run api_to_json.py
    api_to_json_command = ["python", "api_to_json.py", pydoc_file_path, f"{module}_api.json"]
    subprocess.run(api_to_json_command, check=True)

    subprocess.run(["bash", "-c", f"rm {functions_file_path} {pydoc_file_path}"])
    
    end_time = time.perf_counter()
    print(f"Process completed in {round(end_time - start_time, 3)} seconds.")

if __name__ == "__main__":
    main()
