import argparse
import re

from kserve import (
    InferOutput,
    InferRequest,
    InferResponse,
    Model,
    ModelServer,
    model_server,
)
from kserve.utils.utils import generate_uuid
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, NllbTokenizerFast, BitsAndBytesConfig
import torch


DIR = "saved_model"
CHARS_TO_REMOVE_REGEX = '[!"&\(\),-./:;=?+.\n\[\]]'
MODEL_KWARGS = {
    "do_sample": True,
    "max_new_tokens": 40,
    "top_k": 30,
    "top_p": 0.95,
    "temperature": 1.0,
}

# cleaning the datas (remove punctuation and lowercase everything)
def remove_special_characters(text):
    text = re.sub(CHARS_TO_REMOVE_REGEX, " ", text.lower())
    return text.strip()

def clean_text(text: str) -> str:
    """
    Clean input text by removing special characters and converting
    to lower case.
    """
    text = re.sub(CHARS_TO_REMOVE_REGEX, " ", text.lower())
    return text.strip()


class MyModel(Model):
    """Kserve inference implementation of model."""

    def __init__(self, name: str):
        """Initialise model."""
        super().__init__(name)
        self.name = name
        self.model = None
        self.tokenizer = None
        self.ready = False
        self.load()

    def load(self):
        """Reconstitute model from disk."""
        config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            device_map="auto"
        )
        # Load tokenizer
        self.tokenizer = NllbTokenizerFast.from_pretrained(DIR)
        # Load 4-bit quantized model
        self.model = AutoModelForSeq2SeqLM.from_pretrained(DIR, low_cpu_mem_usage=True, torch_dtype="auto", quantization_config=config)
        self.ready = True

    def preprocess(self, payload: InferRequest, *args, **kwargs) -> str:
        """Preprocess inference request."""
        # Clean input sentence and add prefix
        raw_data = payload.inputs[0].data[0]
        prepared_data = f"{clean_text(raw_data)}"
        return prepared_data

    def predict(self, data: str, *args, **kwargs) -> InferResponse:
        """Pass inference request to model to make prediction."""
        # Model prediction preprocessed sentence
        inference_input = self.tokenizer(data, return_tensors="pt").input_ids
        output = self.model.generate(inference_input, **MODEL_KWARGS)
        translation = self.tokenizer.decode(output[0], skip_special_tokens=True)
        response_id = generate_uuid()
        infer_output = InferOutput(
            name="output-0", shape=[1], datatype="STR", data=[translation]
        )
        infer_response = InferResponse(
            model_name=self.name, infer_outputs=[infer_output], response_id=response_id
        )
        return infer_response


parser = argparse.ArgumentParser(parents=[model_server.parser])
parser.add_argument(
    "--model_name", 
    default="model", 
    help="The name that the model is served under."
)
args, _ = parser.parse_known_args()

if __name__ == "__main__":
    model = MyModel(args.model_name)
    ModelServer().start([model])
