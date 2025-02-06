import yaml
from typing import Dict, Any

class QuotedString(str):
    pass

def quoted_presenter(dumper, data):
    """Present string with quotes"""
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

yaml.add_representer(QuotedString, quoted_presenter)

def format_manifest_data(data: Dict) -> Dict:
    """Format specific fields with quotes and proper indentation"""
    formatted = data.copy()
    
    # Add quotes to specific fields
    formatted['study']['title'] = QuotedString(data['study']['title'])
    formatted['study']['abstract'] = QuotedString(data['study']['abstract'])
    formatted['study']['app_link'] = QuotedString(data['study']['app_link'])
    formatted['geo']['geo_summary'] = QuotedString(data['geo']['geo_summary'])
    formatted['processing']['description'] = QuotedString(data['processing']['description'])
    
    # Ensure proper formatting for cell_type_abbreviations
    if isinstance(data['study']['cell_type_abbreviations'], dict):
        formatted['study']['cell_type_abbreviations'] = {
            str(k): str(v) for k, v in data['study']['cell_type_abbreviations'].items()
        }
    
    return formatted

def save_manifest_to_yaml(data: Dict[str, Any], filename: str) -> None:
    """Save manifest data to YAML file with proper formatting"""
    formatted_data = format_manifest_data(data)
    with open(filename, 'w') as f:
        yaml.dump(
            formatted_data,
            f,
            default_flow_style=False,
            sort_keys=False,
            indent=2,
            allow_unicode=True
        ) 