# Copyright 2021 Fabrica Software, LLC

import iograft
import iobasictypes

from iogmaya_threading import maya_main_thread


class GetRootTransformsMaya(iograft.Node):
    """
    Given a list of nodes in Maya, get the root transforms of that list.
    """

    nodes = iograft.InputDefinition("nodes", iobasictypes.StringList())
    root_transforms = iograft.OutputDefinition("root_transforms",
                                               iobasictypes.StringList())

    @classmethod
    def GetDefinition(cls):
        node = iograft.NodeDefinition("get_root_transforms")
        node.AddInput(cls.nodes)
        node.AddOutput(cls.root_transforms)
        return node

    @staticmethod
    def Create():
        return GetRootTransformsMaya()

    @maya_main_thread
    def Process(self, data):
        import maya.cmds
        nodes = iograft.GetInput(self.nodes, data)

        # Get the full DAG paths of the nodes.
        nodes = maya.cmds.ls(nodes, long=True)

        # Get the root of the hierarchy for all passed in nodes.
        roots = set([node.split('|')[1] for node in nodes if '|' in node])

        # Limit the set to only transforms.
        roots = [root for root in roots
                 if maya.cmds.nodeType(root) == "transform"]

        iograft.SetOutput(self.root_transforms, data, roots)


def LoadPlugin(plugin):
    node = GetRootTransformsMaya.GetDefinition()
    plugin.RegisterNode(node, GetRootTransformsMaya.Create)
