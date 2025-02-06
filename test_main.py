import pytest
import yaml
from datetime import datetime
import os
from models import ManifestData, Study, Results, Location, GeoInfo
from main import save_to_yaml

def test_manifest_data_model():
    """Test ManifestData model validation"""
    data = {
        "project_id": "THB_sc0001_GSE123456",
        "study": {
            "name": "Test Study",
            "title": "Test Title",
            "abstract": "Test Abstract",
            "pmid": [12345678],
            "app_link": "http://example.com",
            "year": "2024-02-06",
            "note": "Test note",
            "cell_type_abbreviations": {"NSC": "Neural Stem Cell"}
        },
        "results": {
            "no_of_samples": 10,
            "no_of_cells": 1000,
            "no_of_clusters": 5,
            "no_of_genes_after_pp": 2000,
            "processed_date": datetime.now()
        },
        "loc": {
            "andata_on_azure": "test/location",
            "urls": ["http://example.com"]
        },
        "geo": {
            "platforms": "10x Illumina",
            "organisms": ["Homo sapiens"],
            "geoid": "GSE123456",
            "geo_summary": "Test summary"
        }
    }
    
    manifest = ManifestData(**data)
    assert manifest.project_id == "THB_sc0001_GSE123456"
    assert manifest.study.name == "Test Study"
    assert manifest.results.no_of_samples == 10
    assert manifest.loc.urls == ["http://example.com"]
    assert manifest.geo.platforms == "10x Illumina"

def test_save_to_yaml():
    """Test YAML file saving functionality"""
    test_data = {
        "project_id": "THB_sc0001_GSE123456",
        "study": {
            "name": "Test Study",
            "title": "Test Title",
            "abstract": "Test Abstract",
            "year": "2024-02-06",
            "cell_type_abbreviations": {}
        },
        "results": {
            "no_of_samples": 10,
            "no_of_cells": 1000,
            "no_of_clusters": 5,
            "no_of_genes_after_pp": 2000,
            "processed_date": datetime.now()
        },
        "loc": {
            "urls": []
        },
        "geo": {
            "platforms": "10x Illumina",
            "organisms": ["Homo sapiens"],
            "geoid": "GSE123456"
        }
    }
    
    test_filename = "test_manifest.yaml"
    
    # Save data to YAML
    save_to_yaml(test_data, test_filename)
    
    # Verify file exists
    assert os.path.exists(test_filename)
    
    # Read and verify content
    with open(test_filename, 'r') as f:
        loaded_data = yaml.safe_load(f)
    
    assert loaded_data["project_id"] == test_data["project_id"]
    assert loaded_data["study"]["name"] == test_data["study"]["name"]
    assert loaded_data["results"]["no_of_samples"] == test_data["results"]["no_of_samples"]
    
    # Cleanup
    os.remove(test_filename) 