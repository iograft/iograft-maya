# Copyright 2023 Fabrica Software, LLC

import iograft
import iobasictypes
import iousdtypes

from iogmaya_threading import maya_main_thread


class GetUsdProxyStage(iograft.Node):
    """
    Output the underlying UsdStage object that a USD proxy node in Maya
    is wrapping.
    """
    proxy_shape_path = iograft.InputDefinition("proxy_shape_path",
                                               iobasictypes.String())
    stage = iograft.OutputDefinition("stage", iousdtypes.UsdStage())

    @classmethod
    def GetDefinition(cls):
        node = iograft.NodeDefinition("get_usd_proxy_stage")
        node.SetNamespace("maya_usd")
        node.SetMenuPath("Maya/USD")
        node.AddInput(cls.proxy_shape_path)
        node.AddOutput(cls.stage)
        return node

    @staticmethod
    def Create():
        return GetUsdProxyStage()

    @maya_main_thread
    def Process(self, data):
        proxy_shape_path = iograft.GetInput(self.proxy_shape_path, data)

        # Get the USD Stage through UFE.
        import mayaUsd.ufe
        stage = mayaUsd.ufe.getStage(proxy_shape_path)
        iograft.SetOutput(self.stage, data, stage)


def LoadPlugin(plugin):
    node = GetUsdProxyStage.GetDefinition()
    plugin.RegisterNode(node, GetUsdProxyStage.Create)
