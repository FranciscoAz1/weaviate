from setup_collections import CollectionSetup
from data_insertion import DataInsertion
from data_queries import DataQueries

def setup_stage():
    """Setup the collections and their references."""
    print("Setting up collections...")
    setup = CollectionSetup()
    try:
        setup.setup_collections(clean_start=True)
        return setup
    except Exception as e:
        setup.close()
        print(f"Error during setup: {e}")
        return None

def data_insertion_stage():
    """Insert sample data into the collections."""
    print("\nInserting sample data...")
    insertion = DataInsertion()
    try:
        data_objects = insertion.insert_sample_data(
            num_entidades=2,
            num_pastas_per_entidade=5,
            num_ficheiros_per_pasta=8,
            num_metadados_per_ficheiro=1,
            num_fluxos=5,
            num_etapas_per_fluxo=10
        )
        insertion.add_document_with_extracted_text(
            pdf_path=r"C:\Users\Francisco Azeredo\OneDrive\Documents\tecnico\5 ano\tese\Código\Nougat\teses\DONUT.pdf",
        )
        return insertion
    except Exception as e:
        insertion.close()
        print(f"Error during data insertion: {e}")
        return None

def query_stage():
    """Run test queries on the data."""
    print("\nRunning test queries...")
    queries = DataQueries()
    try:
        # Query 1: Fluxos and their Etapas
        print("\n1. Querying Fluxos and their Etapas:")
        queries.query_fluxo_etapas(limit=3)
        
        # Query 2: Entidade hierarchy
        print("\n2. Querying Entidade hierarchy:")
        queries.query_entidade_hierarchy(limit=2)
        
        # Query 3: Global semantic search
        print("\n3. Running global semantic search:")
        queries.global_semantic_search("Find documents about contract approvals", limit_per_collection=3)
        
        return queries
    except Exception as e:
        queries.close()
        print(f"Error during queries: {e}")
        return None

def main():
    """Main function to orchestrate the workflow."""
    # Step 1: Setup
    setup_manager = setup_stage()
    if not setup_manager:
        return
    setup_manager.close()
    
    # Step 2: Data Insertion
    insertion_manager = data_insertion_stage()
    if not insertion_manager:
        return
    insertion_manager.close()
    
    # Step 3: Queries
    query_manager = query_stage()
    if not query_manager:
        return
    query_manager.close()
    
    print("\nAll operations completed successfully!")

if __name__ == "__main__":
    main()
