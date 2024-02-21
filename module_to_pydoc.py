import inspect
import importlib
import sys

def extract_pydoc(functions_file, output_file, module_in, is_silent):
    with open(functions_file, 'r') as f:
        functions = f.readlines()

    with open(output_file, 'w') as out_f:
        last_non_empty_line = None
        for function_name in functions:
            function_name = function_name.strip()  # Remove leading/trailing whitespace
            if function_name:  # Check if the line is not empty
                try:
                    parts = function_name.split('.')
                    function_name = parts[-1]  # Get the last part as the function name
                    submodules = parts[:-1]   # Get the remaining parts as submodules
                    
                    # If there are no submodules, use module_in directly
                    if not submodules:
                        module = module_in
                    else:
                        module = module_in
                        for submodule_name in submodules:
                            module = getattr(module, submodule_name)
                    
                    function = getattr(module, function_name)
                    pydoc = inspect.getdoc(function)
                    if pydoc:
                        out_f.write(f"Function: {function_name}\n")
                        out_f.write(f"{pydoc}\n\n")
                        last_non_empty_line = out_f.tell()  # Remember the position of the last non-empty line
                    elif not is_silent:
                        print(f"No pydoc found for function: {function_name}\n")
                except (AttributeError, ValueError, ImportError) as e:
                    if not is_silent:
                        print(f"Error accessing function: {function_name}. Details: {str(e)}\n")

    # Truncate the output file to the last non-empty line
    if last_non_empty_line is not None:
        with open(output_file, 'a') as out_f:
            out_f.truncate(last_non_empty_line)

if __name__ == "__main__":
    if len(sys.argv) <   4:
        print("Usage: python module_to_pydoc.py [silent_option] functions_file output_file module")
        sys.exit(1)
    is_silent = False
    if len(sys.argv) == 4:
        functions_file = sys.argv[1]
        output_file = sys.argv[2]
        module_name = sys.argv[3]
    else:
        functions_file = sys.argv[2]
        output_file = sys.argv[3]
        module_name = sys.argv[4]
        if sys.argv[1] == "-s":
            is_silent = True
    module = importlib.import_module(module_name)
    

    extract_pydoc(functions_file, output_file, module, is_silent)
