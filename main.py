import streamlit as st
from datetime import datetime
from typing import Dict, Any, List
from models import ManifestData, Study, Results, Location, GeoInfo, Processing
from yaml_handler import save_manifest_to_yaml
import os
import glob

st.set_page_config(layout="wide")

def remove_old_manifests():
    """Remove all previously generated manifest YAML files."""
    for file_path in glob.glob("manifest_*.yaml"):
        os.remove(file_path)

def parse_cell_types(cell_types_str: str) -> Dict[str, str]:
    """Parse cell type abbreviations from string format to dictionary"""
    if not cell_types_str.strip():
        return {}
    
    cell_types = {}
    lines = cell_types_str.strip().split('\n')
    
    for line_number, line in enumerate(lines, 1):
        # Skip empty lines
        if not line.strip():
            continue
        
        # Validate line format
        if ':' not in line:
            raise ValueError(f"Line {line_number}: Missing colon separator")
        
        # Split and clean
        abbr, desc = line.split(':', 1)
        abbr = abbr.strip()
        desc = desc.strip()
        
        # Validate content
        if not abbr:
            raise ValueError(f"Line {line_number}: Abbreviation is missing")
        if not desc:
            raise ValueError(f"Line {line_number}: Description is missing")
        if any(c in abbr for c in '"\'{}[]|>&*?!%@`'):
            raise ValueError(f"Line {line_number}: Abbreviation contains invalid characters")
        
        # Store in dictionary
        cell_types[abbr] = desc
    
    return cell_types

def validate_mandatory_fields(data: Dict) -> List[str]:
    """Validate mandatory fields"""
    errors = []
    if not data.get('project_id'):
        errors.append("Project ID is required")
    
    study = data.get('study', {})
    if not study.get('name'):
        errors.append("Study name is required")
    if not study.get('title'):
        errors.append("Study title is required")
    if not study.get('abstract'):
        errors.append("Study abstract is required")
    
    return errors

def main():
    # Custom CSS
    st.markdown("""
        <style>
                
            /* Set the base background color and pattern for the entire app  #ECEDEF*/
            .stApp {
                background-color: white !important;
                background-image: radial-gradient(circle, rgba(128, 128, 128, 0.8) 1px, transparent 1px) !important;
                background-size: 25px 25px !important;
                background-position: 0 0 !important;
            }

            /* Hide the deploy button */
            .reportview-container {
                margin-top: 10em;
                
            }
            .st-emotion-cache-1now2ym.ezrtsby2{
                opacity: 0;
                }
            
            .st-emotion-cache-1now2ym.ezrtsby2{
                position: fixed;
                top: 0px;
                left: 0px;
                right: 0px;
                height: 2.875rem;
                background: white;
                outline: none;
                z-index: 999990;
                display: block;
                opacity: 0;
            }
            #MainMenu {visibility: hidden;}
            .stDeployButton {display:none;}
            footer {visibility: hidden;}
            #stDecoration {display:none;}
                
            /*    #ECEDEF */
            /* Main background with dots */
            .main, [data-testid="stSidebar"] {
                background-color: white!important;
                background-image: radial-gradient(circle, rgba(128, 128, 128, 0.4) 1px, transparent 1px) !important;
                background-size: 25px 25px !important;
            }
            .title {
                text-align: center;
                padding: 0.5rem;
                font-size: 4rem;
                color: #1E88E5;
            }
            .subtitle {
                text-align: center;
                color: #666;
                padding-bottom: 1rem;
            }
            /* Headers */
            h1, h2, h3 {
                color: #1a1f36;
                font-weight: 600;
                text-align: center !important;
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
            .form-container {
                background-color: #ffffff;
                padding: 2rem;
                border-radius: 0.5rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .footer {
                position: fixed;
                left: 0;
                bottom: 0;
                width: 100%;
                text-align: center;
                padding: 1rem;
                background-color: white;
                color: grey;
                opacity: 0.75;
                font-size: 0.4rem;
                border-top: 1px solid #eee;
            }
        </style>
    """, unsafe_allow_html=True)

    # Title Section
    st.markdown("<h1 class='title'>Single Cell Manifest Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Fill in the form below to generate your manifest YAML file</p>", unsafe_allow_html=True)
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
            # Project ID Section
            with st.container():
                st.markdown("<h3 class='section-header'>🆔 Project ID</h3>", unsafe_allow_html=True)
                project_id = st.text_input("Project ID", key="project_id", help="Format: THB_sc####_GSE######")

            # Study Information Section
            with st.container():
                st.markdown("<h3 class='section-header'>📝 Study Information</h3>", unsafe_allow_html=True)
                study_name = st.text_input("Study Name", key="study_name",  help="Enter the name of your study; a short abbreviation is recommended")
                study_title = st.text_input("Study Title", key="study_title", help="Enter the title of your study; publication title.")
                study_abstract = st.text_area("Study Abstract", key="study_abstract", help="Pubmed abstract", height=400)
                pmid = st.text_input("PubMed IDs", key="pmid", help="Enter PubMed IDs separated by commas (e.g., 12345678, 87654321)")
                app_link = st.text_input("Application Link", key="app_link", help="Enter the application URL if available; add multiple if available")
                year = st.date_input("Study Date", key="year", help="Select the study date in YYYY-MM-DD format")
                study_note = st.text_area("Study Notes", key="note", help="Add any additional notes about the study", height=300)

            # Results Information Section
            with st.container():
                st.markdown("<h3 class='section-header'>📊 Results Information</h3>", unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    no_of_samples = st.text_input("Number of Samples", key="no_of_samples",  value="100", help="Enter the total number of samples")
                    no_of_cells = st.text_input("Number of Cells", key="no_of_cells_after_pp", value="10000", help="Enter the total number of cells after preprocessing")
                with col2:
                    no_of_clusters = st.text_input("Number of Clusters", key="no_of_clusters", value="10", help="Enter the number of clusters identified")
                    no_of_genes = st.text_input("Number of Genes", key="no_of_genes_after_pp", value="2000", help="Enter the number of genes after preprocessing")
                cluster_cell_numbers = st.text_input("Cluster Cell Numbers", key="cluster_cell_numbers", value="", help="Enter the number of cells in each cluster separated by commas")

        with right_col:
            # GEO Information Section
            with st.container():
                st.markdown("<h3 class='section-header'>🔍 GEO Information</h3>", unsafe_allow_html=True)
                platforms = st.text_input("Platforms", key="platforms", help="Enter the sequencing platforms used")
                organisms = st.text_area("Organisms", key="organisms", value="Homo sapiens", help="Enter organisms (one per line)")
                geoid = st.text_input("GEO ID", key="geoid", help="Enter the GEO accession number")
                geo_summary = st.text_area("GEO Summary", key="geo_summary", help="Provide a summary for GEO submission", height=180)
                urls = st.text_area("URLs", key="urls", help="Enter URLs (one per line)")
                processed_date = st.date_input("Processed Date", key="processed_date", help="Select the processing date")

            # Location Information Section
            with st.container():
                st.markdown("<h3 class='section-header'>📍 Location Information</h3>", unsafe_allow_html=True)
                azure_location = st.text_input("AnnData Azure Location", key="azure_location", help="Enter the Azure storage location for AnnData files")
                pp_notebooks = st.text_input("Preprocessing Notebooks", key="pp_notebooks", help="Enter the preprocessing notebooks location")

            # Processing Information
            with st.container():
                st.markdown("<h3 class='section-header'>⚙️ Processing Information</h3>", unsafe_allow_html=True)
                processing_description = st.text_area("Processing Description", key="processing_description", help="Describe the processing steps")

            # Cell Type Abbreviations Section
            with st.expander("ℹ️ Cell Type Abbreviations", expanded=True):
                st.markdown("""
                Enter cell type abbreviations in the following format (one per line):
                ```
                NSC: Neural Stem Cell
                RG: Radial Glia
                vRG: Ventricular Radial Glia
                ```
                """)
                
                cell_types_str = st.text_area(
                    "Cell Type Abbreviations",
                    key="cell_types",
                    height=200,
                    placeholder="NSC: Neural Stem Cell\nRG: Radial Glia\nvRG: Ventricular Radial Glia",
                    help="Enter cell type abbreviations, one per line with colon separator\n\n"
                         "Guidelines:\n"
                         "• One abbreviation per line\n"
                         "• Use colon (:) as separator\n"
                         "• Both abbreviation and description are required\n"
                         "• No special characters in abbreviations"
                )

        # Submit Button
        submitted = st.form_submit_button("🚀 Generate Manifest", use_container_width=True, type='primary')

        if submitted:
            with st.status("Processing manifest...", expanded=True) as status:
                try:
                    # Process inputs with better error handling
                    status.update(label="Validating inputs...", state="running")
                    
                    # Validate mandatory fields
                    data = {
                        "project_id": project_id,
                        "study": {
                            "name": study_name,
                            "title": study_title,
                            "abstract": study_abstract
                        }
                    }
                    validation_errors = validate_mandatory_fields(data)
                    if validation_errors:
                        for error in validation_errors:
                            st.error(f"❌ {error}")
                        st.stop()

                    status.update(label="Processing PubMed IDs...", state="running")
                    try:
                        pmid_list = [int(id.strip()) for id in pmid.split(",")] if pmid.strip() else []
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
                            no_of_cells_after_pp=no_of_cells,
                            no_of_clusters=no_of_clusters,
                            no_of_genes_after_pp=no_of_genes,
                            cluster_cell_numbers={}
                        )

                        location = Location(
                            andata_on_azure=azure_location,
                            pp_notebooks=pp_notebooks
                        )

                        geo_info = GeoInfo(
                            platforms=platforms,
                            organisms=organisms_list,
                            geoid=geoid,
                            geo_summary=geo_summary,
                            urls=urls_list,
                            processed_date=processed_date.strftime("%Y-%m-%d")
                        )

                        processing = Processing(
                            description=processing_description
                        )

                        manifest = ManifestData(
                            project_id=project_id,
                            study=study,
                            geo=geo_info,
                            loc=location,
                            results=results,
                            processing=processing
                        )
                    except ValueError as e:
                        st.error(f"❌ Validation Error: {str(e)}")
                        st.stop()

                    # Save to YAML
                    filename = f"manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
                    save_manifest_to_yaml(manifest.model_dump(), filename)

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
        with st.expander("## 🎉 Generated Manifest", expanded=True):
            st.code(st.session_state.yaml_content, language='yaml')
            st.download_button(
                label="📥 Download YAML file",
                data=st.session_state.yaml_content,
                file_name=st.session_state.yaml_filename,
                mime="application/x-yaml",
                use_container_width=True
            )
    
    # Footer
    st.markdown("<div class='footer'><h6>Trailhead Biosystems Inc. © 2025</h6></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    remove_old_manifests()
    main()