# Copyright 2022 Fabrica Software, LLC
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

import os
import platform
import sys

import maya.api.OpenMaya as OpenMaya
import maya.cmds
import maya.mel

import iograft


def maya_useNewAPI():
    pass


iograftMayaVersion = "0.9"
iograftShelfName = "iograft"
iograftIconPath = "iograft_icon.png"
iograftShelfButtons = {
    "start_iograft": {
        "label": "start_iograft",
        "command": "loadPlugin \"iograftmaya.py\";\nstart_iograft",
        "sourceType": "mel",
        "annotation": "Start iograft",
        "enableCommandRepeat": 0,
        "commandRepeatable": 0,
        "imageOverlayLabel": "start",
        "overlayLabelColor": (0.8, 0.8, 0.8),
        "useAlpha": 1,
        "overlayLabelBackColor": (0, 0, 0, 0.8),
        "style": "iconOnly"
    },
    "stop_iograft": {
        "label": "stop_iograft",
        "command": "loadPlugin \"iograftmaya.py\";\nstop_iograft",
        "sourceType": "mel",
        "annotation": "Stop iograft",
        "enableCommandRepeat": 0,
        "commandRepeatable": 0,
        "imageOverlayLabel": "stop",
        "overlayLabelColor": (0.8, 0.8, 0.8),
        "useAlpha": 1,
        "overlayLabelBackColor": (0, 0, 0, 0.8),
        "style": "iconOnly"
    },
    "iograft_ui": {
        "label": "iograft_ui",
        "command": "loadPlugin \"iograftmaya.py\";\niograft_ui",
        "sourceType": "mel",
        "annotation": "Launch iograft_ui",
        "enableCommandRepeat": 0,
        "commandRepeatable": 0,
        "imageOverlayLabel": "ui",
        "overlayLabelColor": (0.8, 0.8, 0.8),
        "useAlpha": 1,
        "overlayLabelBackColor": (0, 0, 0, 0.8),
        "style": "iconOnly"
    }
}


# Clear the iograft shelf.
def _clearShelf(delete_if_empty=True):
    if not maya.cmds.shelfLayout(iograftShelfName, exists=1):
        return

    shelf_items = maya.cmds.shelfLayout(iograftShelfName, q=1, ca=1) or []
    item_labels = [maya.cmds.shelfButton(i, q=1, label=1) for i in shelf_items]
    num_removed = 0
    for registered_button in iograftShelfButtons.keys():
        try:
            button_index = item_labels.index(registered_button)
        except ValueError:
            # Button not on the shelf.
            continue

        # Remove the button.
        maya.cmds.deleteUI(shelf_items[button_index])
        num_removed = num_removed + 1

    # If the shelf is now empty, remove it.
    if num_removed == len(shelf_items) and delete_if_empty:
        maya.cmds.deleteUI(iograftShelfName)


# Build the iograft default shelf.
def _buildShelf(loadPath):
    if maya.cmds.shelfLayout(iograftShelfName, exists=1):
        _clearShelf(delete_if_empty=False)
    else:
        # Create the shelf.
        top_level_shelf = maya.mel.eval("$tmpVar=$gShelfTopLevel")
        maya.cmds.shelfLayout(iograftShelfName, parent=top_level_shelf)

    # Create all of the registered buttons.
    resources_dir = os.path.join(loadPath, "resources")
    for button in iograftShelfButtons:
        maya.cmds.shelfButton(parent=iograftShelfName,
                              image=os.path.join(resources_dir,
                                                 iograftIconPath),
                              **iograftShelfButtons[button])


# The name of the Core object to be registered for the Maya session.
IOGRAFT_MAYA_CORE_NAME = "maya"


class StartIograftCommand(OpenMaya.MPxCommand):
    kPluginCmdName = "start_iograft"

    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)

    @staticmethod
    def cmdCreator():
        return StartIograftCommand()

    def doIt(self, args):
        # Initialize iograft if it is not yet initialized.
        if not iograft.IsInitialized():
            iograft.Initialize()

        # Ensure there is a "maya" iograft Core object created and setup
        # to handle requests.
        core = iograft.Core()
        iograft.RegisterCore(IOGRAFT_MAYA_CORE_NAME, core)

        # Ensure that the core's request handler is active so we can
        # connect a UI to it.
        core.StartRequestHandler()

        # Get the core address that clients (such as a UI) can connect to.
        core_address = core.GetClientAddress()
        OpenMaya.MGlobal.displayInfo("iograft Core: '{}' running at: {}".format(
                                        IOGRAFT_MAYA_CORE_NAME,
                                        core_address))


class StopIograftCommand(OpenMaya.MPxCommand):
    kPluginCmdName = "stop_iograft"

    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)

    @staticmethod
    def cmdCreator():
        return StopIograftCommand()

    def doIt(self, args):
        # If iograft is not initialized, nothing to do.
        if not iograft.IsInitialized():
            OpenMaya.MGlobal.displayWarning(
                            "The iograft API is not currently initialized.")
            return

        # Otherwise, clear the "maya" Core object and uninitialize iograft.
        try:
            iograft.UnregisterCore(IOGRAFT_MAYA_CORE_NAME)
        except KeyError:
            pass

        iograft.Uninitialize()
        OpenMaya.MGlobal.displayInfo("The iograft API has been uninitialized.")


class LaunchIograftUI(OpenMaya.MPxCommand):
    kPluginCmdName = "iograft_ui"

    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)

    @staticmethod
    def cmdCreator():
        return LaunchIograftUI()

    def doIt(self, args):
        import subprocess

        # Check that iograft is initialized.
        if not iograft.IsInitialized():
            OpenMaya.MGlobal.displayWarning(
                            "The iograft API has not been initialized.")
            return

        # Try to get the "maya" Core object.
        core_address = ""
        try:
            core = iograft.GetCore(IOGRAFT_MAYA_CORE_NAME,
                                   create_if_needed=False)
            core_address = core.GetClientAddress()
        except KeyError:
            OpenMaya.MGlobal.displayError("No iograft Core: '{}' is currently"
                                          " running.".format(
                                                    IOGRAFT_MAYA_CORE_NAME))
            return

        # On Linux platforms, prior to launching the iograft_ui, we must
        # clear the LD_LIBRARY_PATH to prevent the Qt libraries of Maya
        # conflicting with iograft's Qt libraries.
        # TODO(knowlonix): This can apply to ALL platforms once the unicode
        # environment errors are resolved in iograft.InitializeEnvironment()
        if platform.system() == "Linux":
            sub_env = os.environ.copy()
            sub_env.pop("LD_LIBRARY_PATH", None)

            # Launch the iograft_ui subprocess.
            subprocess.Popen(["iograft_ui", "-c", core_address], env=sub_env)
        else:
            # Launch the iograft_ui subprocess.
            subprocess.Popen(["iograft_ui", "-c", core_address])

        OpenMaya.MGlobal.displayInfo("iograft_ui launched.")


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

    # Register the iograft shelf.
    try:
        _buildShelf(pluginFn.loadPath())
    except:
        sys.stderr.write("Failed to add iograft shelf.\n")
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

    # Deregister the iograft shelf.
    try:
        _clearShelf(delete_if_empty=True)
    except:
        sys.stderr.write("Failed to remove iograft shelf.\n")
        raise
