# Copyright 2021 Fabrica Software, LLC

import iograft
import iobasictypes

from iogmaya_threading import maya_main_thread


class ImportFileMaya(iograft.Node):
    """
    Import a file into Maya.
    """
    filename = iograft.InputDefinition("filename", iobasictypes.Path())
    namespace = iograft.InputDefinition("namespace", iobasictypes.String())

    imported_nodes = iograft.OutputDefinition("imported_nodes",
                                              iobasictypes.StringList())

    @classmethod
    def GetDefinition(cls):
        node = iograft.NodeDefinition("import_file_maya")
        node.AddInput(cls.filename)
        node.AddInput(cls.namespace)
        node.AddOutput(cls.imported_nodes)
        return node

    @staticmethod
    def Create():
        return ImportFileMaya()

    @maya_main_thread
    def Process(self, data):
        import maya.cmds
        filename = iograft.GetInput(self.filename, data)
        namespace = iograft.GetInput(self.namespace, data)

        # Build the args to the file command.
        file_args = {
            "i": True,
            "rnn": True
        }

        if namespace:
            file_args["namespace"] = namespace

        # Run the command.
        new_nodes = maya.cmds.file(filename, **file_args)
        iograft.SetOutput(self.imported_nodes, data, new_nodes)


def LoadPlugin(plugin):
    node = ImportFileMaya.GetDefinition()
    plugin.RegisterNode(node, ImportFileMaya.Create)
