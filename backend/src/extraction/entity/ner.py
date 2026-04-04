from gliner import GLiNER
import torch

# we define a class for NER extraction so that we can 
# easily swap out the underlying NER model if needed. 
# The extract function takes in the text and the labels to extract and returns the identified entities.

class BiomedicalNER:
    def __init__(self, model_path="Ihor/gliner-biomed-base-v1.0"):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = GLiNER.from_pretrained(model_path).to(device)

    def extract(self, text, labels):
        return self.model.predict_entities(text, labels)