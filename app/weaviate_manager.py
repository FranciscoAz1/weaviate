from socket import timeout
import weaviate
from weaviate.classes.config import Property, DataType, ReferenceProperty, Configure
from weaviate.classes.init import AdditionalConfig, Timeout


class WeaviateManager:
    """Base manager class for Weaviate operations."""
    
    # Define Ollama API details
    OLLAMA_API_ENDPOINT = "http://host.docker.internal:11434"
    VECTOR_MODEL = "mxbai-embed-large"
    GENERATION_MODEL = "llama3.2"
    
    def __init__(self, connect_to_local=True):
        """Initialize the Weaviate client connection."""
        if connect_to_local:
            self.client = weaviate.connect_to_local(
                additional_config=AdditionalConfig(
                    timeout=Timeout(init=30, query=30, insert=600)
                )
            )
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
    
    def _get_collection_objects(self):
        """Get references to all collection objects."""
        self.fluxo = self.client.collections.get("Fluxo")
        self.etapa = self.client.collections.get("Etapa")
        self.entidade = self.client.collections.get("Entidade")
        self.pasta = self.client.collections.get("Pasta")
        self.ficheiro = self.client.collections.get("Ficheiro")
        self.metadados = self.client.collections.get("Metadados")
    
    def close(self):
        """Close the Weaviate client connection."""
        self.client.close()
