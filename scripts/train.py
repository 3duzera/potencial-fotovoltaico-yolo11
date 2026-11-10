"""Reproduce the training run (YOLO11n-seg, single class "telhado").

Download the dataset from Roboflow Universe (YOLOv11 format) and pass its data.yaml:
    python scripts/train.py --data path/to/data.yaml
"""
import argparse

from ultralytics import YOLO


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="dataset data.yaml")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=1024)
    args = parser.parse_args()

    model = YOLO("yolo11n-seg.pt")  # COCO-pretrained
    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        patience=8,
        batch=-1,          # auto batch size for the available GPU memory
        single_cls=True,   # "Inclinado" and "Reto" merged into one roof class
    )
    model.val(split="test")


if __name__ == "__main__":
    main()
