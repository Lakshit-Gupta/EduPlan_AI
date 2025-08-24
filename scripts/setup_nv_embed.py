import torch
from transformers import AutoModel, AutoTokenizer

def setup_nv_embed(model_name="nvidia/NV-Embed-v2"):
    """Download and verify NV-Embed model"""
    print(f"Downloading and verifying {model_name}...")
    
    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    
    # Check device availability
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    
    # Print model info
    print(f"Model loaded successfully on {device}!")
    print(f"Model type: {type(model).__name__}")
    print(f"Tokenizer type: {type(tokenizer).__name__}")
    print(f"Model size: {sum(p.numel() for p in model.parameters())/1e6:.2f}M parameters")
    
    return model, tokenizer

if __name__ == "__main__":
    model, tokenizer = setup_nv_embed()
    
    # Test with a simple input
    text = "This is a test for NVIDIA NV-Embed model."
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    print("✅ Model inference successful!")
    print(f"Output shape: {outputs.last_hidden_state.shape}")
    print("Setup complete!")
