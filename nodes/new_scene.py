# Copyright 2021 Fabrica Software, LLC

import iograft
import iobasictypes

from iogmaya_threading import maya_main_thread


class NewSceneMaya(iograft.Node):
    """
    Create a new scene in Maya.
    """
    # Input to define whether or not to "force" the new scene if the current
    # scene needs to be saved.
    force = iograft.InputDefinition("force", iobasictypes.Bool(),
                                    default_value=True)

    @classmethod
    def GetDefinition(cls):
        node = iograft.NodeDefinition("new_scene_maya")
        node.AddInput(cls.force)
        return node

    @staticmethod
    def Create():
        return NewSceneMaya()

    @maya_main_thread
    def Process(self, data):
        import maya.cmds
        force = iograft.GetInput(self.force, data)

        # Build the args to the file command.
        file_args = {
            "new": True
        }
        if force:
            file_args["force"] = True

        # Run the command.
        maya.cmds.file(**file_args)


def LoadPlugin(plugin):
    node = NewSceneMaya.GetDefinition()
    plugin.RegisterNode(node, NewSceneMaya.Create)
