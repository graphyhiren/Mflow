# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: databricks_managed_catalog_messages.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from .scalapb import scalapb_pb2 as scalapb_dot_scalapb__pb2
from . import databricks_pb2 as databricks__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n)databricks_managed_catalog_messages.proto\x12\x15mlflow.managedcatalog\x1a\x15scalapb/scalapb.proto\x1a\x10\x64\x61tabricks.proto\"0\n\tTableInfo\x12\x11\n\tfull_name\x18\x0f \x01(\t\x12\x10\n\x08table_id\x18\x16 \x01(\t\"\xc2\x01\n\x08GetTable\x12\x15\n\rfull_name_arg\x18\x01 \x01(\t\x12\x14\n\x0comit_columns\x18\x05 \x01(\x08\x12\x17\n\x0fomit_properties\x18\x06 \x01(\x08\x12\x18\n\x10omit_constraints\x18\x07 \x01(\x08\x12\x19\n\x11omit_dependencies\x18\x08 \x01(\x08\x12\x15\n\romit_username\x18\x0b \x01(\x08\x12$\n\x1comit_storage_credential_name\x18\x0c \x01(\x08\"7\n\x10GetTableResponse\x12\x11\n\tfull_name\x18\x0f \x01(\t\x12\x10\n\x08table_id\x18\x16 \x01(\tB1\n\'com.databricks.api.proto.managedcatalog\xa0\x01\x01\xe2?\x02\x10\x01')



_TABLEINFO = DESCRIPTOR.message_types_by_name['TableInfo']
_GETTABLE = DESCRIPTOR.message_types_by_name['GetTable']
_GETTABLERESPONSE = DESCRIPTOR.message_types_by_name['GetTableResponse']
TableInfo = _reflection.GeneratedProtocolMessageType('TableInfo', (_message.Message,), {
  'DESCRIPTOR' : _TABLEINFO,
  '__module__' : 'databricks_managed_catalog_messages_pb2'
  # @@protoc_insertion_point(class_scope:mlflow.managedcatalog.TableInfo)
  })
_sym_db.RegisterMessage(TableInfo)

GetTable = _reflection.GeneratedProtocolMessageType('GetTable', (_message.Message,), {
  'DESCRIPTOR' : _GETTABLE,
  '__module__' : 'databricks_managed_catalog_messages_pb2'
  # @@protoc_insertion_point(class_scope:mlflow.managedcatalog.GetTable)
  })
_sym_db.RegisterMessage(GetTable)

GetTableResponse = _reflection.GeneratedProtocolMessageType('GetTableResponse', (_message.Message,), {
  'DESCRIPTOR' : _GETTABLERESPONSE,
  '__module__' : 'databricks_managed_catalog_messages_pb2'
  # @@protoc_insertion_point(class_scope:mlflow.managedcatalog.GetTableResponse)
  })
_sym_db.RegisterMessage(GetTableResponse)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\'com.databricks.api.proto.managedcatalog\240\001\001\342?\002\020\001'
  _TABLEINFO._serialized_start=109
  _TABLEINFO._serialized_end=157
  _GETTABLE._serialized_start=160
  _GETTABLE._serialized_end=354
  _GETTABLERESPONSE._serialized_start=356
  _GETTABLERESPONSE._serialized_end=411
# @@protoc_insertion_point(module_scope)
