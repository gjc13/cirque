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



load("@rules_python//python:defs.bzl", "py_library")
load("@cirque_deps//:requirements.bzl", "requirement")
load("//utils/pystyletest:pystyletest.bzl", "py_style_test")

py_library(
    name="nodes",
    srcs = [
        "__init__.py",
        "dockernode.py",
        "processnode.py",
        "wifiapnode.py",
    ],
    deps = [
        "//cirque/common",
        requirement("docker"),
    ],
    visibility = ["//visibility:public"],
)

py_style_test(
    name="lint",
    srcs = [
        "__init__.py",
        "dockernode.py",
        "processnode.py",
        "wifiapnode.py",
    ],
    deps = [
        "//cirque/common",
        "//cirque/capabilities",
        requirement("docker"),
    ],
)
