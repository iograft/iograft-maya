# Copyright 2021 Fabrica Software, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import functools

import maya.cmds
import maya.utils

import iograft


def maya_main_thread(func):
    """
    Decorator to execute a node in the Maya main thread. All Maya nodes that
    require functions that must run in the main thread should apply this
    decorator to their Process() function:
        @maya_main_thread
        def Process(self, data):
            ...
    """
    def catchNodeException(func, *args):
        try:
            func(*args)
            return None
        except Exception:
            return sys.exc_info()

    @functools.wraps(func)
    def launch_in_main_thread(*args):
        if (maya.cmds.about(batch=True)):
            # If we are executing in batch, there is no access to Maya's
            # executeInMainThreadWithResult function.
            func(*args)
        else:
            result = maya.utils.executeInMainThreadWithResult(
                            functools.partial(catchNodeException, func), *args)
            if result:
                import traceback
                tb = traceback.format_exception(*result)
                raise iograft.NodeProcessException("".join(tb))

    return launch_in_main_thread
