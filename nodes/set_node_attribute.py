# Copyright 2023 Fabrica Software, LLC

import iograft
import iobasictypes

from iogmaya_threading import maya_main_thread


class SetNodeAttribute(iograft.Node):
    """
    Set the value of a DAG node attribute.
    """
    node = iograft.InputDefinition("node", iobasictypes.String())
    attribute = iograft.InputDefinition("attribute", iobasictypes.String())
    value = iograft.MutableInputDefinition("value")
    value_type = iograft.InputDefinition("value_type", iobasictypes.String(),
                                         default_value="")
    out_node = iograft.OutputDefinition("node", iobasictypes.String())

    @classmethod
    def GetDefinition(cls):
        node = iograft.NodeDefinition("set_node_attribute")
        node.SetNamespace("maya")
        node.SetMenuPath("Maya")
        node.AddInput(cls.node)
        node.AddInput(cls.attribute)
        node.AddInput(cls.value)
        node.AddInput(cls.value_type)
        node.AddOutput(cls.out_node)
        return node

    @staticmethod
    def Create():
        return SetNodeAttribute()

    @maya_main_thread
    def Process(self, data):
        import maya.cmds
        node = iograft.GetInput(self.node, data)
        attribute = iograft.GetInput(self.attribute, data)
        value = iograft.GetInput(self.value, data)
        value_type = iograft.GetInput(self.value_type, data)

        # Ensure that the node exists.
        if not maya.cmds.objExists(node):
            raise KeyError("Node: '{}' does not exist.".format(node))

        # Ensure that the attribute exists.
        attribute_path = ".".join([node, attribute])
        if not maya.cmds.objExists(attribute_path):
            raise KeyError("Attribute: '{}' does not exist on node:"
                           " '{}'".format(attribute, node))

        # If the type of the data is defined, set it.
        command_args = {}
        if value_type:
            command_args["type"] = value_type

        # Attempt to set the value.
        maya.cmds.setAttr(attribute_path, value, **command_args)
        iograft.SetOutput(self.out_node, data, node)


def LoadPlugin(plugin):
    node = SetNodeAttribute.GetDefinition()
    plugin.RegisterNode(node, SetNodeAttribute.Create)
