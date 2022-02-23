import os
import base64
import pandas as pd
import numpy as np
import pickle
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from dr_deployment_prediction import main


# Function to prepare image into a format that can be accepted by datarobot
def convert_image_to_base64(image):
    img_bytes = BytesIO()
    image.save(img_bytes, 'jpeg', quality = 90)
    image_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
    return image_base64

def convert_image_to_csv(input_file):
  image = Image.open(input_file)

  # Convert image to base64
  image_base64 = convert_image_to_base64(image)
  
  # Build a CSV with a single row that contains an image
  df = pd.DataFrame({"image": [image_base64]})
  df.to_csv("dog_image.csv", index = False)
  return(image)

# Function to run the selected DR pet model
def get_dr_predictions(filename,
                       deployment_id):
  _ = main(filename, deployment_id)
  
  # Get predictions
  with open("predictions.pickle", "rb") as p:
    predictions = pickle.load(p)
  return(predictions)


  
# Function to convert the top 3 predictions into a string
def get_predictions_string(result):
  result_dict = pd.read_pickle("predictions.pickle")
  result_df = pd.DataFrame(result_dict["data"][0]["predictionValues"])\
                .rename(columns = {"label": "pred_breed",
                                   "value": "predictions"})\
                .sort_values(by = "predictions",
                             ascending= False)\
                .iloc[:3, :]
  
  # Get top 3 predicted dog breeds
  labels = result_df["pred_breed"].tolist()
  values = result_df["predictions"].tolist()
  
  # Create a string with the 3 top predictions
  if values[0] > 0.75:
    dog_string = "I am {:.1%} confident that this dog is a {}".format(values[0], labels[0])
  elif values[0] > 0.5:
    dog_string = "With {:.1%} confidence, I think this dog is a {}, but it's possible that it could also be a {} ({:.1%}) or a {} ({:.1%})!".format(values[0], labels[0], labels[1], values[1], labels[2], values[2])
  else:
    dog_string = "With only {:.1%} confidence I am unsure of this dog's breed. It looks like a {},\n but could also be a {} ({:.1%}) or a {} ({:.1%})!".format(values[0], labels[0], labels[1], values[1], labels[2], values[2])
  return(dog_string.replace("_", " "), labels, values)




def classify_dog(input_file,
                 intermediate_file = "dog_image.csv",
                 deployment_id = "62013daff030fa52feb30679"):
  # Convert image to csv to feed to DR
  image = convert_image_to_csv(input_file = input_file)

  # Run the selected DR pet model
  result = get_dr_predictions(filename = intermediate_file,
                              deployment_id = deployment_id)
  
  # Convert the top 3 predictions into a string
  dog_string, labels, values = get_predictions_string(result = result)
  return(image, dog_string, labels, values)

