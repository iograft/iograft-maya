# Copyright 2023 Fabrica Software, LLC

import iograft
import iobasictypes

from iogmaya_threading import maya_main_thread


class GetParentTransform(iograft.Node):
    """
    Given a DAG node, return that node's parent transform node. Returns
    the closest ancestor node that is a transform.
    """
    node = iograft.InputDefinition("node", iobasictypes.String())
    parent_transform = iograft.OutputDefinition("parent_transform",
                                                iobasictypes.String())

    @classmethod
    def GetDefinition(cls):
        node = iograft.NodeDefinition("get_parent_transform")
        node.SetNamespace("maya")
        node.SetMenuPath("Maya")
        node.AddInput(cls.node)
        node.AddOutput(cls.parent_transform)
        return node

    @staticmethod
    def Create():
        return GetParentTransform()

    @maya_main_thread
    def Process(self, data):
        import maya.cmds
        node = iograft.GetInput(self.node, data)

        # Ensure that the node exists.
        if not maya.cmds.objExists(node):
            raise KeyError("Node: '{}' does not exist.".format(node))

        # Get the relatives of type parent.
        relative_list = maya.cmds.listRelatives([node],
                                                fullPath=True,
                                                type="transform",
                                                parent=True)

        # Check if the list is empty (meaning there is no parent), and
        # raise an exception if so.
        if relative_list is None or len(relative_list) == 0:
            raise ValueError(
                "Node: '{}' does not have a transform parent.".format(node))

        iograft.SetOutput(self.parent_transform, data, relative_list[0])


def LoadPlugin(plugin):
    node = GetParentTransform.GetDefinition()
    plugin.RegisterNode(node, GetParentTransform.Create)
