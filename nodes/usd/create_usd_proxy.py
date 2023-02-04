# Copyright 2023 Fabrica Software, LLC

import iograft
import iobasictypes

from iogmaya_threading import maya_main_thread


class CreateUSDProxy(iograft.Node):
    """
    Create a USD proxy node which holds a USD stage which can be interacted
    with from Maya.
    """
    name = iograft.InputDefinition("name", iobasictypes.String(),
                                   default_value="stageShape1")
    filename = iograft.InputDefinition("usd_file", iobasictypes.Path(),
                                       default_value="")
    prim_path = iograft.InputDefinition("prim_path", iobasictypes.String(),
                                        default_value="")
    load_payloads = iograft.InputDefinition("load_payloads",
                                            iobasictypes.Bool(),
                                            default_value=True)
    select_node = iograft.InputDefinition("select", iobasictypes.Bool(),
                                          default_value=False)

    shape_node = iograft.OutputDefinition("shape_node", iobasictypes.String())

    @classmethod
    def GetDefinition(cls):
        node = iograft.NodeDefinition("create_usd_proxy")
        node.SetNamespace("maya_usd")
        node.SetMenuPath("Maya/USD")
        node.AddInput(cls.name)
        node.AddInput(cls.filename)
        node.AddInput(cls.prim_path)
        node.AddInput(cls.load_payloads)
        node.AddInput(cls.select_node)
        node.AddOutput(cls.shape_node)
        return node

    @staticmethod
    def Create():
        return CreateUSDProxy()

    @maya_main_thread
    def Process(self, data):
        import maya.cmds
        name = iograft.GetInput(self.name, data)
        select_node = iograft.GetInput(self.select_node, data)
        filename = iograft.GetInput(self.filename, data)
        prim_path = iograft.GetInput(self.prim_path, data)
        load_payloads = iograft.GetInput(self.load_payloads, data)

        # Verify that the USD plugin has been loaded.
        if not maya.cmds.pluginInfo("mayaUsdPlugin", query=True, loaded=True):
            raise RuntimeError("The mayaUsdPlugin has not been loaded.")

        # Build a dictionary of the arguments to createNode.
        create_args = {
            "skipSelect": not select_node
        }
        if name:
            create_args["name"] = name

        # Create the usd proxy shape.
        shape_node = maya.cmds.createNode('mayaUsdProxyShape', **create_args)

        # Set whether or not to load payloads.
        maya.cmds.setAttr(shape_node + ".loadPayloads", load_payloads)

        # If there is a filename input, set that on the proxy shape.
        if filename:
            maya.cmds.setAttr(shape_node + ".filePath",
                              filename,
                              type="string")

        # If there is a prim path specified, set the corresponding attribute.
        if prim_path:
            maya.cmds.setAttr(shape_node + ".primPath",
                              prim_path,
                              type="string")

        # Make additional connections and setup similar to
        # mayaUsd_createStageFromFile:
        # https://github.com/Autodesk/maya-usd/blob/dev/plugin/adsk/scripts/mayaUsd_createStageFromFile.mel
        maya.cmds.connectAttr('time1.outTime', shape_node + '.time')
        full_path = maya.cmds.ls(shape_node, long=True)
        iograft.SetOutput(self.shape_node, data, full_path[0])


def LoadPlugin(plugin):
    node = CreateUSDProxy.GetDefinition()
    plugin.RegisterNode(node, CreateUSDProxy.Create)
