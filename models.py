from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class Study(BaseModel):
    name: str = Field(..., description="Name of the study")
    title: str = Field(..., description="Title of the study")
    abstract: str = Field(..., description="Abstract of the study")
    pmid: Optional[List[int]] = Field(default=None, description="PubMed IDs")
    app_link: Optional[str] = Field(default=None, description="Application link")
    year: str = Field(..., description="Year of the study")
    note: Optional[str] = Field(default=None, description="Additional notes")
    cell_type_abbreviations: Dict[str, str] = Field(
        default_factory=dict,
        description="Dictionary of cell type abbreviations and their meanings"
    )

class Results(BaseModel):
    no_of_samples: int = Field(..., description="Number of samples")
    no_of_cells: int = Field(..., description="Number of cells")
    no_of_clusters: int = Field(..., description="Number of clusters")
    cluster_cell_numbers: Optional[Dict[str, int]] = Field(
        default_factory=dict,
        description="Number of cells per cluster"
    )
    no_of_genes_after_pp: int = Field(..., description="Number of genes after preprocessing")
    processed_date: datetime = Field(default_factory=datetime.now)

class Location(BaseModel):
    andata_on_azure: Optional[str] = Field(default=None, description="AnnData location on Azure")
    urls: List[str] = Field(default_factory=list, description="Related URLs")

class GeoInfo(BaseModel):
    platforms: str = Field(..., description="Sequencing platforms")
    organisms: List[str] = Field(..., description="List of organisms")
    geoid: str = Field(..., description="GEO ID")
    geo_summary: Optional[str] = Field(default=None, description="GEO summary")

class ManifestData(BaseModel):
    project_id: str = Field(..., description="Project ID")
    study: Study
    results: Results
    loc: Location
    geo: GeoInfo 