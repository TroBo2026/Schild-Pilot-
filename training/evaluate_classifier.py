"""Evaluate a trained classifier on a separate ImageFolder test split."""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets,models,transforms
from core.decision import decide_prediction

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--data",type=Path,default=Path("data/signs/test"))
    p.add_argument("--model-dir",type=Path,default=Path("artifacts/sign_classifier"))
    p.add_argument("--output",type=Path,default=Path("artifacts/evaluation"))
    p.add_argument("--batch-size",type=int,default=32)
    p.add_argument("--min-score",type=float,default=0.45)
    p.add_argument("--min-margin",type=float,default=0.10)
    p.add_argument("--thresholds",type=Path,default=None,
                   help="JSON aus training.calibrate_thresholds; falls nicht angegeben, wird model-dir/calibrated_thresholds.json verwendet.")
    a=p.parse_args()
    if a.batch_size<1: raise SystemExit("--batch-size muss positiv sein.")
    mp=a.model_dir/"metadata.json"; wp=a.model_dir/"best_model.pth"
    if not a.data.is_dir() or not mp.is_file() or not wp.is_file():
        raise SystemExit("Testdaten oder trainiertes Modell/Metadaten fehlen.")
    metadata=json.loads(mp.read_text(encoding="utf-8")); classes=metadata.get("classes")
    threshold_path=a.thresholds or (a.model_dir/"calibrated_thresholds.json")
    threshold_source="command_line" if a.thresholds else "model_dir_default"
    if threshold_path.is_file():
      thresholds=json.loads(threshold_path.read_text(encoding="utf-8"))
      a.min_score=float(thresholds["min_score"]); a.min_margin=float(thresholds["min_margin"])
    else:
      threshold_source="fixed_cli_defaults"
    if not isinstance(classes,list) or not classes: raise SystemExit("Ungültige Klassenliste.")
    ds=datasets.ImageFolder(a.data,transform=transforms.Compose([
      transforms.Resize((int(metadata.get("image_size",224)),)*2),transforms.ToTensor(),
      transforms.Normalize((0.485,0.456,0.406),(0.229,0.224,0.225))]))
    if ds.classes!=classes: raise SystemExit("Testklassen oder Klassenreihenfolge stimmen nicht überein.")
    if not len(ds): raise SystemExit("Der Testdatensatz ist leer.")
    model=models.resnet18(weights=None); model.fc=nn.Linear(model.fc.in_features,len(classes))
    model.load_state_dict(torch.load(wp,map_location="cpu",weights_only=True)); model.eval()
    loader=DataLoader(ds,batch_size=a.batch_size,shuffle=False,num_workers=0)
    confusion=[[0 for _ in classes] for _ in classes]
    accepted=correct_accepted=total=abstained=top5_correct=0
    with torch.inference_mode():
      for images,labels in loader:
        probs=torch.softmax(model(images),dim=1)
        top5=probs.topk(min(5,len(classes)),dim=1).indices
        top5_correct+=(top5==labels.unsqueeze(1)).any(dim=1).sum().item()
        for row,truth in zip(probs.tolist(),labels.tolist()):
          decision=decide_prediction(row,classes,min_score=a.min_score,min_margin=a.min_margin)
          candidate=classes.index(decision["candidate"]); confusion[truth][candidate]+=1; total+=1
          if decision["status"]=="accepted":
            accepted+=1
            if candidate==truth: correct_accepted+=1
          else: abstained+=1
    class_metrics=[]
    for i,name in enumerate(classes):
      support=sum(confusion[i]); correct=confusion[i][i]
      class_metrics.append({"class":name,"samples":support,"top1_correct":correct,
                            "top1_accuracy":correct/support if support else None})
    supported=[x["top1_accuracy"] for x in class_metrics if x["top1_accuracy"] is not None]
    metrics={"samples":total,"classes":len(classes),
      "top1_accuracy_before_abstention":sum(confusion[i][i] for i in range(len(classes)))/total,
      "top5_accuracy":top5_correct/total,
      "macro_top1_accuracy":sum(supported)/len(supported) if supported else None,
      "accepted_predictions":accepted,"abstained_predictions":abstained,
      "coverage":accepted/total,"accuracy_on_accepted":correct_accepted/accepted if accepted else None,
      "min_score":a.min_score,"min_margin":a.min_margin,"threshold_source":threshold_source,
      "note":"Scores are not calibrated safety probabilities. Research evaluation only."}
    a.output.mkdir(parents=True,exist_ok=True)
    (a.output/"metrics.json").write_text(json.dumps(metrics,indent=2,ensure_ascii=False),encoding="utf-8")
    (a.output/"per_class_metrics.json").write_text(json.dumps(class_metrics,indent=2,ensure_ascii=False),encoding="utf-8")
    with (a.output/"confusion_matrix.csv").open("w",newline="",encoding="utf-8") as stream:
      writer=csv.writer(stream); writer.writerow(["true/predicted",*classes])
      for name,values in zip(classes,confusion): writer.writerow([name,*values])
    print(json.dumps(metrics,indent=2,ensure_ascii=False))
    print("Auswertung gespeichert: metrics.json, per_class_metrics.json, confusion_matrix.csv")

if __name__=="__main__": main()
