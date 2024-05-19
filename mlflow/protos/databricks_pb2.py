# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: databricks.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import descriptor_pb2 as google_dot_protobuf_dot_descriptor__pb2
from .scalapb import scalapb_pb2 as scalapb_dot_scalapb__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10\x64\x61tabricks.proto\x12\x06mlflow\x1a google/protobuf/descriptor.proto\x1a\x15scalapb/scalapb.proto\"\xcd\x01\n\x14\x44\x61tabricksRpcOptions\x12\'\n\tendpoints\x18\x01 \x03(\x0b\x32\x14.mlflow.HttpEndpoint\x12&\n\nvisibility\x18\x02 \x01(\x0e\x32\x12.mlflow.Visibility\x12&\n\x0b\x65rror_codes\x18\x03 \x03(\x0e\x32\x11.mlflow.ErrorCode\x12%\n\nrate_limit\x18\x04 \x01(\x0b\x32\x11.mlflow.RateLimit\x12\x15\n\rrpc_doc_title\x18\x05 \x01(\t\"\x1a\n\x18\x44\x61tabricksGraphqlOptions\"U\n\x0cHttpEndpoint\x12\x14\n\x06method\x18\x01 \x01(\t:\x04POST\x12\x0c\n\x04path\x18\x02 \x01(\t\x12!\n\x05since\x18\x03 \x01(\x0b\x32\x12.mlflow.ApiVersion\"*\n\nApiVersion\x12\r\n\x05major\x18\x01 \x01(\x05\x12\r\n\x05minor\x18\x02 \x01(\x05\"@\n\tRateLimit\x12\x11\n\tmax_burst\x18\x01 \x01(\x03\x12 \n\x18max_sustained_per_second\x18\x02 \x01(\x03\"\x93\x01\n\x15\x44ocumentationMetadata\x12\x11\n\tdocstring\x18\x01 \x01(\t\x12\x10\n\x08lead_doc\x18\x02 \x01(\t\x12&\n\nvisibility\x18\x03 \x01(\x0e\x32\x12.mlflow.Visibility\x12\x1b\n\x13original_proto_path\x18\x04 \x03(\t\x12\x10\n\x08position\x18\x05 \x01(\x05*?\n\nVisibility\x12\n\n\x06PUBLIC\x10\x01\x12\x0c\n\x08INTERNAL\x10\x02\x12\x17\n\x13PUBLIC_UNDOCUMENTED\x10\x03*\xfd\x10\n\tErrorCode\x12\x12\n\x0eINTERNAL_ERROR\x10\x01\x12\x1b\n\x17TEMPORARILY_UNAVAILABLE\x10\x02\x12\x0c\n\x08IO_ERROR\x10\x03\x12\x0f\n\x0b\x42\x41\x44_REQUEST\x10\x04\x12\x1d\n\x19SERVICE_UNDER_MAINTENANCE\x10\x05\x12%\n!WORKSPACE_TEMPORARILY_UNAVAILABLE\x10\x06\x12\x15\n\x11\x44\x45\x41\x44LINE_EXCEEDED\x10\x07\x12\r\n\tCANCELLED\x10\x08\x12\x16\n\x12RESOURCE_EXHAUSTED\x10\t\x12\x0b\n\x07\x41\x42ORTED\x10\n\x12\r\n\tNOT_FOUND\x10\x0b\x12\x12\n\x0e\x41LREADY_EXISTS\x10\x0c\x12\x13\n\x0fUNAUTHENTICATED\x10\r\x12\x1c\n\x17INVALID_PARAMETER_VALUE\x10\xe8\x07\x12\x17\n\x12\x45NDPOINT_NOT_FOUND\x10\xe9\x07\x12\x16\n\x11MALFORMED_REQUEST\x10\xea\x07\x12\x12\n\rINVALID_STATE\x10\xeb\x07\x12\x16\n\x11PERMISSION_DENIED\x10\xec\x07\x12\x15\n\x10\x46\x45\x41TURE_DISABLED\x10\xed\x07\x12\x1a\n\x15\x43USTOMER_UNAUTHORIZED\x10\xee\x07\x12\x1b\n\x16REQUEST_LIMIT_EXCEEDED\x10\xef\x07\x12\x16\n\x11RESOURCE_CONFLICT\x10\xf0\x07\x12\x1b\n\x16UNPARSEABLE_HTTP_ERROR\x10\xf1\x07\x12\x14\n\x0fNOT_IMPLEMENTED\x10\xf2\x07\x12\x0e\n\tDATA_LOSS\x10\xf3\x07\x12\x1d\n\x18INVALID_STATE_TRANSITION\x10\xd1\x0f\x12\x1b\n\x16\x43OULD_NOT_ACQUIRE_LOCK\x10\xd2\x0f\x12\x1c\n\x17RESOURCE_ALREADY_EXISTS\x10\xb9\x17\x12\x1c\n\x17RESOURCE_DOES_NOT_EXIST\x10\xba\x17\x12\x13\n\x0eQUOTA_EXCEEDED\x10\xa1\x1f\x12\x1c\n\x17MAX_BLOCK_SIZE_EXCEEDED\x10\xa2\x1f\x12\x1b\n\x16MAX_READ_SIZE_EXCEEDED\x10\xa3\x1f\x12\x13\n\x0ePARTIAL_DELETE\x10\xa4\x1f\x12\x1b\n\x16MAX_LIST_SIZE_EXCEEDED\x10\xa5\x1f\x12\x13\n\x0e\x44RY_RUN_FAILED\x10\x89\'\x12\x1c\n\x17RESOURCE_LIMIT_EXCEEDED\x10\x8a\'\x12\x18\n\x13\x44IRECTORY_NOT_EMPTY\x10\xf1.\x12\x18\n\x13\x44IRECTORY_PROTECTED\x10\xf2.\x12\x1f\n\x1aMAX_NOTEBOOK_SIZE_EXCEEDED\x10\xf3.\x12!\n\x1cMAX_CHILD_NODE_SIZE_EXCEEDED\x10\xf4.\x12\x1a\n\x15SEARCH_QUERY_TOO_LONG\x10\xd4/\x12\x1b\n\x16SEARCH_QUERY_TOO_SHORT\x10\xd5/\x12*\n%MANAGED_RESOURCE_GROUP_DOES_NOT_EXIST\x10\xd9\x36\x12\x1e\n\x19PERMISSION_NOT_PROPAGATED\x10\xda\x36\x12\x17\n\x12\x44\x45PLOYMENT_TIMEOUT\x10\xdb\x36\x12\x11\n\x0cGIT_CONFLICT\x10\xc1>\x12\x14\n\x0fGIT_UNKNOWN_REF\x10\xc2>\x12!\n\x1cGIT_SENSITIVE_TOKEN_DETECTED\x10\xc3>\x12\x1e\n\x19GIT_URL_NOT_ON_ALLOW_LIST\x10\xc4>\x12\x15\n\x10GIT_REMOTE_ERROR\x10\xc5>\x12\x1f\n\x1aPROJECTS_OPERATION_TIMEOUT\x10\xc6>\x12\x17\n\x12IPYNB_FILE_IN_REPO\x10\xc7>\x12\x1e\n\x19INSECURE_PARTNER_RESPONSE\x10\xa4?\x12\x1f\n\x1aMALFORMED_PARTNER_RESPONSE\x10\xa5?\x12\x1d\n\x18METASTORE_DOES_NOT_EXIST\x10\xa8\x46\x12\x17\n\x12\x44\x41\x43_DOES_NOT_EXIST\x10\xa9\x46\x12\x1b\n\x16\x43\x41TALOG_DOES_NOT_EXIST\x10\xaa\x46\x12\x1a\n\x15SCHEMA_DOES_NOT_EXIST\x10\xab\x46\x12\x19\n\x14TABLE_DOES_NOT_EXIST\x10\xac\x46\x12\x19\n\x14SHARE_DOES_NOT_EXIST\x10\xad\x46\x12\x1d\n\x18RECIPIENT_DOES_NOT_EXIST\x10\xae\x46\x12&\n!STORAGE_CREDENTIAL_DOES_NOT_EXIST\x10\xaf\x46\x12%\n EXTERNAL_LOCATION_DOES_NOT_EXIST\x10\xb0\x46\x12\x1d\n\x18PRINCIPAL_DOES_NOT_EXIST\x10\xb1\x46\x12\x1c\n\x17PROVIDER_DOES_NOT_EXIST\x10\xb2\x46\x12\x1d\n\x18METASTORE_ALREADY_EXISTS\x10\xbc\x46\x12\x17\n\x12\x44\x41\x43_ALREADY_EXISTS\x10\xbd\x46\x12\x1b\n\x16\x43\x41TALOG_ALREADY_EXISTS\x10\xbe\x46\x12\x1a\n\x15SCHEMA_ALREADY_EXISTS\x10\xbf\x46\x12\x19\n\x14TABLE_ALREADY_EXISTS\x10\xc0\x46\x12\x19\n\x14SHARE_ALREADY_EXISTS\x10\xc1\x46\x12\x1d\n\x18RECIPIENT_ALREADY_EXISTS\x10\xc2\x46\x12&\n!STORAGE_CREDENTIAL_ALREADY_EXISTS\x10\xc3\x46\x12%\n EXTERNAL_LOCATION_ALREADY_EXISTS\x10\xc4\x46\x12\x1c\n\x17PROVIDER_ALREADY_EXISTS\x10\xc5\x46\x12\x16\n\x11\x43\x41TALOG_NOT_EMPTY\x10\xd0\x46\x12\x15\n\x10SCHEMA_NOT_EMPTY\x10\xd1\x46\x12\x18\n\x13METASTORE_NOT_EMPTY\x10\xd2\x46\x12\"\n\x1dPROVIDER_SHARE_NOT_ACCESSIBLE\x10\xe4\x46:G\n\nvisibility\x12\x1d.google.protobuf.FieldOptions\x18\xee\x90\x03 \x01(\x0e\x32\x12.mlflow.Visibility::\n\x11validate_required\x12\x1d.google.protobuf.FieldOptions\x18\xef\x90\x03 \x01(\x08:4\n\x0bjson_inline\x12\x1d.google.protobuf.FieldOptions\x18\xf0\x90\x03 \x01(\x08:1\n\x08json_map\x12\x1d.google.protobuf.FieldOptions\x18\xf1\x90\x03 \x01(\x08:Q\n\tfield_doc\x12\x1d.google.protobuf.FieldOptions\x18\xf2\x90\x03 \x03(\x0b\x32\x1d.mlflow.DocumentationMetadata:K\n\x03rpc\x12\x1e.google.protobuf.MethodOptions\x18\xee\x90\x03 \x01(\x0b\x32\x1c.mlflow.DatabricksRpcOptions:S\n\nmethod_doc\x12\x1e.google.protobuf.MethodOptions\x18\xf2\x90\x03 \x03(\x0b\x32\x1d.mlflow.DocumentationMetadata:S\n\x07graphql\x12\x1e.google.protobuf.MethodOptions\x18\xc7\x91\x03 \x01(\x0b\x32 .mlflow.DatabricksGraphqlOptions:U\n\x0bmessage_doc\x12\x1f.google.protobuf.MessageOptions\x18\xf2\x90\x03 \x03(\x0b\x32\x1d.mlflow.DocumentationMetadata:U\n\x0bservice_doc\x12\x1f.google.protobuf.ServiceOptions\x18\xf2\x90\x03 \x03(\x0b\x32\x1d.mlflow.DocumentationMetadata:O\n\x08\x65num_doc\x12\x1c.google.protobuf.EnumOptions\x18\xf2\x90\x03 \x03(\x0b\x32\x1d.mlflow.DocumentationMetadata:V\n\x15\x65num_value_visibility\x12!.google.protobuf.EnumValueOptions\x18\xee\x90\x03 \x01(\x0e\x32\x12.mlflow.Visibility:Z\n\x0e\x65num_value_doc\x12!.google.protobuf.EnumValueOptions\x18\xf2\x90\x03 \x03(\x0b\x32\x1d.mlflow.DocumentationMetadataB*\n#com.databricks.api.proto.databricks\xe2?\x02\x10\x01')

_VISIBILITY = DESCRIPTOR.enum_types_by_name['Visibility']
Visibility = enum_type_wrapper.EnumTypeWrapper(_VISIBILITY)
_ERRORCODE = DESCRIPTOR.enum_types_by_name['ErrorCode']
ErrorCode = enum_type_wrapper.EnumTypeWrapper(_ERRORCODE)
PUBLIC = 1
INTERNAL = 2
PUBLIC_UNDOCUMENTED = 3
INTERNAL_ERROR = 1
TEMPORARILY_UNAVAILABLE = 2
IO_ERROR = 3
BAD_REQUEST = 4
SERVICE_UNDER_MAINTENANCE = 5
WORKSPACE_TEMPORARILY_UNAVAILABLE = 6
DEADLINE_EXCEEDED = 7
CANCELLED = 8
RESOURCE_EXHAUSTED = 9
ABORTED = 10
NOT_FOUND = 11
ALREADY_EXISTS = 12
UNAUTHENTICATED = 13
INVALID_PARAMETER_VALUE = 1000
ENDPOINT_NOT_FOUND = 1001
MALFORMED_REQUEST = 1002
INVALID_STATE = 1003
PERMISSION_DENIED = 1004
FEATURE_DISABLED = 1005
CUSTOMER_UNAUTHORIZED = 1006
REQUEST_LIMIT_EXCEEDED = 1007
RESOURCE_CONFLICT = 1008
UNPARSEABLE_HTTP_ERROR = 1009
NOT_IMPLEMENTED = 1010
DATA_LOSS = 1011
INVALID_STATE_TRANSITION = 2001
COULD_NOT_ACQUIRE_LOCK = 2002
RESOURCE_ALREADY_EXISTS = 3001
RESOURCE_DOES_NOT_EXIST = 3002
QUOTA_EXCEEDED = 4001
MAX_BLOCK_SIZE_EXCEEDED = 4002
MAX_READ_SIZE_EXCEEDED = 4003
PARTIAL_DELETE = 4004
MAX_LIST_SIZE_EXCEEDED = 4005
DRY_RUN_FAILED = 5001
RESOURCE_LIMIT_EXCEEDED = 5002
DIRECTORY_NOT_EMPTY = 6001
DIRECTORY_PROTECTED = 6002
MAX_NOTEBOOK_SIZE_EXCEEDED = 6003
MAX_CHILD_NODE_SIZE_EXCEEDED = 6004
SEARCH_QUERY_TOO_LONG = 6100
SEARCH_QUERY_TOO_SHORT = 6101
MANAGED_RESOURCE_GROUP_DOES_NOT_EXIST = 7001
PERMISSION_NOT_PROPAGATED = 7002
DEPLOYMENT_TIMEOUT = 7003
GIT_CONFLICT = 8001
GIT_UNKNOWN_REF = 8002
GIT_SENSITIVE_TOKEN_DETECTED = 8003
GIT_URL_NOT_ON_ALLOW_LIST = 8004
GIT_REMOTE_ERROR = 8005
PROJECTS_OPERATION_TIMEOUT = 8006
IPYNB_FILE_IN_REPO = 8007
INSECURE_PARTNER_RESPONSE = 8100
MALFORMED_PARTNER_RESPONSE = 8101
METASTORE_DOES_NOT_EXIST = 9000
DAC_DOES_NOT_EXIST = 9001
CATALOG_DOES_NOT_EXIST = 9002
SCHEMA_DOES_NOT_EXIST = 9003
TABLE_DOES_NOT_EXIST = 9004
SHARE_DOES_NOT_EXIST = 9005
RECIPIENT_DOES_NOT_EXIST = 9006
STORAGE_CREDENTIAL_DOES_NOT_EXIST = 9007
EXTERNAL_LOCATION_DOES_NOT_EXIST = 9008
PRINCIPAL_DOES_NOT_EXIST = 9009
PROVIDER_DOES_NOT_EXIST = 9010
METASTORE_ALREADY_EXISTS = 9020
DAC_ALREADY_EXISTS = 9021
CATALOG_ALREADY_EXISTS = 9022
SCHEMA_ALREADY_EXISTS = 9023
TABLE_ALREADY_EXISTS = 9024
SHARE_ALREADY_EXISTS = 9025
RECIPIENT_ALREADY_EXISTS = 9026
STORAGE_CREDENTIAL_ALREADY_EXISTS = 9027
EXTERNAL_LOCATION_ALREADY_EXISTS = 9028
PROVIDER_ALREADY_EXISTS = 9029
CATALOG_NOT_EMPTY = 9040
SCHEMA_NOT_EMPTY = 9041
METASTORE_NOT_EMPTY = 9042
PROVIDER_SHARE_NOT_ACCESSIBLE = 9060

VISIBILITY_FIELD_NUMBER = 51310
visibility = DESCRIPTOR.extensions_by_name['visibility']
VALIDATE_REQUIRED_FIELD_NUMBER = 51311
validate_required = DESCRIPTOR.extensions_by_name['validate_required']
JSON_INLINE_FIELD_NUMBER = 51312
json_inline = DESCRIPTOR.extensions_by_name['json_inline']
JSON_MAP_FIELD_NUMBER = 51313
json_map = DESCRIPTOR.extensions_by_name['json_map']
FIELD_DOC_FIELD_NUMBER = 51314
field_doc = DESCRIPTOR.extensions_by_name['field_doc']
RPC_FIELD_NUMBER = 51310
rpc = DESCRIPTOR.extensions_by_name['rpc']
METHOD_DOC_FIELD_NUMBER = 51314
method_doc = DESCRIPTOR.extensions_by_name['method_doc']
GRAPHQL_FIELD_NUMBER = 51399
graphql = DESCRIPTOR.extensions_by_name['graphql']
MESSAGE_DOC_FIELD_NUMBER = 51314
message_doc = DESCRIPTOR.extensions_by_name['message_doc']
SERVICE_DOC_FIELD_NUMBER = 51314
service_doc = DESCRIPTOR.extensions_by_name['service_doc']
ENUM_DOC_FIELD_NUMBER = 51314
enum_doc = DESCRIPTOR.extensions_by_name['enum_doc']
ENUM_VALUE_VISIBILITY_FIELD_NUMBER = 51310
enum_value_visibility = DESCRIPTOR.extensions_by_name['enum_value_visibility']
ENUM_VALUE_DOC_FIELD_NUMBER = 51314
enum_value_doc = DESCRIPTOR.extensions_by_name['enum_value_doc']

_DATABRICKSRPCOPTIONS = DESCRIPTOR.message_types_by_name['DatabricksRpcOptions']
_DATABRICKSGRAPHQLOPTIONS = DESCRIPTOR.message_types_by_name['DatabricksGraphqlOptions']
_HTTPENDPOINT = DESCRIPTOR.message_types_by_name['HttpEndpoint']
_APIVERSION = DESCRIPTOR.message_types_by_name['ApiVersion']
_RATELIMIT = DESCRIPTOR.message_types_by_name['RateLimit']
_DOCUMENTATIONMETADATA = DESCRIPTOR.message_types_by_name['DocumentationMetadata']
DatabricksRpcOptions = _reflection.GeneratedProtocolMessageType('DatabricksRpcOptions', (_message.Message,), {
  'DESCRIPTOR' : _DATABRICKSRPCOPTIONS,
  '__module__' : 'databricks_pb2'
  # @@protoc_insertion_point(class_scope:mlflow.DatabricksRpcOptions)
  })
_sym_db.RegisterMessage(DatabricksRpcOptions)

DatabricksGraphqlOptions = _reflection.GeneratedProtocolMessageType('DatabricksGraphqlOptions', (_message.Message,), {
  'DESCRIPTOR' : _DATABRICKSGRAPHQLOPTIONS,
  '__module__' : 'databricks_pb2'
  # @@protoc_insertion_point(class_scope:mlflow.DatabricksGraphqlOptions)
  })
_sym_db.RegisterMessage(DatabricksGraphqlOptions)

HttpEndpoint = _reflection.GeneratedProtocolMessageType('HttpEndpoint', (_message.Message,), {
  'DESCRIPTOR' : _HTTPENDPOINT,
  '__module__' : 'databricks_pb2'
  # @@protoc_insertion_point(class_scope:mlflow.HttpEndpoint)
  })
_sym_db.RegisterMessage(HttpEndpoint)

ApiVersion = _reflection.GeneratedProtocolMessageType('ApiVersion', (_message.Message,), {
  'DESCRIPTOR' : _APIVERSION,
  '__module__' : 'databricks_pb2'
  # @@protoc_insertion_point(class_scope:mlflow.ApiVersion)
  })
_sym_db.RegisterMessage(ApiVersion)

RateLimit = _reflection.GeneratedProtocolMessageType('RateLimit', (_message.Message,), {
  'DESCRIPTOR' : _RATELIMIT,
  '__module__' : 'databricks_pb2'
  # @@protoc_insertion_point(class_scope:mlflow.RateLimit)
  })
_sym_db.RegisterMessage(RateLimit)

DocumentationMetadata = _reflection.GeneratedProtocolMessageType('DocumentationMetadata', (_message.Message,), {
  'DESCRIPTOR' : _DOCUMENTATIONMETADATA,
  '__module__' : 'databricks_pb2'
  # @@protoc_insertion_point(class_scope:mlflow.DocumentationMetadata)
  })
_sym_db.RegisterMessage(DocumentationMetadata)

if _descriptor._USE_C_DESCRIPTORS == False:
  # `RegisterExtension` was removed in v26: https://github.com/protocolbuffers/protobuf/pull/15270
  # The following code is a workaround for this breaking change.
  import google.protobuf.__version__ as protobuf_version
  if int(protobuf_version.split(".", 1)[0]) >= 5:
    google_dot_protobuf_dot_descriptor__pb2.FieldOptions.RegisterExtension(visibility)
    google_dot_protobuf_dot_descriptor__pb2.FieldOptions.RegisterExtension(validate_required)
    google_dot_protobuf_dot_descriptor__pb2.FieldOptions.RegisterExtension(json_inline)
    google_dot_protobuf_dot_descriptor__pb2.FieldOptions.RegisterExtension(json_map)
    google_dot_protobuf_dot_descriptor__pb2.FieldOptions.RegisterExtension(field_doc)
    google_dot_protobuf_dot_descriptor__pb2.MethodOptions.RegisterExtension(rpc)
    google_dot_protobuf_dot_descriptor__pb2.MethodOptions.RegisterExtension(method_doc)
    google_dot_protobuf_dot_descriptor__pb2.MethodOptions.RegisterExtension(graphql)
    google_dot_protobuf_dot_descriptor__pb2.MessageOptions.RegisterExtension(message_doc)
    google_dot_protobuf_dot_descriptor__pb2.ServiceOptions.RegisterExtension(service_doc)
    google_dot_protobuf_dot_descriptor__pb2.EnumOptions.RegisterExtension(enum_doc)
    google_dot_protobuf_dot_descriptor__pb2.EnumValueOptions.RegisterExtension(enum_value_visibility)
    google_dot_protobuf_dot_descriptor__pb2.EnumValueOptions.RegisterExtension(enum_value_doc)

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n#com.databricks.api.proto.databricks\342?\002\020\001'
  _VISIBILITY._serialized_start=668
  _VISIBILITY._serialized_end=731
  _ERRORCODE._serialized_start=734
  _ERRORCODE._serialized_end=2907
  _DATABRICKSRPCOPTIONS._serialized_start=86
  _DATABRICKSRPCOPTIONS._serialized_end=291
  _DATABRICKSGRAPHQLOPTIONS._serialized_start=293
  _DATABRICKSGRAPHQLOPTIONS._serialized_end=319
  _HTTPENDPOINT._serialized_start=321
  _HTTPENDPOINT._serialized_end=406
  _APIVERSION._serialized_start=408
  _APIVERSION._serialized_end=450
  _RATELIMIT._serialized_start=452
  _RATELIMIT._serialized_end=516
  _DOCUMENTATIONMETADATA._serialized_start=519
  _DOCUMENTATIONMETADATA._serialized_end=666
# @@protoc_insertion_point(module_scope)
