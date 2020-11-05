# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: databricks_model_artifacts.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import service as _service
from google.protobuf import service_reflection
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from .scalapb import scalapb_pb2 as scalapb_dot_scalapb__pb2
from . import databricks_pb2 as databricks__pb2
from . import service_pb2 as service__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='databricks_model_artifacts.proto',
  package='mlflow',
  syntax='proto2',
  serialized_options=_b('\n\037com.databricks.api.proto.mlflow\220\001\001\240\001\001\342?\002\020\001'),
  serialized_pb=_b('\n databricks_model_artifacts.proto\x12\x06mlflow\x1a\x15scalapb/scalapb.proto\x1a\x10\x64\x61tabricks.proto\x1a\rservice.proto\"\xae\x01\n GetModelVersionSignedDownloadUri\x12\x12\n\x04name\x18\x01 \x01(\tB\x04\xf8\x86\x19\x01\x12\x15\n\x07version\x18\x02 \x01(\tB\x04\xf8\x86\x19\x01\x12\x12\n\x04path\x18\x03 \x01(\tB\x04\xf8\x86\x19\x01\x1a\x1e\n\x08Response\x12\x12\n\nsigned_uri\x18\x01 \x01(\t:+\xe2?(\n&com.databricks.rpc.RPC[$this.Response]\"\xd4\x01\n\x12ListModelArtifacts\x12\x12\n\x04name\x18\x01 \x01(\tB\x04\xf8\x86\x19\x01\x12\x15\n\x07version\x18\x02 \x01(\tB\x04\xf8\x86\x19\x01\x12\x0c\n\x04path\x18\x03 \x01(\t\x12\x12\n\npage_token\x18\x04 \x01(\t\x1a\x44\n\x08Response\x12\x1f\n\x05\x66iles\x18\x01 \x03(\x0b\x32\x10.mlflow.FileInfo\x12\x17\n\x0fnext_page_token\x18\x02 \x01(\t:+\xe2?(\n&com.databricks.rpc.RPC[$this.Response]2\xfc\x02\n\x1f\x44\x61tabricksModelArtifactsService\x12\xc4\x01\n getModelVersionSignedDownloadUri\x12(.mlflow.GetModelVersionSignedDownloadUri\x1a\x31.mlflow.GetModelVersionSignedDownloadUri.Response\"C\xf2\x86\x19?\n;\n\x03GET\x12./mlflow/model-versions/get-signed-download-uri\x1a\x04\x08\x02\x10\x00\x10\x03\x12\x91\x01\n\x12listModelArtifacts\x12\x1a.mlflow.ListModelArtifacts\x1a#.mlflow.ListModelArtifacts.Response\":\xf2\x86\x19\x36\n2\n\x03GET\x12%/mlflow/model-versions/list-artifacts\x1a\x04\x08\x02\x10\x00\x10\x03\x42,\n\x1f\x63om.databricks.api.proto.mlflow\x90\x01\x01\xa0\x01\x01\xe2?\x02\x10\x01')
  ,
  dependencies=[scalapb_dot_scalapb__pb2.DESCRIPTOR,databricks__pb2.DESCRIPTOR,service__pb2.DESCRIPTOR,])




_GETMODELVERSIONSIGNEDDOWNLOADURI_RESPONSE = _descriptor.Descriptor(
  name='Response',
  full_name='mlflow.GetModelVersionSignedDownloadUri.Response',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='signed_uri', full_name='mlflow.GetModelVersionSignedDownloadUri.Response.signed_uri', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=200,
  serialized_end=230,
)

_GETMODELVERSIONSIGNEDDOWNLOADURI = _descriptor.Descriptor(
  name='GetModelVersionSignedDownloadUri',
  full_name='mlflow.GetModelVersionSignedDownloadUri',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='mlflow.GetModelVersionSignedDownloadUri.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('\370\206\031\001'), file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='version', full_name='mlflow.GetModelVersionSignedDownloadUri.version', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('\370\206\031\001'), file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='path', full_name='mlflow.GetModelVersionSignedDownloadUri.path', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('\370\206\031\001'), file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_GETMODELVERSIONSIGNEDDOWNLOADURI_RESPONSE, ],
  enum_types=[
  ],
  serialized_options=_b('\342?(\n&com.databricks.rpc.RPC[$this.Response]'),
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=101,
  serialized_end=275,
)


_LISTMODELARTIFACTS_RESPONSE = _descriptor.Descriptor(
  name='Response',
  full_name='mlflow.ListModelArtifacts.Response',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='files', full_name='mlflow.ListModelArtifacts.Response.files', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='next_page_token', full_name='mlflow.ListModelArtifacts.Response.next_page_token', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=377,
  serialized_end=445,
)

_LISTMODELARTIFACTS = _descriptor.Descriptor(
  name='ListModelArtifacts',
  full_name='mlflow.ListModelArtifacts',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='mlflow.ListModelArtifacts.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('\370\206\031\001'), file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='version', full_name='mlflow.ListModelArtifacts.version', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('\370\206\031\001'), file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='path', full_name='mlflow.ListModelArtifacts.path', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='page_token', full_name='mlflow.ListModelArtifacts.page_token', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_LISTMODELARTIFACTS_RESPONSE, ],
  enum_types=[
  ],
  serialized_options=_b('\342?(\n&com.databricks.rpc.RPC[$this.Response]'),
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=278,
  serialized_end=490,
)

_GETMODELVERSIONSIGNEDDOWNLOADURI_RESPONSE.containing_type = _GETMODELVERSIONSIGNEDDOWNLOADURI
_LISTMODELARTIFACTS_RESPONSE.fields_by_name['files'].message_type = service__pb2._FILEINFO
_LISTMODELARTIFACTS_RESPONSE.containing_type = _LISTMODELARTIFACTS
DESCRIPTOR.message_types_by_name['GetModelVersionSignedDownloadUri'] = _GETMODELVERSIONSIGNEDDOWNLOADURI
DESCRIPTOR.message_types_by_name['ListModelArtifacts'] = _LISTMODELARTIFACTS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

GetModelVersionSignedDownloadUri = _reflection.GeneratedProtocolMessageType('GetModelVersionSignedDownloadUri', (_message.Message,), dict(

  Response = _reflection.GeneratedProtocolMessageType('Response', (_message.Message,), dict(
    DESCRIPTOR = _GETMODELVERSIONSIGNEDDOWNLOADURI_RESPONSE,
    __module__ = 'databricks_model_artifacts_pb2'
    # @@protoc_insertion_point(class_scope:mlflow.GetModelVersionSignedDownloadUri.Response)
    ))
  ,
  DESCRIPTOR = _GETMODELVERSIONSIGNEDDOWNLOADURI,
  __module__ = 'databricks_model_artifacts_pb2'
  # @@protoc_insertion_point(class_scope:mlflow.GetModelVersionSignedDownloadUri)
  ))
_sym_db.RegisterMessage(GetModelVersionSignedDownloadUri)
_sym_db.RegisterMessage(GetModelVersionSignedDownloadUri.Response)

ListModelArtifacts = _reflection.GeneratedProtocolMessageType('ListModelArtifacts', (_message.Message,), dict(

  Response = _reflection.GeneratedProtocolMessageType('Response', (_message.Message,), dict(
    DESCRIPTOR = _LISTMODELARTIFACTS_RESPONSE,
    __module__ = 'databricks_model_artifacts_pb2'
    # @@protoc_insertion_point(class_scope:mlflow.ListModelArtifacts.Response)
    ))
  ,
  DESCRIPTOR = _LISTMODELARTIFACTS,
  __module__ = 'databricks_model_artifacts_pb2'
  # @@protoc_insertion_point(class_scope:mlflow.ListModelArtifacts)
  ))
_sym_db.RegisterMessage(ListModelArtifacts)
_sym_db.RegisterMessage(ListModelArtifacts.Response)


DESCRIPTOR._options = None
_GETMODELVERSIONSIGNEDDOWNLOADURI.fields_by_name['name']._options = None
_GETMODELVERSIONSIGNEDDOWNLOADURI.fields_by_name['version']._options = None
_GETMODELVERSIONSIGNEDDOWNLOADURI.fields_by_name['path']._options = None
_GETMODELVERSIONSIGNEDDOWNLOADURI._options = None
_LISTMODELARTIFACTS.fields_by_name['name']._options = None
_LISTMODELARTIFACTS.fields_by_name['version']._options = None
_LISTMODELARTIFACTS._options = None

_DATABRICKSMODELARTIFACTSSERVICE = _descriptor.ServiceDescriptor(
  name='DatabricksModelArtifactsService',
  full_name='mlflow.DatabricksModelArtifactsService',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=493,
  serialized_end=873,
  methods=[
  _descriptor.MethodDescriptor(
    name='getModelVersionSignedDownloadUri',
    full_name='mlflow.DatabricksModelArtifactsService.getModelVersionSignedDownloadUri',
    index=0,
    containing_service=None,
    input_type=_GETMODELVERSIONSIGNEDDOWNLOADURI,
    output_type=_GETMODELVERSIONSIGNEDDOWNLOADURI_RESPONSE,
    serialized_options=_b('\362\206\031?\n;\n\003GET\022./mlflow/model-versions/get-signed-download-uri\032\004\010\002\020\000\020\003'),
  ),
  _descriptor.MethodDescriptor(
    name='listModelArtifacts',
    full_name='mlflow.DatabricksModelArtifactsService.listModelArtifacts',
    index=1,
    containing_service=None,
    input_type=_LISTMODELARTIFACTS,
    output_type=_LISTMODELARTIFACTS_RESPONSE,
    serialized_options=_b('\362\206\0316\n2\n\003GET\022%/mlflow/model-versions/list-artifacts\032\004\010\002\020\000\020\003'),
  ),
])
_sym_db.RegisterServiceDescriptor(_DATABRICKSMODELARTIFACTSSERVICE)

DESCRIPTOR.services_by_name['DatabricksModelArtifactsService'] = _DATABRICKSMODELARTIFACTSSERVICE

DatabricksModelArtifactsService = service_reflection.GeneratedServiceType('DatabricksModelArtifactsService', (_service.Service,), dict(
  DESCRIPTOR = _DATABRICKSMODELARTIFACTSSERVICE,
  __module__ = 'databricks_model_artifacts_pb2'
  ))

DatabricksModelArtifactsService_Stub = service_reflection.GeneratedServiceStubType('DatabricksModelArtifactsService_Stub', (DatabricksModelArtifactsService,), dict(
  DESCRIPTOR = _DATABRICKSMODELARTIFACTSSERVICE,
  __module__ = 'databricks_model_artifacts_pb2'
  ))


# @@protoc_insertion_point(module_scope)
