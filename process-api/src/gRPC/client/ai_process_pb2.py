# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ai_process.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import any_pb2 as google_dot_protobuf_dot_any__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='ai_process.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x10\x61i_process.proto\x1a\x19google/protobuf/any.proto\"2\n\x0eProcessRequest\x12\r\n\x05input\x18\x01 \x01(\t\x12\x11\n\tprocesses\x18\x02 \x03(\t\"P\n\x0cProcessReply\x12\x12\n\nstatusCode\x18\x01 \x01(\x05\x12\r\n\x05\x65rror\x18\x02 \x01(\x08\x12\x0c\n\x04\x64\x61ta\x18\x03 \x01(\t\x12\x0f\n\x07message\x18\x04 \x01(\t2l\n\tAIProcess\x12.\n\nPreProcess\x12\x0f.ProcessRequest\x1a\r.ProcessReply\"\x00\x12/\n\x0bPostProcess\x12\x0f.ProcessRequest\x1a\r.ProcessReply\"\x00\x62\x06proto3'
  ,
  dependencies=[google_dot_protobuf_dot_any__pb2.DESCRIPTOR,])




_PROCESSREQUEST = _descriptor.Descriptor(
  name='ProcessRequest',
  full_name='ProcessRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='input', full_name='ProcessRequest.input', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='processes', full_name='ProcessRequest.processes', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=47,
  serialized_end=97,
)


_PROCESSREPLY = _descriptor.Descriptor(
  name='ProcessReply',
  full_name='ProcessReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='statusCode', full_name='ProcessReply.statusCode', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='error', full_name='ProcessReply.error', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='data', full_name='ProcessReply.data', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='message', full_name='ProcessReply.message', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=99,
  serialized_end=179,
)

DESCRIPTOR.message_types_by_name['ProcessRequest'] = _PROCESSREQUEST
DESCRIPTOR.message_types_by_name['ProcessReply'] = _PROCESSREPLY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ProcessRequest = _reflection.GeneratedProtocolMessageType('ProcessRequest', (_message.Message,), {
  'DESCRIPTOR' : _PROCESSREQUEST,
  '__module__' : 'ai_process_pb2'
  # @@protoc_insertion_point(class_scope:ProcessRequest)
  })
_sym_db.RegisterMessage(ProcessRequest)

ProcessReply = _reflection.GeneratedProtocolMessageType('ProcessReply', (_message.Message,), {
  'DESCRIPTOR' : _PROCESSREPLY,
  '__module__' : 'ai_process_pb2'
  # @@protoc_insertion_point(class_scope:ProcessReply)
  })
_sym_db.RegisterMessage(ProcessReply)



_AIPROCESS = _descriptor.ServiceDescriptor(
  name='AIProcess',
  full_name='AIProcess',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=181,
  serialized_end=289,
  methods=[
  _descriptor.MethodDescriptor(
    name='PreProcess',
    full_name='AIProcess.PreProcess',
    index=0,
    containing_service=None,
    input_type=_PROCESSREQUEST,
    output_type=_PROCESSREPLY,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='PostProcess',
    full_name='AIProcess.PostProcess',
    index=1,
    containing_service=None,
    input_type=_PROCESSREQUEST,
    output_type=_PROCESSREPLY,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_AIPROCESS)

DESCRIPTOR.services_by_name['AIProcess'] = _AIPROCESS

# @@protoc_insertion_point(module_scope)
