import json
import sys

def remove_parameters_with_dash(json_obj):
    if isinstance(json_obj, dict):
        for key in list(json_obj.keys()):
            if key == "Parameters" and isinstance(json_obj[key], dict):
                params = json_obj[key]
                for param_key in list(params.keys()):
                    if param_key.startswith('-'):
                        del params[param_key]
            else:
                remove_parameters_with_dash(json_obj[key])
    elif isinstance(json_obj, list):
        for item in json_obj:
            remove_parameters_with_dash(item)

def remove_key_in_value(json_obj):
    if isinstance(json_obj, dict):
        for key in list(json_obj.keys()):
            if key == "Parameters" and isinstance(json_obj[key], dict):
                params = json_obj[key]
                for param_key, param_value in params.items():
                    if '\n' in param_value:
                        params[param_key] = param_value.split('\n', 1)[-1].strip()
            else:
                remove_key_in_value(json_obj[key])
    elif isinstance(json_obj, list):
        for item in json_obj:
            remove_key_in_value(item)

def remove_header_prefix(json_obj, key_name):
    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            # Check if the key exists and is a string before proceeding
            if key == key_name and key in json_obj and isinstance(value, str):
                # Split the string at the first occurrence of "-\n", keep the rest
                parts = value.split("-\n",  1)
                if len(parts) >  1:
                    # Combine the rest of the string, removing the separator
                    json_obj[key] = parts[1]
            else:
                remove_header_prefix(value, key_name)
    elif isinstance(json_obj, list):
        for item in json_obj:
            remove_header_prefix(item, key_name)

def group_data_by_package_and_submodule(data):
    # Initialize an empty dictionary for the grouped data
    grouped_data = {}

    # Iterate over the items in the original dictionary
    for function, details in data.items():
        package = details["Package"]
        submodule = details["Submodule"]

        # Initialize the package key in the new dictionary if it doesn't exist
        if package not in grouped_data:
            grouped_data[package] = {}

        # If the submodule is not empty, use it as a sub-key
        if submodule:
            if submodule not in grouped_data[package]:
                grouped_data[package][submodule] = {}
            # Use the function name as the key within the submodule dictionary
            grouped_data[package][submodule][function] = details
        else:
            # If the submodule is empty, append the item directly under the package
            if "__no_submodule" not in grouped_data[package]:
                grouped_data[package]["__no_submodule"] = {}
            # Use the function name as the key within the no_submodule dictionary
            grouped_data[package]["__no_submodule"][function] = details

    return grouped_data

def process_text_file(input_file, output_file):
    data = {}
    with open(input_file, 'r') as f:
        lines = f.readlines()
        function = None
        description = ""
        parameters = {}
        returns = ""
        return_type = ""
        notes = ""
        see_also_block = ""
        example = ""
        in_parameters = False  # Flag to track when to parse parameters
        in_returns = False  # Flag to track when to parse returns
        in_notes = False  # Flag to track when to parse notes
        in_see_also = False  # Flag to track when to parse lines under "See also"
        in_example = False # Flag to track when to parse examples
        last_key = None
        value_accumulator = None

        for i, line in enumerate(lines):
            if line.startswith("Function:"):
                if function is not None:
                    # Store the collected data for the previous function
                    data[function] = {
                        "Package": function.split('.')[0],
                        "Submodule": "" if len(function.split('.')) <= 2 else '.'.join(function.split('.')[1:-1]),
                        "Description": description.strip(),
                        "Parameters": parameters,
                        "Returns": returns.strip(),
                        "Return type": return_type.strip(),
                        "Notes": notes.strip(),
                        "Examples": example.strip(),
                        "See also": see_also_block.strip()  # Store the See_also block
                    }
                # Start parsing a new function
                function = line[len("Function:"):].strip()
                description = ""
                parameters = {}
                returns = ""
                notes = ""
                example = ""
                see_also_block = ""
                in_parameters = False
                in_returns = False
                in_notes = False
                in_example = False
                in_see_also = False
                last_key = None
                value_accumulator = None
            elif line.strip().startswith("Param") and lines[i+1].strip().startswith("-"):
                # Start parsing parameters
                in_parameters = True
                in_returns = False
                in_notes = False
                in_see_also = False
                in_example = False
            elif line.strip().startswith("Return") and lines[i+1].strip().startswith("-"):
                # Start parsing returns
                in_parameters = False
                in_returns = True
                in_notes = False
                in_see_also = False
                in_example = False
                returns += line
            elif line.strip().startswith("Note") and lines[i+1].strip().startswith("-"):
                # Start parsing notes
                in_parameters = False
                in_returns = False
                in_notes = True
                in_see_also = False
                in_example = False
                notes += line
            elif line.lower().strip().startswith("see also") and lines[i+1].strip().startswith("-"):
                # Start parsing see also
                in_parameters = False
                in_returns = False
                in_notes = False
                in_see_also = True
                in_example = False
                see_also_block += line
            elif line.lower().strip().startswith("example") and lines[i+1].strip().startswith("-"):
                # Start parsing example
                in_parameters = False
                in_returns = False
                in_notes = False
                in_see_also = False
                in_example = True
                example += line
            elif in_parameters:
                # Parse parameters
                if line.strip() and line[0].isspace() and last_key:
                    # Append to the value of the last key
                    if line.strip() == "":
                        # If the line is blank, preserve the newline character
                        value_accumulator += "\n"
                    else:
                        value_accumulator += "\n" + line.strip()
                else:
                    # Store line as part of parameters or returns or notes or example or see also
                    if last_key:
                        if in_returns:
                            returns += line.strip() + "\n"
                        elif in_notes:
                            notes += line.strip() + "\n"
                        elif in_see_also:
                            see_also_block += line.strip() + "\n"
                        elif in_example:
                            example += line.strip() + "\n"
                        else:
                            parameters[last_key] = value_accumulator.strip()
                    value_accumulator = line.strip()
                    parts = value_accumulator.split(None,  1)
                    
                    if len(parts) ==  1:
                        # Line with length of split equal to  1 is a key
                        last_key = parts[0].split(":")[0]  # Remove the key from appearing within the values
                    elif len(parts) >  1:
                        # If there's a last_key, it's followed by a value
                        if in_returns:
                            returns += parts[0] + " " + parts[1] + "\n"
                        elif in_notes:
                            notes += parts[0] + " " + parts[1] + "\n"
                        elif in_example:
                            example += parts[0] + " " + parts[1] + "\n"
                        elif in_see_also:
                            see_also_block += parts[0] + " " + parts[1] + "\n"
                        else:
                            parameters[parts[0]] = parts[1]
                        
                        last_key = None
                    if last_key and parts:
                        parameters[last_key] = parts[0]

                    # If there's a last key after parsing all lines, store its accumulated value
                if last_key:
                    parameters[last_key] = value_accumulator.strip()
            else:
                # Store line as part of description or returns or notes
                if in_returns:
                    returns += line.strip() + "\n"
                elif in_notes:
                    notes += line.strip() + "\n"
                elif in_see_also:
                    see_also_block += line.strip() + "\n"
                elif in_example:
                    example += line.strip() + "\n"
                else:
                    description += line.lstrip('\n').strip() + "\n"

        # Capture the last function-description pair
        if function is not None:
            data[function] = {
                "Package": function.split('.')[0],
                "Submodule": "" if len(function.split('.')) <= 2 else '.'.join(function.split('.')[1:-1]),
                "Description": description.strip(),
                "Parameters": parameters,
                "Returns": returns.strip(),
                "Return type": return_type.strip(),
                "Notes": notes.strip(),
                "Examples": example.strip(),
                "See also": see_also_block.strip()
            }
    
    remove_parameters_with_dash(data)
    remove_key_in_value(data)
    for key in ['Returns', 'Notes', 'Examples', "See also"]:
        remove_header_prefix(data, key)
    
    data = group_data_by_package_and_submodule(data)

    # Write data to JSON file
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    if len(sys.argv) !=  3:
        print("Usage: python api_to_json.py input_file output_file")
        sys.exit(1)

    input_file = sys.argv[1]  # Get the input file name from the command line arguments
    output_file = sys.argv[2]  # Get the output file name from the command line arguments
    process_text_file(input_file, output_file)
    print("Conversion complete. JSON file generated successfully.")
