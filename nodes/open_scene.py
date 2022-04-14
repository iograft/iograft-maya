# Copyright 2021 Fabrica Software, LLC

import iograft
import iobasictypes

from iogmaya_threading import maya_main_thread


class OpenSceneMaya(iograft.Node):
    """
    Open an existing scene in Maya.
    """
    filename = iograft.InputDefinition("filename", iobasictypes.Path())
    force = iograft.InputDefinition("force", iobasictypes.Bool(),
                                    default_value=True)
    out_filename = iograft.OutputDefinition("filename", iobasictypes.Path())

    @classmethod
    def GetDefinition(cls):
        node = iograft.NodeDefinition("open_scene_maya")
        node.AddInput(cls.filename)
        node.AddInput(cls.force)
        node.AddOutput(cls.out_filename)
        return node

    @staticmethod
    def Create():
        return OpenSceneMaya()

    @maya_main_thread
    def Process(self, data):
        import maya.cmds
        filename = iograft.GetInput(self.filename, data)
        force = iograft.GetInput(self.force, data)

        # Build the args to the file command.
        file_args = {
            "open": True
        }
        if force:
            file_args["force"] = True

        # Run the command.
        out_filename = maya.cmds.file(filename, **file_args)
        iograft.SetOutput(self.out_filename, data, out_filename)


def LoadPlugin(plugin):
    node = OpenSceneMaya.GetDefinition()
    plugin.RegisterNode(node, OpenSceneMaya.Create)
