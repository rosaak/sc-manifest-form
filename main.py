import streamlit as st
import yaml
from datetime import datetime
from typing import Dict, Any, List
import json
from models import ManifestData, Study, Results, Location, GeoInfo

def save_to_yaml(data: Dict[str, Any], filename: str) -> None:
    """Save dictionary data to a YAML file"""
    with open(filename, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

def parse_cell_types(cell_types_str: str) -> Dict[str, str]:
    """Parse cell type abbreviations from a string format to dictionary"""
    if not cell_types_str.strip():
        return {}
    
    try:
        # First try to parse as JSON
        return json.loads(cell_types_str)
    except json.JSONDecodeError:
        # If JSON parsing fails, try parsing line by line format
        cell_types = {}
        for line in cell_types_str.strip().split('\n'):
            if ':' in line:
                abbr, desc = line.split(':', 1)
                cell_types[abbr.strip()] = desc.strip()
        return cell_types

def main():
    st.title("Single Cell Manifest Generator")
    st.write("Fill in the form below to generate your manifest YAML file")
    
    with st.form("manifest_form"):
        # Project ID
        project_id = st.text_input(
            "Project ID", 
            key="project_id", 
            help="Format: THB_sc####_GSE######"
        )
        
        # Study Section
        st.subheader("Study Information")
        study_name = st.text_input("Study Name", key="study_name")
        study_title = st.text_input("Study Title", key="study_title")
        study_abstract = st.text_area("Study Abstract", key="study_abstract")
        pmid = st.text_input(
            "PubMed IDs", 
            key="pmid",
            help="Enter PubMed IDs separated by commas (e.g., 12345678, 87654321)"
        )
        app_link = st.text_input("Application Link", key="app_link")
        year = st.date_input("Study Date", key="year")
        study_note = st.text_area("Study Notes", key="note")
        
        # Cell Type Abbreviations
        st.subheader("Cell Type Abbreviations")
        st.markdown("""
        Enter cell type abbreviations in either format:
        ```
        NSC: Neural Stem Cell
        RG: Radial Glia
        vRG: Ventricular Radial Glia
        ```
        OR as JSON:
        ```json
        {
            "NSC": "Neural Stem Cell",
            "RG": "Radial Glia",
            "vRG": "Ventricular Radial Glia"
        }
        ```
        """)
        cell_types_str = st.text_area(
            "Cell Type Abbreviations", 
            key="cell_types",
            height=200
        )
        
        # Results Section
        st.subheader("Results Information")
        no_of_samples = st.number_input("Number of Samples", min_value=1, key="no_of_samples")
        no_of_cells = st.number_input("Number of Cells", min_value=1, key="no_of_cells")
        no_of_clusters = st.number_input("Number of Clusters", min_value=1, key="no_of_clusters")
        no_of_genes = st.number_input("Number of Genes After Preprocessing", min_value=1, key="no_of_genes")
        
        # Location Section
        st.subheader("Location Information")
        azure_location = st.text_input("AnnData Azure Location", key="azure_location")
        urls = st.text_area(
            "URLs", 
            key="urls",
            help="Enter one URL per line"
        )
        
        # GEO Information
        st.subheader("GEO Information")
        platforms = st.text_input("Platforms", key="platforms")
        organisms = st.text_area(
            "Organisms", 
            key="organisms",
            help="Enter one organism per line"
        )
        geoid = st.text_input("GEO ID", key="geoid")
        geo_summary = st.text_area("GEO Summary", key="geo_summary")
        
        submitted = st.form_submit_button("Generate Manifest")
        
        if submitted:
            try:
                # Process inputs with better error handling
                try:
                    pmid_list = [int(id.strip()) for id in pmid.split(",")] if pmid.strip() else None
                except ValueError as e:
                    st.error("❌ Error: PubMed IDs must be valid integers separated by commas")
                    st.stop()
                
                try:
                    cell_types_dict = parse_cell_types(cell_types_str)
                except Exception as e:
                    st.error("❌ Error: Invalid cell type abbreviations format. Please check the format and try again.")
                    st.stop()
                
                urls_list = [url.strip() for url in urls.splitlines() if url.strip()]
                organisms_list = [org.strip() for org in organisms.splitlines() if org.strip()]
                
                # Create model instances
                try:
                    study = Study(
                        name=study_name,
                        title=study_title,
                        abstract=study_abstract,
                        pmid=pmid_list,
                        app_link=app_link,
                        year=year.strftime("%Y-%m-%d"),
                        note=study_note,
                        cell_type_abbreviations=cell_types_dict
                    )
                    
                    results = Results(
                        no_of_samples=no_of_samples,
                        no_of_cells=no_of_cells,
                        no_of_clusters=no_of_clusters,
                        no_of_genes_after_pp=no_of_genes,
                        processed_date=datetime.now()
                    )
                    
                    location = Location(
                        andata_on_azure=azure_location,
                        urls=urls_list
                    )
                    
                    geo_info = GeoInfo(
                        platforms=platforms,
                        organisms=organisms_list,
                        geoid=geoid,
                        geo_summary=geo_summary
                    )
                    
                    manifest = ManifestData(
                        project_id=project_id,
                        study=study,
                        results=results,
                        loc=location,
                        geo=geo_info
                    )
                except ValueError as e:
                    st.error(f"❌ Validation Error: {str(e)}")
                    st.stop()
                
                # Convert to dict and save
                data_dict = manifest.model_dump()
                
                # Save to YAML
                filename = f"manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
                save_to_yaml(data_dict, filename)
                
                # Show success message
                st.success(f"✅ Manifest saved successfully as {filename}")
                
                # Display the YAML content
                with open(filename, 'r') as f:
                    yaml_content = f.read()
                st.code(yaml_content, language='yaml')
                
                # Add download button
                st.download_button(
                    label="Download YAML file",
                    data=yaml_content,
                    file_name=filename,
                    mime="application/x-yaml"
                )
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 