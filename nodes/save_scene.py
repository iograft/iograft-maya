# Copyright 2021 Fabrica Software, LLC

import iograft
import iobasictypes

from iogmaya_threading import maya_main_thread


class SaveSceneMaya(iograft.Node):
    """
    Save a scene from Maya.
    """
    filename = iograft.InputDefinition("file", iobasictypes.Path())
    filetype = iograft.InputDefinition("filetype", iobasictypes.String(),
                                       default_value="")
    force = iograft.InputDefinition("force", iobasictypes.Bool(),
                                    default_value=True)
    out_filename = iograft.OutputDefinition("filename", iobasictypes.Path())

    @classmethod
    def GetDefinition(cls):
        node = iograft.NodeDefinition("save_scene_maya")
        node.AddInput(SaveSceneMaya.filename)
        node.AddInput(SaveSceneMaya.filetype)
        node.AddInput(SaveSceneMaya.force)
        node.AddOutput(SaveSceneMaya.out_filename)
        return node

    @staticmethod
    def Create():
        return SaveSceneMaya()

    @maya_main_thread
    def Process(self, data):
        import maya.cmds
        filename = iograft.GetInput(self.filename, data)
        filetype = iograft.GetInput(self.filetype, data)
        force = iograft.GetInput(self.force, data)

        # Check if the current filename matches the save file name, rename
        # if not.
        if maya.cmds.file(query=True, sceneName=True) != filename:
            maya.cmds.file(rename=filename)

        # Build the args to the file command.
        file_args = {
            "save": True
        }
        if filetype:
            file_args["type"] = filetype
        if force:
            file_args["force"] = True

        # Run the command.
        saved_filename = maya.cmds.file(**file_args)
        iograft.SetOutput(self.out_filename, data, saved_filename)


def LoadPlugin(plugin):
    node = SaveSceneMaya.GetDefinition()
    plugin.RegisterNode(node, SaveSceneMaya.Create)
