# Copyright 2023 Fabrica Software, LLC

import iograft
import iobasictypes

from iogmaya_threading import maya_main_thread


class CreateNode(iograft.Node):
    """
    Create a new DAG node in Maya with the specified type. Outputs the name
    of the created node.
    """
    node_type = iograft.InputDefinition("node_type", iobasictypes.String())
    name = iograft.InputDefinition("name", iobasictypes.String(),
                                   default_value="")
    parent = iograft.InputDefinition("parent", iobasictypes.String(),
                                     default_value="")
    select_node = iograft.InputDefinition("select", iobasictypes.Bool(),
                                          default_value=False)

    out_node = iograft.OutputDefinition("node", iobasictypes.String())

    @classmethod
    def GetDefinition(cls):
        node = iograft.NodeDefinition("create_node")
        node.SetNamespace("maya")
        node.SetMenuPath("Maya")
        node.AddInput(cls.node_type)
        node.AddInput(cls.name)
        node.AddInput(cls.parent)
        node.AddInput(cls.select_node)
        node.AddOutput(cls.out_node)
        return node

    @staticmethod
    def Create():
        return CreateNode()

    @maya_main_thread
    def Process(self, data):
        import maya.cmds
        node_type = iograft.GetInput(self.node_type, data)
        name = iograft.GetInput(self.name, data)
        parent = iograft.GetInput(self.parent, data)
        select_node = iograft.GetInput(self.select_node, data)

        # Build a dictionary of the arguments to createNode.
        create_args = {
            "skipSelect": not select_node
        }
        if name:
            create_args["name"] = name

        if parent:
            # Check that the parent node actually exists and is a transform.
            if not maya.cmds.objExists(parent):
                raise KeyError(
                        "Parent node: '{}' does not exist.".format(parent))

            create_args["parent"] = parent

        # Attempt to create the node.
        node = maya.cmds.createNode(node_type, **create_args)

        # Get the full path to the node.
        path_list = maya.cmds.ls([node], long=True)
        full_path = path_list[0]
        iograft.SetOutput(self.out_node, data, full_path)


def LoadPlugin(plugin):
    node = CreateNode.GetDefinition()
    plugin.RegisterNode(node, CreateNode.Create)
