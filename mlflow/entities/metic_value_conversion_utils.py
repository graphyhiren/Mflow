import sys

def is_module_imported(module_name: str) -> bool:
    return module_name in sys.modules

def __converter_requires(func, module_name: str):  
    def wrap(x):
        if not is_module_imported(module_name):
            return x
        
        return func(x)

    return wrap

def convert_metric_value_to_str_if_possible(x) -> str:
    if type(x) == str:
        return x
    
    converter_fns_to_try = [convert_metric_value_to_str_if_pyspark_mlparam, convert_metric_value_to_str_if_ndarray, convert_metric_value_to_str_if_tensorflow_tensor, convert_metric_value_to_str_if_torch_tensor]

    for converter_fn in converter_fns_to_try:
        possible_str = converter_fn(x)
        if type(possible_str) == str:
            return possible_str

    return str(x)

def convert_metric_value_to_float_if_possible(x) -> float:
    if type(x) == float:
        return x
    
    converter_fns_to_try = [convert_metric_value_to_float_if_ndarray, convert_metric_value_to_float_if_tensorflow_tensor, convert_metric_value_to_float_if_torch_tensor]

    for converter_fn in converter_fns_to_try:
        possible_float = converter_fn(x)
        if type(possible_float) == float:
            return possible_float

    return float(x)

@__converter_requires("pyspark.ml")
def convert_metric_value_to_str_if_pyspark_mlparam(x):
    import pyspark.ml.param

    if isinstance(x, pyspark.ml.param.Param):
        return x.name

    return x

@__converter_requires("numpy")
def convert_metric_value_to_str_if_ndarray(x):
    import numpy as np

    if isinstance(x, np.ndarray):
        return str(x.tolist())

    return x

@__converter_requires("numpy")
def convert_metric_value_to_float_if_ndarray(x):
    import numpy as np

    if isinstance(x, np.ndarray):
        return float(x.item())

    return x

@__converter_requires("torch")
def convert_metric_value_to_float_if_torch_tensor(x):
    import torch

    if isinstance(x, torch.Tensor):
        extracted_tensor_val = x.detach().cpu().item()
        return float(extracted_tensor_val)

    return x

@__converter_requires("torch")
def convert_metric_value_to_str_if_torch_tensor(x):
    import torch

    if isinstance(x, torch.Tensor):
        extracted_ndarray = x.detach().cpu().numpy()
        return convert_metric_value_to_float_if_ndarray(extracted_ndarray)

    return x

@__converter_requires("tensorflow")
def convert_metric_value_to_float_if_tensorflow_tensor(x):
    import tensorflow as tf

    if isinstance(x, tf.Tensor):
        return float(x)

    return x

@__converter_requires("tensorflow")
def convert_metric_value_to_str_if_tensorflow_tensor(x):
    import tensorflow as tf

    if isinstance(x, tf.Tensor):
        extracted_ndarray = x.numpy()
        return convert_metric_value_to_str_if_ndarray(extracted_ndarray)

    return x