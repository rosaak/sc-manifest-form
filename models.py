from typing import List, Dict, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime

class Processing(BaseModel):
    description: str = Field(default="", description="Processing description")

class Study(BaseModel):
    name: str = Field(..., description="Name of the study")
    title: str = Field(..., description="Title of the study")
    abstract: str = Field(..., description="Abstract of the study")
    pmid: List[int] = Field(default_factory=list, description="PubMed IDs")
    app_link: str = Field(default="", description="Application link")
    year: str = Field(default="", description="Year of the study")
    note: str = Field(default="", description="Additional notes")
    cell_type_abbreviations: Dict[str, str] = Field(
        default_factory=dict,
        description="Dictionary of cell type abbreviations"
    )

class GeoInfo(BaseModel):
    platforms: str = Field(..., description="Sequencing platforms")
    organisms: List[str] = Field(default_factory=lambda: ["Homo sapiens"], description="List of organisms")
    geoid: str = Field(..., description="GEO ID")
    geo_summary: str = Field(default="", description="GEO summary")
    urls: List[str] = Field(default_factory=list, description="Related URLs")
    processed_date: str = Field(default="", description="Processing date")

class Location(BaseModel):
    andata_on_azure: str = Field(default="", description="AnnData location on Azure")
    pp_notebooks: str = Field(default="", description="Preprocessing notebooks")

class Results(BaseModel):
    no_of_samples: str = Field(..., description="Number of samples")
    no_of_cells_after_pp: str = Field(..., description="Number of cells after preprocessing")
    no_of_genes_after_pp: str = Field(..., description="Number of genes after preprocessing")
    no_of_clusters: str = Field(..., description="Number of clusters")
    cluster_cell_numbers: Dict[str, int] = Field(default_factory=dict, description="Number of cells per cluster")

class ManifestData(BaseModel):
    project_id: str = Field(..., description="Project ID")
    study: Study
    geo: GeoInfo
    loc: Location
    results: Results
    processing: Processing

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "THB_sc0001_GSE123456",
                "study": {
                    "name": "Example Study",
                    "title": "Example Study Title",
                    "abstract": "Example study abstract",
                    "pmid": [12345678],
                    "app_link": "",
                    "year": "2024-02-06",
                    "note": "",
                    "cell_type_abbreviations": {
                        "NSC": "Neural Stem Cell",
                        "RG": "Radial Glia"
                    }
                },
                "geo": {
                    "platforms": "10x Illumina",
                    "organisms": ["Homo sapiens"],
                    "geoid": "GSE123456",
                    "geo_summary": "",
                    "urls": [],
                    "processed_date": ""
                },
                "loc": {
                    "andata_on_azure": "",
                    "pp_notebooks": ""
                },
                "results": {
                    "no_of_samples": "100",
                    "no_of_cells_after_pp": "10000",
                    "no_of_genes_after_pp": "2000",
                    "no_of_clusters": "10",
                    "cluster_cell_numbers": {}
                },
                "processing": {
                    "description": ""
                }
            }
        } 