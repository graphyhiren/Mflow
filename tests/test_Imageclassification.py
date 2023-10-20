
import mlflow
import os
from mlflow import pyfunc
from datasets import load_dataset
from transformers import ViTImageProcessor,ViTForImageClassification
def vision_model_save():
    model_name="facebook/deit-base-patch16-224"
    path= "facebook_deit_base_patch16_224"
    print(os.path.exists(path))
    if not (os.path.exists(path)):
       image_processor = ViTImageProcessor.from_pretrained(Model_name)
       model = ViTForImageClassification.from_pretrained(Model_name)
       components={"model": model,"image_processor":image_processor}
       mlflow.transformers.save_model(
                transformers_model=components,
                path=path,
        )
    return  path 
def load_mlmodel():
    path=vision_model_save()
    
    model = mlflow.pyfunc.load_model(path)
    url = 'http://images.cocodataset.org/val2017/000000039769.jpg'
    result=model.predict(url)
    
    return result

