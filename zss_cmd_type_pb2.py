# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: zss_cmd_type.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12zss_cmd_type.proto\x12\x07ZSS.New\"\'\n\x04Pose\x12\t\n\x01x\x18\x01 \x01(\x02\x12\t\n\x01y\x18\x02 \x01(\x02\x12\t\n\x01w\x18\x03 \x01(\x02\"(\n\x05Twist\x12\t\n\x01x\x18\x01 \x01(\x02\x12\t\n\x01y\x18\x02 \x01(\x02\x12\t\n\x01w\x18\x03 \x01(\x02\"$\n\x04Odom\x12\x1c\n\x05poses\x18\x01 \x03(\x0b\x32\r.ZSS.New.Pose\"J\n\x08\x43mdWheel\x12\x0e\n\x06wheel1\x18\x01 \x01(\x02\x12\x0e\n\x06wheel2\x18\x02 \x01(\x02\x12\x0e\n\x06wheel3\x18\x03 \x01(\x02\x12\x0e\n\x06wheel4\x18\x04 \x01(\x02\"h\n\x06\x43mdVel\x12\x12\n\nvelocity_x\x18\x01 \x01(\x02\x12\x12\n\nvelocity_y\x18\x02 \x01(\x02\x12\x0f\n\x07use_imu\x18\x03 \x01(\x08\x12\x12\n\nvelocity_r\x18\x04 \x01(\x02\x12\x11\n\timu_theta\x18\x05 \x01(\x02\"o\n\rCmdPoseConfig\x12\x0e\n\x06max_vx\x18\x01 \x01(\x02\x12\x0e\n\x06max_vy\x18\x02 \x01(\x02\x12\x0e\n\x06max_vw\x18\x03 \x01(\x02\x12\x0e\n\x06max_ax\x18\x04 \x01(\x02\x12\x0e\n\x06max_ay\x18\x05 \x01(\x02\x12\x0e\n\x06max_aw\x18\x06 \x01(\x02\"\xdd\x01\n\x07\x43mdPose\x12\x1c\n\x05start\x18\x01 \x01(\x0b\x32\r.ZSS.New.Pose\x12\x1f\n\x07start_v\x18\x02 \x01(\x0b\x32\x0e.ZSS.New.Twist\x12\x1d\n\x06target\x18\x03 \x01(\x0b\x32\r.ZSS.New.Pose\x12 \n\x08target_v\x18\x04 \x01(\x0b\x32\x0e.ZSS.New.Twist\x12\x16\n\x0erotation_sense\x18\x05 \x01(\x05\x12\x12\n\nuse_config\x18\x06 \x01(\x08\x12&\n\x06\x63onfig\x18\x07 \x01(\x0b\x32\x16.ZSS.New.CmdPoseConfig\"\x86\x01\n\x08\x43mdChase\x12\x1c\n\x05start\x18\x01 \x01(\x0b\x32\r.ZSS.New.Pose\x12\x1f\n\x07start_v\x18\x02 \x01(\x0b\x32\x0e.ZSS.New.Twist\x12\x1b\n\x04\x62\x61ll\x18\x03 \x01(\x0b\x32\r.ZSS.New.Pose\x12\x1e\n\x06\x62\x61ll_v\x18\x04 \x01(\x0b\x32\x0e.ZSS.New.Twistb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'zss_cmd_type_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _globals['_POSE']._serialized_start=31
  _globals['_POSE']._serialized_end=70
  _globals['_TWIST']._serialized_start=72
  _globals['_TWIST']._serialized_end=112
  _globals['_ODOM']._serialized_start=114
  _globals['_ODOM']._serialized_end=150
  _globals['_CMDWHEEL']._serialized_start=152
  _globals['_CMDWHEEL']._serialized_end=226
  _globals['_CMDVEL']._serialized_start=228
  _globals['_CMDVEL']._serialized_end=332
  _globals['_CMDPOSECONFIG']._serialized_start=334
  _globals['_CMDPOSECONFIG']._serialized_end=445
  _globals['_CMDPOSE']._serialized_start=448
  _globals['_CMDPOSE']._serialized_end=669
  _globals['_CMDCHASE']._serialized_start=672
  _globals['_CMDCHASE']._serialized_end=806
# @@protoc_insertion_point(module_scope)
