# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



load("@rules_proto//proto:defs.bzl", "proto_library")
load("@com_github_grpc_grpc//bazel:grpc_build_system.bzl", "grpc_proto_library")
load("@com_github_grpc_grpc//bazel:python_rules.bzl", "py_proto_library", "py_grpc_library")

proto_library(
    name = "capability_proto",
    srcs = ["capability.proto"],
)

py_proto_library(
    name = "capability_py_pb2",
    deps = [ ":capability_proto" ],
    visibility = ["//visibility:public"],
)

proto_library(
    name = "device_proto",
    srcs = ["device.proto"],
    deps = [":capability_proto"],
)

py_proto_library(
    name = "device_py_pb2",
    deps = [ ":device_proto" ],
    visibility = ["//visibility:public"],
)

proto_library(
    name = "service_proto",
    srcs = ["service.proto"],
    deps = [
        ":device_proto",
        ":capability_proto",
        "@com_google_protobuf//:empty_proto",
    ],
)

py_proto_library(
    name = "service_py_pb2",
    deps = [":service_proto"],
    visibility = ["//visibility:public"],
)

py_grpc_library(
    name = "service_py_pb2_grpc",
    srcs = [":service_proto"],
    deps = [":service_py_pb2"],
    visibility = ["//visibility:public"],
)
