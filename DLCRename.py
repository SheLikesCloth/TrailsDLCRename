import os
import json
import re
import xml.etree.ElementTree as ET

def get_folder_name():
    # List all directories in the current directory
    all_dirs = [d for d in os.listdir('.') if os.path.isdir(d)]
    
    # Filter directories matching the required format
    matching_dirs = [d for d in all_dirs if re.match(r'^C_CHR\d{3}(?:_C\d{2,3})?$', d)]
    
    # Return the first matching directory or None if no match is found
    return matching_dirs[0] if matching_dirs else None

def get_user_input():
    NameOrg = get_folder_name()
    if NameOrg is None:
        print("No folder found with the required naming format.")
        return None, None

    NameSuffix = input("Select a model suffix number (to create C_CHR***_C090, enter 090): ")

    return NameOrg, NameSuffix

def compute_names(NameOrg, NameSuffix):
    # Compute NameOrgLower
    NameOrgLower = NameOrg[2:].lower()

    # Compute NameNew and NameNewLower
    NameNew = re.match(r'^C_CHR\d{3}', NameOrg).group() + "_C" + NameSuffix
    NameNewLower = NameNew[2:].lower()

    return NameOrgLower, NameNew, NameNewLower

def process_directory_and_metadata(NameOrg, NameOrgLower, NameNew, NameNewLower):
    # Rename directory
    if os.path.exists(NameOrg):
        os.rename(NameOrg, NameNew)
    else:
        print(f"Directory '{NameOrg}' not found.")

    # Update metadata.json
    if os.path.exists('metadata.json'):
        with open('metadata.json', 'r') as f:
            data = json.load(f)

        if data.get("name") == NameOrgLower:
            data["name"] = NameNewLower
        if data.get("pkg_name") == NameOrg:
            data["pkg_name"] = NameNew

        with open('metadata.json', 'w') as f:
            json.dump(data, f, indent=4)
    else:
        print("metadata.json not found.")

def modify_xml(NameOrg, NameOrgLower, NameNew, NameNewLower):
    xml_path = os.path.join(NameNew, "asset_D3D11.xml")
    
    if not os.path.exists(xml_path):
        print(f"XML file '{xml_path}' not found.")
        return

    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    for asset in root.findall(".//asset[@symbol='{}']".format(NameOrg)):
        asset.set("symbol", NameNew)
        
        # Find the first cluster with type="p_collada"
        cluster = asset.find(".//cluster[@type='p_collada']")
        if cluster is not None:
            path = cluster.get("path")
            if path:
                path_parts = path.split("/")
                if path_parts[2] != "dlc":
                    path_parts.insert(2, "dlc")
                path = "/".join(path_parts)
                # Replace all instances of NameOrgLower with NameNewLower
                path = path.replace(NameOrgLower, NameNewLower)
                cluster.set("path", path)
    
    # Write the XML file with declaration
    with open(xml_path, 'wb') as f:
        f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
        tree.write(f)


def main():
    NameOrg, NameSuffix = get_user_input()
    if NameOrg and NameSuffix:
        NameOrgLower, NameNew, NameNewLower = compute_names(NameOrg, NameSuffix)
        process_directory_and_metadata(NameOrg, NameOrgLower, NameNew, NameNewLower)
        modify_xml(NameOrg, NameOrgLower, NameNew, NameNewLower)

if __name__ == "__main__":
    main()
