import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
import torchvision.datasets as datasets
import torchvision.models as models
from torch.utils.data import DataLoader

print("Loading dataset...")

data_dir = "PlantVillage"

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

dataset = datasets.ImageFolder(root=data_dir, transform=transform)

print("Total images:", len(dataset))
print("Classes:", dataset.classes)

train_loader = DataLoader(
    dataset,
    batch_size=8,   # SMALL batch for CPU
    shuffle=True
)

print("Loading MobileNet...")

model = models.mobilenet_v2(weights="DEFAULT")

num_classes = len(dataset.classes)
model.classifier[1] = nn.Linear(model.last_channel, num_classes)

device = torch.device("cpu")
model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

epochs = 1   # ONLY 1 epoch for hackathon

print("Starting training...")

for epoch in range(epochs):
    model.train()
    running_loss = 0.0

    for i, (images, labels) in enumerate(train_loader):
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

        if i % 20 == 0:
            print(f"Batch {i}/{len(train_loader)} - Loss: {loss.item():.4f}")

    print(f"Epoch [{epoch+1}/{epochs}] Loss: {running_loss:.4f}")

print("Saving model...")
torch.save(model.state_dict(), "pest_model.pth")
torch.save(dataset.classes, "class_names.pth")

print("✅ Training finished and model saved!")