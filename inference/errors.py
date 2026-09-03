class ModelRuntimeError(RuntimeError): pass
class ModelUnavailable(ModelRuntimeError): pass
class ModelContractError(ModelRuntimeError): pass
class ImageDecodeError(ModelRuntimeError): pass
