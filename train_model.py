"""
CNN Model Training Script for Forgery Image Detection
Trained on paired datasets using PyTorch with Error Level Analysis & Deep Convolutional Layers.
"""
import os
import sys
import time
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# Add current directory to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from detector.cnn_engine import ForgeryCNN

def train(epochs=5, batch_size=16, learning_rate=0.0003):
    print("=" * 65)
    print("[TRAINING] 25-Layer Deep CNN for Image Forgery Detection")
    print("=" * 65)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}")

    # Data transformations
    train_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.1, contrast=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    test_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    train_dir = os.path.join(BASE_DIR, 'dataset', 'train')
    test_dir = os.path.join(BASE_DIR, 'dataset', 'test')

    if not os.path.exists(train_dir):
        print("Training dataset not found. Generating synthetic dataset first...")
        from generate_dataset import create_synthetic_dataset
        create_synthetic_dataset()

    train_dataset = datasets.ImageFolder(train_dir, transform=train_transforms)
    test_dataset = datasets.ImageFolder(test_dir, transform=test_transforms)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    print(f"Dataset classes: {train_dataset.classes}")
    print(f"Train samples: {len(train_dataset)} | Test samples: {len(test_dataset)}")

    # Model Initialization
    model = ForgeryCNN(num_classes=2).to(device)
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Model Architecture: 25-Layer Deep ConvNet | Trainable Parameters: {total_params:,}")

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    start_time = time.time()

    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        scheduler.step()
        epoch_loss = running_loss / total
        train_acc = (correct / total) * 100.0

        # Validation
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for images, labels in test_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)

                val_loss += loss.item() * images.size(0)
                _, predicted = torch.max(outputs, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()

        val_loss = val_loss / val_total
        val_acc = (val_correct / val_total) * 100.0

        print(f"Epoch [{epoch}/{epochs}] - Train Loss: {epoch_loss:.4f} | Train Acc: {train_acc:.1f}% | Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.1f}%")

    elapsed = time.time() - start_time
    print("-" * 65)
    print(f"[OK] Training completed in {elapsed:.1f} seconds. Final Val Accuracy: {val_acc:.1f}%")

    # Save model weights
    save_path = os.path.join(BASE_DIR, 'forgery_cnn_model.pth')
    torch.save(model.state_dict(), save_path)
    print(f"[SAVED] Trained model saved to: {save_path}")

    return save_path

if __name__ == '__main__':
    train(epochs=4, batch_size=16)
