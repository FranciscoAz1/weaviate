from weaviate.classes.config import Property, DataType, ReferenceProperty, Configure
from weaviate_manager_fail import WeaviateManager

class CollectionSetup(WeaviateManager):
    """Class for setting up Weaviate collections and references."""
    
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
                Configure.NamedVectors.text2vec_ollama(
                    name="title_vector",
                    source_properties=["name"],
                    api_endpoint=self.OLLAMA_API_ENDPOINT,
                    model=self.VECTOR_MODEL
                )
            ],
            generative_config=Configure.Generative.ollama(
                api_endpoint=self.OLLAMA_API_ENDPOINT,
                model=self.GENERATION_MODEL
            )
        )
    
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
