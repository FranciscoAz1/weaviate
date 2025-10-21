from weaviate.classes.query import QueryReference, MetadataQuery
from weaviate_manager import WeaviateManager

class DataQueries(WeaviateManager):
    """Class for querying data from Weaviate collections."""
    
    def query_fluxo_etapas(self, limit=10):
        """Query Fluxos and their associated Etapas."""
        # Make sure collection objects are loaded
        self._get_collection_objects()
        
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
        # Make sure collection objects are loaded
        self._get_collection_objects()
        
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
        # Make sure collection objects are loaded
        self._get_collection_objects()
        
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
            # print(f"  Metadata: {result['metadados']}")
            
        return results
