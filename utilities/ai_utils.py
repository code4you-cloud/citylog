import torch
from torchvision import transforms
from PIL import Image
import json

# Caricare un modello pre-addestrato (es. ResNet)
model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet18', pretrained=True)
model.eval()

# Classi definite per CityLog (da migliorare con addestramento personalizzato)
CLASSES = ["rifiuti", "buche stradali", "illuminazione", "verde pubblico", "altro"]

def classify_image(image_path):
    """Classifica un'immagine di segnalazione in una categoria."""
    image = Image.open(image_path).convert("RGB")

    # Trasformazioni per il modello
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])

    image = transform(image).unsqueeze(0)

    with torch.no_grad():
        outputs = model(image)

    predicted_class = CLASSES[outputs.argmax().item()]
    return predicted_class

