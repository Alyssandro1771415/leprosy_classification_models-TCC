import tensorflow as tf
print("GPUs detectadas:", tf.config.list_physical_devices('GPU'))
print("Versão CUDA:", tf.sysconfig.get_build_info()["cuda_version"])
