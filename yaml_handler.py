import yaml
from typing import Dict, Any

class QuotedString(str):
    pass

def quoted_presenter(dumper, data):
    """Present string with quotes"""
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

def dict_representer(dumper, data):
    """Custom representer for dictionaries to control formatting"""
    return dumper.represent_dict(data)

# Add custom representers
yaml.add_representer(QuotedString, quoted_presenter)
yaml.add_representer(dict, dict_representer)

# Configure YAML dumper
yaml.Dumper.ignore_aliases = lambda *args: True

def format_string_for_yaml(s: str) -> str:
    """Format string for YAML output, handling special characters"""
    if not s:
        return ""
    # If string contains newlines or special characters, use literal block style
    if "\n" in s or any(c in s for c in '"\'{}[]|>&*?!:%@`'):
        return s.replace('"', '\\"')
    return s

def clean_dict_strings(d: dict) -> dict:
    """Clean dictionary strings and handle special characters"""
    clean = {}
    for k, v in d.items():
        # Clean the key (remove quotes and extra spaces)
        clean_key = str(k).strip().strip("'\"")
        
        # Clean the value based on its type
        if isinstance(v, str):
            clean_value = v.strip().strip("'\"").rstrip(",")
        elif isinstance(v, dict):
            clean_value = clean_dict_strings(v)
        else:
            clean_value = v
            
        clean[clean_key] = clean_value
    return clean

def format_manifest_data(data: Dict) -> Dict:
    """Format manifest data for YAML output"""
    formatted = data.copy()
    
    # Format strings that need special handling
    formatted['study']['title'] = format_string_for_yaml(data['study']['title'])
    formatted['study']['abstract'] = format_string_for_yaml(data['study']['abstract'])
    formatted['study']['app_link'] = format_string_for_yaml(data['study']['app_link'])
    formatted['geo']['geo_summary'] = format_string_for_yaml(data['geo']['geo_summary'])
    formatted['processing']['description'] = format_string_for_yaml(data['processing']['description'])
    
    # Handle cell_type_abbreviations with special care
    if isinstance(data['study']['cell_type_abbreviations'], dict):
        formatted['study']['cell_type_abbreviations'] = clean_dict_strings(
            data['study']['cell_type_abbreviations']
        )
    
    return formatted

def save_manifest_to_yaml(data: Dict[str, Any], filename: str) -> None:
    """Save manifest data to YAML file with proper formatting"""
    formatted_data = format_manifest_data(data)
    
    with open(filename, 'w') as f:
        yaml.dump(
            formatted_data,
            f,
            default_style=None,
            default_flow_style=False,
            sort_keys=False,
            indent=2,
            allow_unicode=True,
            width=1000,
            explicit_start=True,
            explicit_end=True
        ) 