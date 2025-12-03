from weaviate_manager_fail import WeaviateManager

class DataInsertion(WeaviateManager):
    """Class for inserting data into Weaviate collections."""
    
    def insert_sample_data(self, num_entidades=2, num_pastas_per_entidade=5, 
                           num_ficheiros_per_pasta=8, num_metadados_per_ficheiro=1,
                           num_fluxos=5, num_etapas_per_fluxo=10):
        """Insert sample data into all collections with proper references."""
        # Make sure collection objects are loaded
        self._get_collection_objects()
        
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

    def add_ficheiro(self, ficheiro_name,content=None, pasta_obj=None, entidade_obj=None, etapa_obj=None, metadados_obj=None):
        """Creates a Ficheiro and links it to Pasta, Entidade, Etapa and Metadados if provided."""
        properties = {"name": ficheiro_name}
        if content:
            properties["content"] = content

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

    def add_document_with_extracted_text(self, pdf_path, entity_name=None, pasta_name=None):
        """
        Extract text from a PDF document and add it to the Weaviate database.
        
        Args:
            pdf_path (str): Path to the PDF file
            entity_name (str, optional): Name of the entity to associate with the document
            pasta_name (str, optional): Name of the folder to place the document in
            
        Returns:
            dict: Object references for the created entities
        """
        # Make sure collection objects are loaded
        self._get_collection_objects()
        
        # Extract filename from path
        from pathlib import Path
        filename = Path(pdf_path).stem
        
        # Create entity if not exists
        if entity_name:
            # Check if entity exists
            query_result = self.entidade.query.fetch_objects(
                where={"path": ["name"], "operator": "Equal", "valueText": entity_name},
                limit=1
            )
            
            if query_result.objects:
                entidade_obj = query_result.objects[0].uuid
            else:
                entidade_obj = self.add_entidade(entity_name)
        else:
            # Create default entity
            entidade_obj = self.add_entidade(f"Entity for {filename}")
        
        # Create pasta if not exists
        if pasta_name:
            # Check if pasta exists
            query_result = self.pasta.query.fetch_objects(
                where={"path": ["name"], "operator": "Equal", "valueText": pasta_name},
                limit=1
            )
            
            if query_result.objects:
                pasta_obj = query_result.objects[0].uuid
            else:
                pasta_obj = self.add_pasta(pasta_name, entidade_obj=entidade_obj)
        else:
            # Create default pasta
            pasta_obj = self.add_pasta(f"Folder for {filename}", entidade_obj=entidade_obj)
        
        # Extract text from PDF using the provided code
        import io
        import fitz
        import torch
        from PIL import Image
        from transformers import AutoProcessor, VisionEncoderDecoderModel, StoppingCriteria, StoppingCriteriaList
        from collections import defaultdict
        
        # Use existing processor and model (assuming they're already loaded)
        # If not, this code would need to load them
        try:
            processor
            model
            device
        except NameError:
            # Load model and processor if not already loaded
            processor = AutoProcessor.from_pretrained("facebook/nougat-small")
            model = VisionEncoderDecoderModel.from_pretrained("facebook/nougat-small")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model.to(device)
        
        # Define the necessary classes (from your code)
        class RunningVarTorch:
            def __init__(self, L=15, norm=False):
                self.values = None
                self.L = L
                self.norm = norm
                
            def push(self, x: torch.Tensor):
                assert x.dim() == 1
                if self.values is None:
                    self.values = x[:, None]
                elif self.values.shape[1] < self.L:
                    self.values = torch.cat((self.values, x[:, None]), 1)
                else:
                    self.values = torch.cat((self.values[:, 1:], x[:, None]), 1)
                    
            def variance(self):
                return torch.var(self.values, 1) if self.values is not None else None

        class StoppingCriteriaScores(StoppingCriteria):
            def __init__(self, threshold: float = 0.015, window_size: int = 200):
                super().__init__()
                self.threshold = threshold
                self.vars = RunningVarTorch(norm=True)
                self.varvars = RunningVarTorch(L=window_size)
                self.stop_inds = defaultdict(int)
                self.stopped = defaultdict(bool)
                self.size = 0
                self.window_size = window_size
                
            @torch.no_grad()
            def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor):
                last_scores = scores[-1]
                self.vars.push(last_scores.max(1)[0].float().cpu())
                self.varvars.push(self.vars.variance())
                self.size += 1
                
                if self.size < self.window_size:
                    return False
                    
                varvar = self.varvars.variance()
                for b in range(len(last_scores)):
                    if varvar[b] < self.threshold:
                        self.stop_inds[b] = int(min(max(self.size, 1) * 1.15 + 150 + self.window_size, 4095))
                        self.stopped[b] = self.stop_inds[b] >= self.size
                    else:
                        self.stop_inds[b] = 0
                        self.stopped[b] = False
                        
                return all(self.stopped.values()) and len(self.stopped) > 0
        
        # Function to convert PDF to images
        def rasterize_paper(pdf_path, dpi: int = 96):
            """Converts a PDF to a list of images."""
            images = []
            pdf_doc = fitz.open(pdf_path)
            for page in pdf_doc:
                img_bytes = page.get_pixmap(dpi=dpi).pil_tobytes(format="PNG")
                images.append(io.BytesIO(img_bytes))
            return images
        
        # Process the PDF
        images = rasterize_paper(pdf_path)
        
        # Extract text from each page
        extracted_text = ""
        for idx, img_bytes in enumerate(images):
            img = Image.open(io.BytesIO(img_bytes.getvalue()))
            pixel_values = processor(images=img, return_tensors="pt").pixel_values.to(device)
            
            outputs = model.generate(
                pixel_values,
                min_length=1,
                max_length=3584,
                bad_words_ids=[[processor.tokenizer.unk_token_id]],
                return_dict_in_generate=True,
                output_scores=True,
                stopping_criteria=StoppingCriteriaList([StoppingCriteriaScores()]),
            )
            
            generated_text = processor.batch_decode(outputs[0], skip_special_tokens=True)[0]
            generated_text = processor.post_process_generation(generated_text, fix_markdown=False)
            extracted_text += f"Page {idx + 1}:\n{generated_text}\n\n"
        
        # Create ficheiro with the extracted text
        ficheiro_obj = self.ficheiro.data.insert({
            "name": filename,
            "content": extracted_text,  # Store the extracted text
            "source_path": str(pdf_path)
        })
        
        # Link ficheiro to pasta and entidade
        self.pasta.data.reference_add(pasta_obj, "hasFicheiros", ficheiro_obj)
        self.entidade.data.reference_add(entidade_obj, "hasFicheiros", ficheiro_obj)
        
        # Create metadata for the document
        metadados_obj = self.add_metadados(f"Metadata for {filename}", ficheiro_obj=ficheiro_obj)
        
        print(f"Document '{filename}' added successfully with extracted text")
        
        return {
            "entidade": entidade_obj,
            "pasta": pasta_obj,
            "ficheiro": ficheiro_obj,
            "metadados": metadados_obj
        }