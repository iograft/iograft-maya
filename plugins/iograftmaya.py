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
class LoadGraphCommand(OpenMaya.MPxCommand):
    kPluginCmdName = "iograft_load"

    kGraphFileFlag = "-f"
    kGraphFileLongFlag = "-file"

    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)

    @staticmethod
    def cmdCreator():
        return LoadGraphCommand()

    @classmethod
    def syntaxCreator(cls):
        syntax = OpenMaya.MSyntax()
        syntax.addFlag(cls.kGraphFileFlag,
                       cls.kGraphFileLongFlag,
                       OpenMaya.MSyntax.kString)
        return syntax

    def doIt(self, args):
        argData = OpenMaya.MArgDatabase(self.syntax(), args)

        state = _getState()
        if state._core is None:
            OpenMaya.MGlobal.displayWarning(
                                "No iograft instance currently running.")
            return

        # Load the requested graph.
        if not argData.isFlagSet(self.kGraphFileFlag):
            OpenMaya.MGlobal.displayWarning("The graph file arg is required.")
            return
        graph_file = argData.flagArgumentString(self.kGraphFileFlag, 0)
        OpenMaya.MGlobal.displayInfo(
                            "Loading iograft graph: {}".format(graph_file))
        state._core.LoadGraph(graph_file)


class ExecuteGraphCommand(OpenMaya.MPxCommand):
    kPluginCmdName = "iograft_execute"

    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)

    @staticmethod
    def cmdCreator():
        return ExecuteGraphCommand()

    def doIt(self, args):
        state = _getState()
        if state._core is None:
            OpenMaya.MGlobal.displayWarning(
                                "No iograft instance currently running.")
            return

        # Start the graph processing.
        state._core.StartGraphProcessing()


# This command allows for the execution of an iograft graph directly
# in Maya; it is "blocking" and does not allow for editing the graph
class SetNodeInputValue(OpenMaya.MPxCommand):
    kPluginCmdName = "iograft_set_input"

    kNodeNameFlag = "-n"
    kNodeNameLongFlag = "-nodename"

    kInputNameFlag = "-i"
    kInputNameLongFlag = "-input"

    kValueFlag = "-v"
    kValueLongFlag = "-value"

    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)

    @staticmethod
    def cmdCreator():
        return SetNodeInputValue()

    @classmethod
    def syntaxCreator(cls):
        syntax = OpenMaya.MSyntax()
        syntax.addFlag(cls.kNodeNameFlag,
                       cls.kNodeNameLongFlag,
                       OpenMaya.MSyntax.kString)
        syntax.addFlag(cls.kInputNameFlag,
                       cls.kInputNameLongFlag,
                       OpenMaya.MSyntax.kString)
        syntax.addFlag(cls.kValueFlag,
                       cls.kValueLongFlag,
                       OpenMaya.MSyntax.kString)
        return syntax

    def doIt(self, args):
        argData = OpenMaya.MArgDatabase(self.syntax(), args)

        state = _getState()
        if state._core is None:
            OpenMaya.MGlobal.displayWarning(
                                "No iograft instance currently running.")
            return

        # Load the requested graph.
        if not argData.isFlagSet(self.kNodeNameFlag):
            OpenMaya.MGlobal.displayWarning("The node name flag is required.")
            return
        node_name = argData.flagArgumentString(self.kNodeNameFlag, 0)

        if not argData.isFlagSet(self.kInputNameFlag):
            OpenMaya.MGlobal.displayWarning("The input name flag is required.")
            return
        input_name = argData.flagArgumentString(self.kInputNameFlag, 0)

        if not argData.isFlagSet(self.kValueFlag):
            OpenMaya.MGlobal.displayWarning("The value flag is required.")
            return
        value = argData.flagArgumentString(self.kValueFlag, 0)

        # Set the value.
        result = state._core.SetNodeInputValue(node_name, input_name, value)
        if not result:
            OpenMaya.MGlobal.displayError("Setting node input failed.")
        else:
            OpenMaya.MGlobal.displayInfo("Setting node input was successful.")


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
        pluginFn.registerCommand(LoadGraphCommand.kPluginCmdName,
                                 LoadGraphCommand.cmdCreator,
                                 LoadGraphCommand.syntaxCreator)
        pluginFn.registerCommand(ExecuteGraphCommand.kPluginCmdName,
                                 ExecuteGraphCommand.cmdCreator)
        pluginFn.registerCommand(SetNodeInputValue.kPluginCmdName,
                                 SetNodeInputValue.cmdCreator,
                                 SetNodeInputValue.syntaxCreator)

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
