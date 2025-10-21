import weaviate
from weaviate.classes.config import Property, DataType, ReferenceProperty, Configure
from weaviate.classes.query import QueryReference, MetadataQuery

class WeaviateDataManager:
    # Define Ollama API details
    OLLAMA_API_ENDPOINT = "http://host.docker.internal:11434"
    VECTOR_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    GENERATION_MODEL = "qwen2.5:latest"
    
    def __init__(self, connect_to_local=True):
        """Initialize the Weaviate client connection."""
        if connect_to_local:
            self.client = weaviate.connect_to_local()
        else:
            # Add configuration for non-local connection if needed
            self.client = weaviate.connect_to_local()  # Placeholder
        
        # Collection objects
        self.fluxo = None
        self.etapa = None
        self.entidade = None
        self.pasta = None
        self.ficheiro = None
        self.metadados = None
    
    def setup_collections(self, clean_start=True):
        """Create all collections and their references."""
        # Delete old collections if clean_start is True
        if clean_start:
            self._delete_existing_collections()
        
        # Create collections
        self._create_collections()
        
        # Get collection objects
        self._get_collection_objects()
        
        # Create references between collections
        self._create_references()
        
        print("Collections with vectorization & generation created successfully!")
        print("References added successfully!")
    
    def _delete_existing_collections(self):
        """Delete existing collections if they exist."""
        collection_names = ["Fluxo", "Etapa", "Entidade", "Pasta", "Ficheiro", "Metadados"]
        for collection_name in collection_names:
            try:
                self.client.collections.delete(collection_name)
            except:
                pass  # Ignore if collection doesn't exist
    
    def _create_collections(self):
        """Create all required collections."""
        # 1. Create "Fluxo" Collection
        self._create_collection(
            "Fluxo",
            "A workflow that contains multiple stages (etapas).",
            [Property(name="name", data_type=DataType.TEXT)]
        )

        # 2. Create "Etapa" Collection
        self._create_collection(
            "Etapa",
            "A stage within a workflow.",
            [Property(name="name", data_type=DataType.TEXT)]
        )

        # 3. Create "Entidade" Collection
        self._create_collection(
            "Entidade",
            "An entity that owns folders (pastas).",
            [Property(name="name", data_type=DataType.TEXT)]
        )

        # 4. Create "Pasta" Collection
        self._create_collection(
            "Pasta",
            "A folder belonging to an entity and containing documents (ficheiros).",
            [Property(name="name", data_type=DataType.TEXT)]
        )

        # 5. Create "Ficheiro" Collection
        self._create_collection(
            "Ficheiro",
            "A document that contains metadata.",
            [Property(name="name", data_type=DataType.TEXT)]
        )

        # 6. Create "Metadados" Collection
        self._create_collection(
            "Metadados",
            "Metadata associated with a document (ficheiro).",
            [Property(name="name", data_type=DataType.TEXT)]
        )
    
    def _create_collection(self, name, description, properties):
        """Create a collection with vectorization & generative AI."""
        self.client.collections.create(
            name=name,
            description=description,
            properties=properties,
        vectorizer_config=[
            Configure.NamedVectors.text2vec_transformers(
                name="text_vector",
                source_properties=["text"],
                pooling_strategy="masked_mean",
                )
        ],
            generative_config=Configure.Generative.ollama(
                api_endpoint=self.OLLAMA_API_ENDPOINT,
                model=self.GENERATION_MODEL
            )
        )
    
    def _get_collection_objects(self):
        """Get references to all collection objects."""
        self.fluxo = self.client.collections.get("Fluxo")
        self.etapa = self.client.collections.get("Etapa")
        self.entidade = self.client.collections.get("Entidade")
        self.pasta = self.client.collections.get("Pasta")
        self.ficheiro = self.client.collections.get("Ficheiro")
        self.metadados = self.client.collections.get("Metadados")
    
    def _create_references(self):
        """Create all references between collections."""
        # Add cross-references
        self.fluxo.config.add_reference(ReferenceProperty(name="hasEtapas", target_collection="Etapa"))
        self.fluxo.config.add_reference(ReferenceProperty(name="belongsToFicheiros", target_collection="Ficheiro"))
        self.fluxo.config.add_reference(ReferenceProperty(name="belongsToPastas", target_collection="Pasta"))

        self.etapa.config.add_reference(ReferenceProperty(name="belongsToFluxo", target_collection="Fluxo"))
        self.etapa.config.add_reference(ReferenceProperty(name="hasFicheiros", target_collection="Ficheiro"))

        self.entidade.config.add_reference(ReferenceProperty(name="hasFicheiros", target_collection="Ficheiro"))
        self.entidade.config.add_reference(ReferenceProperty(name="hasPastas", target_collection="Pasta"))

        self.pasta.config.add_reference(ReferenceProperty(name="hasFicheiros", target_collection="Ficheiro"))
        self.pasta.config.add_reference(ReferenceProperty(name="hasEntidades", target_collection="Entidade"))
        self.pasta.config.add_reference(ReferenceProperty(name="hasFluxos", target_collection="Fluxo"))

        self.ficheiro.config.add_reference(ReferenceProperty(name="belongsToMetadados", target_collection="Metadados"))
        self.ficheiro.config.add_reference(ReferenceProperty(name="hasEtapas", target_collection="Etapa"))
        self.ficheiro.config.add_reference(ReferenceProperty(name="hasPastas", target_collection="Pasta"))
        self.ficheiro.config.add_reference(ReferenceProperty(name="hasEntidades", target_collection="Entidade"))

        self.metadados.config.add_reference(ReferenceProperty(name="hasFicheiros", target_collection="Ficheiro"))
        self.metadados.config.add_reference(ReferenceProperty(name="hasEtapas", target_collection="Etapa"))
        self.metadados.config.add_reference(ReferenceProperty(name="hasPastas", target_collection="Pasta"))
        self.metadados.config.add_reference(ReferenceProperty(name="hasEntidades", target_collection="Entidade"))
    
    def insert_sample_data(self, num_entidades=2, num_pastas_per_entidade=5, 
                           num_ficheiros_per_pasta=8, num_metadados_per_ficheiro=1,
                           num_fluxos=5, num_etapas_per_fluxo=10):
        """Insert sample data into all collections with proper references."""
        # Step 1: Create Entidades
        entidade_objs = [self.add_entidade(f"Empresa {i+1}") for i in range(num_entidades)]

        # Step 2: Create Pastas and link them to Entidades
        pasta_objs = []
        for i, entidade_obj in enumerate(entidade_objs):
            for j in range(num_pastas_per_entidade):
                pasta_obj = self.add_pasta(f"Pasta {j+1} of Empresa {i+1}", entidade_obj=entidade_obj)
                pasta_objs.append(pasta_obj)

        # Step 3: Create Ficheiros and link them to Pastas and Entidades
        ficheiro_objs = []
        for i, pasta_obj in enumerate(pasta_objs):
            entidade_obj = entidade_objs[i % len(entidade_objs)]
            for j in range(num_ficheiros_per_pasta):
                ficheiro_obj = self.add_ficheiro(f"Documento {j+1} in {pasta_obj}", 
                                                pasta_obj=pasta_obj, 
                                                entidade_obj=entidade_obj)
                ficheiro_objs.append(ficheiro_obj)

        # Step 4: Create Metadados and link them to Ficheiros
        metadados_objs = []
        for i, ficheiro_obj in enumerate(ficheiro_objs):
            for j in range(num_metadados_per_ficheiro):
                metadados_obj = self.add_metadados(f"Metadata {j+1} for {ficheiro_obj}", 
                                                  ficheiro_obj=ficheiro_obj)
                metadados_objs.append(metadados_obj)

        # Step 5: Create Fluxos and link them to Pastas and Ficheiros
        fluxo_objs = []
        for i in range(num_fluxos):
            pasta_obj = pasta_objs[i % len(pasta_objs)]
            ficheiro_obj = ficheiro_objs[i % len(ficheiro_objs)]
            fluxo_obj = self.add_fluxo(f"Fluxo {i+1}", pasta_obj=pasta_obj, ficheiro_obj=ficheiro_obj)
            fluxo_objs.append(fluxo_obj)

        # Step 6: Create Etapas and link them to Fluxos and Ficheiros
        etapa_objs = []
        for i, fluxo_obj in enumerate(fluxo_objs):
            ficheiro_obj = ficheiro_objs[i % len(ficheiro_objs)]
            for j in range(num_etapas_per_fluxo):
                etapa_obj = self.add_etapa(f"Etapa {j+1} of Fluxo {i+1}", 
                                          fluxo_obj=fluxo_obj, 
                                          ficheiro_obj=ficheiro_obj)
                etapa_objs.append(etapa_obj)

        print("Bulk sample data inserted and linked successfully!")
        
        return {
            "entidades": entidade_objs,
            "pastas": pasta_objs,
            "ficheiros": ficheiro_objs,
            "metadados": metadados_objs,
            "fluxos": fluxo_objs,
            "etapas": etapa_objs
        }
    
    def add_fluxo(self, fluxo_name, pasta_obj=None, ficheiro_obj=None, etapa_obj=None):
        """Creates a Fluxo and links it to Pasta and Ficheiro if provided."""
        fluxo_obj = self.fluxo.data.insert({"name": fluxo_name})
        if pasta_obj:
            self.fluxo.data.reference_add(fluxo_obj, "belongsToPastas", pasta_obj)
        if ficheiro_obj:
            self.fluxo.data.reference_add(fluxo_obj, "belongsToFicheiros", ficheiro_obj)
        if etapa_obj:
            self.fluxo.data.reference_add(fluxo_obj, "hasEtapas", etapa_obj)
        return fluxo_obj

    def add_etapa(self, etapa_name, fluxo_obj=None, ficheiro_obj=None):
        """Creates an Etapa and links it to Fluxo and Ficheiro if provided."""
        etapa_obj = self.etapa.data.insert({"name": etapa_name})
        if fluxo_obj:
            self.fluxo.data.reference_add(fluxo_obj, "hasEtapas", etapa_obj)
            self.etapa.data.reference_add(etapa_obj, "belongsToFluxo", fluxo_obj)
        if ficheiro_obj:
            self.etapa.data.reference_add(etapa_obj, "hasFicheiros", ficheiro_obj)
        return etapa_obj

    def add_entidade(self, entidade_name, ficheiro_obj=None, pasta_obj=None):
        """Creates an Entidade and links it to Ficheiro and Pasta if provided."""
        entidade_obj = self.entidade.data.insert({"name": entidade_name})
        if ficheiro_obj:
            self.entidade.data.reference_add(entidade_obj, "hasFicheiros", ficheiro_obj)
        if pasta_obj:
            self.entidade.data.reference_add(entidade_obj, "hasPastas", pasta_obj)
        return entidade_obj

    def add_pasta(self, pasta_name, entidade_obj=None, fluxo_obj=None, ficheiro_obj=None):
        """Creates a Pasta and links it to Entidade, Fluxo and Ficheiro if provided."""
        pasta_obj = self.pasta.data.insert({"name": pasta_name})
        if entidade_obj:
            self.entidade.data.reference_add(entidade_obj, "hasPastas", pasta_obj)
            self.pasta.data.reference_add(pasta_obj, "hasEntidades", entidade_obj)
        if fluxo_obj:
            self.pasta.data.reference_add(pasta_obj, "hasFluxos", fluxo_obj)
        if ficheiro_obj:
            self.pasta.data.reference_add(pasta_obj, "hasFicheiros", ficheiro_obj)
        return pasta_obj

    def add_ficheiro(self, ficheiro_name, pasta_obj=None, entidade_obj=None, etapa_obj=None, metadados_obj=None):
        """Creates a Ficheiro and links it to Pasta, Entidade, Etapa and Metadados if provided."""
        ficheiro_obj = self.ficheiro.data.insert({"name": ficheiro_name})
        if pasta_obj:
            self.pasta.data.reference_add(pasta_obj, "hasFicheiros", ficheiro_obj)
        if entidade_obj:
            self.entidade.data.reference_add(entidade_obj, "hasFicheiros", ficheiro_obj)
        if etapa_obj:
            self.etapa.data.reference_add(etapa_obj, "hasFicheiros", ficheiro_obj)
        if metadados_obj:
            self.ficheiro.data.reference_add(ficheiro_obj, "belongsToMetadados", metadados_obj)
        return ficheiro_obj

    def add_metadados(self, metadados_data, ficheiro_obj=None, etapa_obj=None, pasta_obj=None, entidade_obj=None):
        """Creates Metadados and links it to Ficheiro, Etapa, Pasta and Entidade if provided."""
        metadados_obj = self.metadados.data.insert({"name": metadados_data})
        if ficheiro_obj:
            self.metadados.data.reference_add(metadados_obj, "hasFicheiros", ficheiro_obj)
        if etapa_obj:
            self.metadados.data.reference_add(metadados_obj, "hasEtapas", etapa_obj)
        if pasta_obj:
            self.metadados.data.reference_add(metadados_obj, "hasPastas", pasta_obj)
        if entidade_obj:
            self.metadados.data.reference_add(metadados_obj, "hasEntidades", entidade_obj)
        return metadados_obj
    
    def query_fluxo_etapas(self, limit=10):
        """Query Fluxos and their associated Etapas."""
        query_result = self.fluxo.query.fetch_objects(
            return_properties=["name"],
            return_references=QueryReference(
                link_on="hasEtapas",
                return_properties=["name"]
            ),
            limit=limit
        )
        
        results = []
        for obj in query_result.objects:
            fluxo_data = {
                "fluxo_name": obj.properties['name'],
                "etapas": []
            }
            
            if "hasEtapas" in obj.references:
                for etapa in obj.references["hasEtapas"].objects:
                    fluxo_data["etapas"].append(etapa.properties['name'])
            
            results.append(fluxo_data)
            
            # Print results for debugging
            print(f"Fluxo: {obj.properties['name']}")
            if "hasEtapas" in obj.references:
                for etapa in obj.references["hasEtapas"].objects:
                    print(f"  - Etapa: {etapa.properties['name']}")
            else:
                print("No 'hasEtapas' reference found for this Fluxo.")
                
        return results
    
    def query_entidade_hierarchy(self, limit=10):
        """Query Entidades and their nested hierarchy of Pastas, Ficheiros, and Metadados."""
        query_result = self.entidade.query.fetch_objects(
            return_properties=["name"],
            return_references=QueryReference(
                link_on="hasPastas",
                return_properties=["name"],
                return_references=QueryReference(
                    link_on="hasFicheiros",
                    return_properties=["name"],
                    return_references=QueryReference(
                        link_on="belongsToMetadados",
                        return_properties=["name"]
                    )
                )
            ),
            limit=limit
        )
        
        results = []
        for obj in query_result.objects:
            entidade_data = {
                "entidade_name": obj.properties['name'],
                "pastas": []
            }
            
            print(f"Entidade: {obj.properties['name']}")
            
            if "hasPastas" in obj.references:
                for pasta in obj.references["hasPastas"].objects:
                    pasta_data = {
                        "pasta_name": pasta.properties['name'],
                        "ficheiros": []
                    }
                    
                    count_ficheiros = 0
                    if "hasFicheiros" in pasta.references:
                        for ficheiro in pasta.references["hasFicheiros"].objects:
                            count_ficheiros += 1
                            ficheiro_data = {
                                "ficheiro_name": ficheiro.properties['name'],
                                "metadados": []
                            }
                            
                            if "belongsToMetadados" in ficheiro.references:
                                for meta in ficheiro.references["belongsToMetadados"].objects:
                                    ficheiro_data["metadados"].append(meta.properties['name'])
                                    print(f"      - Metadados: {meta.properties['name']}")
                            
                            pasta_data["ficheiros"].append(ficheiro_data)
                    
                    print(f"  - Pasta: {pasta.properties['name'][0:7]}", end="|")
                    print(f"- Ficheiros: {count_ficheiros}")
                    
                    entidade_data["pastas"].append(pasta_data)
            
            results.append(entidade_data)
                
        return results
    
    def global_semantic_search(self, query_text, alpha=0.2, limit_per_collection=5):
        """Perform a global semantic search across all collections."""
        results = []
        
        for collection_name in ["Pasta", "Fluxo", "Etapa", "Metadados", "Ficheiro", "Entidade"]:
            collection = self.client.collections.get(collection_name)

            search_results = collection.query.hybrid(
                query=query_text,  
                alpha=alpha,  # Set alpha for balanced results
                return_properties=["name"],  # Return these properties
                return_metadata=MetadataQuery(score=True),  # Return relevance score
                limit=limit_per_collection,  # Get top results per collection
            )

            # Store results with class name
            for obj in search_results.objects:
                results.append({
                    "class": collection_name,
                    "name": obj.properties["name"],
                    "score": obj.metadata.score,
                    "metadados": obj.properties.get("metadados", {})
                })

        # Sort results by relevance score (higher is better)
        results.sort(key=lambda x: x["score"], reverse=True)

        # Display results
        for result in results:
            print(f"[{result['class']}] {result['name']} (Score: {result['score']})")
            print(f"  Metadata: {result['metadados']}")
            
        return results
    
    def close(self):
        """Close the Weaviate client connection."""
        self.client.close()


def main():
    """Main function to demonstrate the workflow."""
    # Initialize the manager
    manager = WeaviateDataManager()
    
    try:
        # Setup the collections
        print("Setting up collections...")
        manager.setup_collections(clean_start=True)
        
        # Insert sample data
        print("Inserting sample data...")
        data_objects = manager.insert_sample_data(
            num_entidades=2,
            num_pastas_per_entidade=5,
            num_ficheiros_per_pasta=8,
            num_metadados_per_ficheiro=1,
            num_fluxos=5,
            num_etapas_per_fluxo=10
        )
        
        # Run test queries
        print("\nRunning test queries...")
        print("\n1. Querying Fluxos and their Etapas:")
        manager.query_fluxo_etapas(limit=3)
        
        print("\n2. Querying Entidade hierarchy:")
        manager.query_entidade_hierarchy(limit=2)
        
        print("\n3. Running global semantic search:")
        manager.global_semantic_search("Find documents about contract approvals", limit_per_collection=3)
        
    finally:
        # Close the connection
        manager.close()
        print("\nConnection closed.")


if __name__ == "__main__":
    main()