# Copyright 2023 Fabrica Software, LLC

import iograft
import iobasictypes

from iogmaya_threading import maya_main_thread


class GetRootTransform(iograft.Node):
    """
    Return the root transform of a DAG node in Maya.
    """
    node = iograft.InputDefinition("node", iobasictypes.String())
    root_transform = iograft.OutputDefinition("root_transform",
                                              iobasictypes.String())

    @classmethod
    def GetDefinition(cls):
        node = iograft.NodeDefinition("get_root_transform")
        node.SetNamespace("maya")
        node.SetMenuPath("Maya")
        node.AddInput(cls.node)
        node.AddOutput(cls.root_transform)
        return node

    @staticmethod
    def Create():
        return GetRootTransform()

    @maya_main_thread
    def Process(self, data):
        import maya.cmds
        node = iograft.GetInput(self.node, data)

        # Ensure that the node exists.
        if not maya.cmds.objExists(node):
            raise KeyError("Node: '{}' does not exist.".format(node))

        # Get the full DAG path of the node.
        node = maya.cmds.ls([node], long=True)[0]

        # Get the root of the hierarchy for all passed in nodes.
        root_transform = node.split('|')[1] if '|' in node else ""
        if not root_transform:
            raise RuntimeError(
                "Could not find root transform for node: '{}'".format(node))

        # Return the full path to the root.
        root_transform = maya.cmds.ls(root_transform, long=True)[0]
        iograft.SetOutput(self.root_transform, data, root_transform)


def LoadPlugin(plugin):
    node = GetRootTransform.GetDefinition()
    plugin.RegisterNode(node, GetRootTransform.Create)
