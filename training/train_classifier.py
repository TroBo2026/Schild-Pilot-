"""Fine-tune a ResNet18 classifier on already-cropped traffic-sign images."""
from __future__ import annotations
import argparse, json, random
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument("--data",type=Path,default=Path("data/signs"))
    p.add_argument("--output",type=Path,default=Path("artifacts/sign_classifier"))
    p.add_argument("--epochs",type=int,default=8)
    p.add_argument("--batch-size",type=int,default=32)
    p.add_argument("--image-size",type=int,default=160)
    p.add_argument("--workers",type=int,default=2)
    p.add_argument("--seed",type=int,default=20261113)
    p.add_argument("--patience",type=int,default=3)
    return p.parse_args()

def main():
    a=parse_args()
    if min(a.epochs,a.batch_size,a.image_size,a.patience)<1:
        raise SystemExit("Epochen, Batchgröße, Bildgröße und Geduld müssen positiv sein.")
    random.seed(a.seed); np.random.seed(a.seed); torch.manual_seed(a.seed)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(a.seed)
    train_dir,val_dir=a.data/"train",a.data/"val"
    if not train_dir.is_dir() or not val_dir.is_dir():
        raise SystemExit(f"Erwartet werden {train_dir} und {val_dir}.")
    mean,std=(0.485,0.456,0.406),(0.229,0.224,0.225)
    train_tf=transforms.Compose([
        transforms.Resize((a.image_size,a.image_size)),
        transforms.RandomRotation(10),
        transforms.RandomAffine(degrees=0,translate=(0.06,0.06),scale=(0.90,1.10)),
        transforms.ColorJitter(brightness=0.18,contrast=0.18,saturation=0.12,hue=0.02),
        transforms.ToTensor(),transforms.Normalize(mean,std)])
    eval_tf=transforms.Compose([
        transforms.Resize((a.image_size,a.image_size)),
        transforms.ToTensor(),transforms.Normalize(mean,std)])
    train_ds=datasets.ImageFolder(train_dir,transform=train_tf)
    val_ds=datasets.ImageFolder(val_dir,transform=eval_tf)
    if train_ds.classes!=val_ds.classes: raise SystemExit("Train- und Val-Klassen stimmen nicht überein.")
    if not len(train_ds) or not len(val_ds): raise SystemExit("Train- und Val-Ordner dürfen nicht leer sein.")
    device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
    kw={"num_workers":a.workers,"pin_memory":device.type=="cuda"}
    train_loader=DataLoader(train_ds,batch_size=a.batch_size,shuffle=True,**kw)
    val_loader=DataLoader(val_ds,batch_size=a.batch_size,shuffle=False,**kw)
    model=models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    for p in model.parameters(): p.requires_grad=False
    for p in model.layer4.parameters(): p.requires_grad=True
    model.fc=nn.Linear(model.fc.in_features,len(train_ds.classes))
    model=model.to(device)
    optimizer=torch.optim.AdamW([
        {"params":model.layer4.parameters(),"lr":1e-4},
        {"params":model.fc.parameters(),"lr":5e-4}],weight_decay=1e-4)
    scheduler=torch.optim.lr_scheduler.CosineAnnealingLR(optimizer,T_max=a.epochs)
    loss_fn=nn.CrossEntropyLoss(label_smoothing=0.05)
    best=-1.0; best_epoch=0; stale=0; history=[]
    a.output.mkdir(parents=True,exist_ok=True)
    for epoch in range(a.epochs):
        model.train()
        for layer in (model.conv1,model.bn1,model.layer1,model.layer2,model.layer3): layer.eval()
        loss_sum=0.0; correct=total=0
        for images,labels in train_loader:
            images,labels=images.to(device),labels.to(device)
            optimizer.zero_grad(set_to_none=True)
            logits=model(images); loss=loss_fn(logits,labels)
            loss.backward(); optimizer.step()
            loss_sum+=loss.item()*images.size(0)
            correct+=(logits.argmax(1)==labels).sum().item(); total+=labels.size(0)
        model.eval(); val_correct=val_total=0
        with torch.inference_mode():
            for images,labels in val_loader:
                images,labels=images.to(device),labels.to(device)
                val_correct+=(model(images).argmax(1)==labels).sum().item()
                val_total+=labels.size(0)
        accuracy=val_correct/max(val_total,1)
        row={"epoch":epoch+1,"train_loss":loss_sum/max(total,1),
             "train_accuracy":correct/max(total,1),"validation_accuracy":accuracy}
        history.append(row)
        print(f"Epoch {epoch+1}/{a.epochs} | loss={row['train_loss']:.4f} | train_accuracy={row['train_accuracy']:.4f} | val_accuracy={accuracy:.4f}",flush=True)
        if accuracy>best:
            best=accuracy; best_epoch=epoch+1; stale=0
            torch.save(model.state_dict(),a.output/"best_model.pth")
        else: stale+=1
        scheduler.step()
        if stale>=a.patience:
            print(f"Early stopping nach Epoche {epoch+1}.",flush=True); break
    metadata={"architecture":"resnet18","classes":train_ds.classes,"image_size":a.image_size,
      "validation_accuracy":best,"best_epoch":best_epoch,"epochs_completed":len(history),
      "task":"classification_of_cropped_signs","pretrained_weights":"ResNet18_Weights.DEFAULT",
      "fine_tuned_layers":["layer4","fc"],"seed":a.seed,"history":history,
      "limitations":["Synthetic German dataset only.","Classification, not full-scene detection.",
                     "Not validated for real roads or safety-critical use."]}
    (a.output/"metadata.json").write_text(json.dumps(metadata,indent=2,ensure_ascii=False),encoding="utf-8")
    print(f"Bestes Validierungsergebnis: {best:.4f} (Epoche {best_epoch})")
    print("Testdaten wurden nicht zur Modellauswahl verwendet.")
    print("Forschungsprototyp; keine Fahrzeug- oder Sicherheitsfreigabe.")

if __name__=="__main__": main()
