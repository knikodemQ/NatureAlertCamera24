from ultralytics import YOLO
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "best.pt")

# Wczytaj model
# model = YOLO("wages/best.pt")
model = YOLO(model_path)  


model.model.names = {
    0: "buffalo",
    1: "elephant",
    2: "rino",
    3: "zebra",
    4: "giraffe",
    5: "lion",
    6: "hippo",
    7: "antelope",
    8: "person"
}

# Wykonaj detekcję na wideo

# results = model(source="wages/animals.mp4", show=True, conf=0.3, save=True, project="output", name="my_video")

results = model(source=0, show=True, conf=0.3, save=False, project="output", name="my_video")

# model.predict(source=0, show=True, conf=0.3, save=False, project="output", name="my_video")
# model.predict(source="wages/animals.mp4", show=True, conf=0.3, save=False, project="output", name="my_video")
# model.predict(source="wages/savana.mp4", show=True, conf=0.3, save=False, project="output", name="my_video")
 


