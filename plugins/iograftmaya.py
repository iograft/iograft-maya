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

import maya.api.OpenMaya as OpenMaya

import iograft


def maya_useNewAPI():
    pass


iograftMayaVersion = "0.9"


# Keep track of the iograft state and preserve this across scenes. Only
# a single iograft core should be running within Maya at one time.
class _iograftState(object):
    _instance = None

    def __init__(self):
        self._initialized = False
        self._core = None


def _getState():
    if not _iograftState._instance:
        _iograftState._instance = _iograftState()
    return _iograftState._instance


class StartIograftCommand(OpenMaya.MPxCommand):
    kPluginCmdName = "startiograft"

    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)

    @staticmethod
    def cmdCreator():
        return StartIograftCommand()

    def _configure(self):
        """
        Run some configuration steps to ensure iograft can execute nodes
        within Maya.
        """
        # Initialize the iograft system.
        iograft.Initialize()

    def doIt(self, args):
        state = _getState()

        # Check if iograft is already running.
        if state._core is not None:
            iograft_address = state._core.GetClientAddress()
            OpenMaya.MGlobal.displayWarning(
                            "iograft already running at: " + iograft_address)
            return

        # Ensure that iograft has been configure to run in Maya.
        if not state._initialized:
            self._configure()
            state._initialized = True

        # Launch iograft.
        state._core = iograft.Core()
        state._core.StartRequestHandler()
        iograft_address = state._core.GetClientAddress()
        OpenMaya.MGlobal.displayInfo("iograft started at: " + iograft_address)


class StopIograftCommand(OpenMaya.MPxCommand):
    kPluginCmdName = "stopiograft"

    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)

    @staticmethod
    def cmdCreator():
        return StopIograftCommand()

    def doIt(self, args):
        state = _getState()
        if state._core is None:
            OpenMaya.MGlobal.displayWarning(
                                "No iograft instance currently running.")
            return

        # Clear the iograft core.
        state._core = None

        # Uninitialize iograft.
        iograft.Uninitialize()
        state._initialized = False
        OpenMaya.MGlobal.displayInfo("iograft stopped.")


class LaunchIograftUI(OpenMaya.MPxCommand):
    kPluginCmdName = "iograft_ui"

    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)

    @staticmethod
    def cmdCreator():
        return LaunchIograftUI()

    def doIt(self, args):
        import subprocess

        state = _getState()
        if state._core is None:
            OpenMaya.MGlobal.displayWarning(
                                "No iograft instance currently running.")
            return

        subprocess.Popen(["iograft_ui", "-c", state._core.GetClientAddress()])
        OpenMaya.MGlobal.displayInfo("iograft_ui launched.")


# This command allows for the execution of an iograft graph directly
# in Maya; it is "blocking" and does not allow for editing the graph
class ExecuteGraphCommand(OpenMaya.MPxCommand):
    pass


def initializePlugin(plugin):
    pluginFn = OpenMaya.MFnPlugin(plugin,
                                  "Fabrica Software, LLC",
                                  iograftMayaVersion,
                                  "Any")

    # Load the commands to start and stop the iograft core.
    try:
        pluginFn.registerCommand(StartIograftCommand.kPluginCmdName,
                                 StartIograftCommand.cmdCreator)
        pluginFn.registerCommand(StopIograftCommand.kPluginCmdName,
                                 StopIograftCommand.cmdCreator)
        pluginFn.registerCommand(LaunchIograftUI.kPluginCmdName,
                                 LaunchIograftUI.cmdCreator)
    except:
        sys.stderr.write("Failed to register iograft commands.\n")
        raise


def uninitializePlugin(plugin):
    pluginFn = OpenMaya.MFnPlugin(plugin,
                                  "Fabrica Software, LLC",
                                  iograftMayaVersion,
                                  "Any")
    try:
        pluginFn.deregisterCommand(StartIograftCommand.kPluginCmdName)
        pluginFn.deregisterCommand(StopIograftCommand.kPluginCmdName)
        pluginFn.deregisterCommand(LaunchIograftUI.kPluginCmdName)
    except:
        sys.stderr.write("Failed to unregister iograft commands.\n")
        raise
