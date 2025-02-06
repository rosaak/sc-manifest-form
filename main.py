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
    # Custom CSS
    st.markdown("""
        <style>
            .title {
                text-align: center;
                padding: 1rem;
                color: #1E88E5;
            }
            .subtitle {
                text-align: center;
                color: #666;
                padding-bottom: 1rem;
            }
            .stContainer {
                background-color: #f8f9fa;
                padding: 1rem;
                border-radius: 0.5rem;
                margin-bottom: 1rem;
            }
            .section-header {
                color: #1E88E5;
                padding: 0.5rem 0;
                border-bottom: 2px solid #1E88E5;
                margin-bottom: 1rem;
            }
            .stTextInput, .stNumberInput, .stTextArea {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 0.25rem;
                padding: 0.5rem;
            }
            .form-container {
                background-color: #ffffff;
                padding: 2rem;
                border-radius: 0.5rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
        </style>
    """, unsafe_allow_html=True)

    # Title Section
    st.markdown("<h1 class='title'>Single Cell Manifest Generator</h1>", unsafe_allow_html=True)
    st.caption("<p class='subtitle'>Fill in the form below to generate your manifest YAML file</p>", unsafe_allow_html=True)
    st.divider()

    # Initialize session state
    if 'yaml_content' not in st.session_state:
        st.session_state.yaml_content = None
    if 'yaml_filename' not in st.session_state:
        st.session_state.yaml_filename = None

    # Main Form
    with st.form("manifest_form", clear_on_submit=False):
        # Create two columns for the layout
        left_col, right_col = st.columns([3, 2])

        with left_col:
            # Study Information Section
            with st.container():
                st.markdown("<h3 class='section-header'>📝 Study Information</h3>", unsafe_allow_html=True)
                study_name = st.text_input("Study Name", key="study_name", help="Enter the name of your study")
                study_title = st.text_input("Study Title", key="study_title", help="Enter the title of your study")
                study_abstract = st.text_area("Study Abstract", key="study_abstract", help="Provide a detailed abstract of your study")
                pmid = st.text_input("PubMed IDs", key="pmid", help="Enter PubMed IDs separated by commas (e.g., 12345678, 87654321)")
                app_link = st.text_input("Application Link", key="app_link", help="Enter the application URL if available")
                year = st.date_input("Study Date", key="year", help="Select the study date")
                study_note = st.text_area("Study Notes", key="note", help="Add any additional notes about the study")

            # Results Information Section
            with st.container():
                st.markdown("<h3 class='section-header'>📊 Results Information</h3>", unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    no_of_samples = st.text_input("Number of Samples", key="no_of_samples", help="Enter the total number of samples", value="100")
                    no_of_cells = st.text_input("Number of Cells", key="no_of_cells", help="Enter the total number of cells", value="10000")
                with col2:
                    no_of_clusters = st.text_input("Number of Clusters", key="no_of_clusters", help="Enter the number of clusters identified", value="10")
                    no_of_genes = st.text_input("Number of Genes", key="no_of_genes", help="Enter the number of genes after preprocessing", value="2000")

            # Location Information Section
            with st.container():
                st.markdown("<h3 class='section-header'>📍 Location Information</h3>", unsafe_allow_html=True)
                azure_location = st.text_input("AnnData Azure Location", key="azure_location",
                                             help="Enter the Azure storage location for AnnData files")
                urls = st.text_area("URLs", key="urls",
                                  help="Enter URLs (one per line) for additional resources")

        with right_col:
            # Project ID Section
            with st.container():
                st.markdown("<h3 class='section-header'>🆔 Project ID</h3>", unsafe_allow_html=True)
                project_id = st.text_input("Project ID", key="project_id",
                                         help="Format: THB_sc####_GSE######")

            # GEO Information Section
            with st.container():
                st.markdown("<h3 class='section-header'>🔍 GEO Information</h3>", unsafe_allow_html=True)
                platforms = st.text_input("Platforms", key="platforms",
                                        help="Enter the sequencing platforms used")
                organisms = st.text_area("Organisms", key="organisms",
                                       help="Enter organisms (one per line)")
                geoid = st.text_input("GEO ID", key="geoid",
                                    help="Enter the GEO accession number")
                geo_summary = st.text_area("GEO Summary", key="geo_summary",
                                         help="Provide a summary for GEO submission")

            # Cell Type Abbreviations Section
            with st.expander("ℹ️ Cell Type Abbreviations", expanded=True):
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
                cell_types_str = st.text_area("Cell Type Abbreviations", 
                                            key="cell_types",
                                            height=200,
                                            help="Enter cell type abbreviations in either format shown above")

        # Submit Button
        submitted = st.form_submit_button("🚀 Generate Manifest")

        if submitted:
            with st.status("Processing manifest...", expanded=True) as status:
                try:
                    # Process inputs with better error handling
                    status.update(label="Validating PubMed IDs...", state="running")
                    try:
                        pmid_list = [int(id.strip()) for id in pmid.split(",")] if pmid.strip() else None
                    except ValueError as e:
                        st.error("❌ Error: PubMed IDs must be valid integers separated by commas")
                        st.stop()

                    status.update(label="Processing cell type abbreviations...", state="running")
                    try:
                        cell_types_dict = parse_cell_types(cell_types_str)
                    except Exception as e:
                        st.error("❌ Error: Invalid cell type abbreviations format. Please check the format and try again.")
                        st.stop()

                    urls_list = [url.strip() for url in urls.splitlines() if url.strip()]
                    organisms_list = [org.strip() for org in organisms.splitlines() if org.strip()]

                    # Create model instances
                    status.update(label="Creating manifest...", state="running")
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
                    filename = f"manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
                    save_to_yaml(data_dict, filename)

                    # Store YAML content in session state
                    with open(filename, 'r') as f:
                        st.session_state.yaml_content = f.read()
                        st.session_state.yaml_filename = filename

                    status.update(label="✅ Manifest generated successfully!", state="complete")
                    st.toast("Manifest generated successfully!", icon="✅")

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    status.update(label="❌ Error generating manifest", state="error")

    # Display YAML content and download button outside the form
    if st.session_state.yaml_content is not None:
        with st.expander("🎉 Generated Manifest", expanded=True):
            st.code(st.session_state.yaml_content, language='yaml')
            st.download_button(
                label="📥 Download YAML file",
                data=st.session_state.yaml_content,
                file_name=st.session_state.yaml_filename,
                mime="application/x-yaml",
                use_container_width=True
            )

if __name__ == "__main__":
    main() 