# Copyright 2023 Fabrica Software, LLC

import iograft
import iobasictypes

from iogmaya_threading import maya_main_thread


class GetNodeAttribute(iograft.Node):
    """
    Get the value of a DAG node attribute.
    """
    node = iograft.InputDefinition("node", iobasictypes.String())
    attribute = iograft.InputDefinition("attribute", iobasictypes.String())
    value = iograft.MutableOutputDefinition("value")

    @classmethod
    def GetDefinition(cls):
        node = iograft.NodeDefinition("get_node_attribute")
        node.SetNamespace("maya")
        node.SetMenuPath("Maya")
        node.AddInput(cls.node)
        node.AddInput(cls.attribute)
        node.AddOutput(cls.value)
        return node

    @staticmethod
    def Create():
        return GetNodeAttribute()

    @maya_main_thread
    def Process(self, data):
        import maya.cmds
        node = iograft.GetInput(self.node, data)
        attribute = iograft.GetInput(self.attribute, data)

        # Ensure that the node exists.
        if not maya.cmds.objExists(node):
            raise KeyError("Node: '{}' does not exist.".format(node))

        # Ensure that the attribute exists.
        attribute_path = ".".join([node, attribute])
        if not maya.cmds.objExists(attribute_path):
            raise KeyError("Attribute: '{}' does not exist on node:"
                           " '{}'".format(attribute, node))

        # Get the value and return it.
        value = maya.cmds.getAttr(attribute_path)
        iograft.SetOutput(self.value, data, value)


def LoadPlugin(plugin):
    node = GetNodeAttribute.GetDefinition()
    plugin.RegisterNode(node, GetNodeAttribute.Create)
