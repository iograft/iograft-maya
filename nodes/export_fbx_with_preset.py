# Copyright 2023 Fabrica Software, LLC

import iograft
import iobasictypes

from iogmaya_threading import maya_main_thread


class ExportFbxWithPreset(iograft.Node):
    """
    Export the given nodes to an FBX file at the given path. A preset file
    (i.e. *.fbxexportpreset) must be provided containing the settings for the
    export. If the `nodes` list is empty, all objects in the scene will be
    exported.
    """
    filename = iograft.InputDefinition("filename", iobasictypes.Path())
    preset = iograft.InputDefinition("preset_path", iobasictypes.Path())
    nodes = iograft.InputDefinition("nodes", iobasictypes.StringList(),
                                    default_value=[])
    out_filename = iograft.OutputDefinition("filename", iobasictypes.Path())

    @classmethod
    def GetDefinition(cls):
        node = iograft.NodeDefinition("export_fbx_with_preset")
        node.SetNamespace("maya")
        node.SetMenuPath("Maya/FBX")
        node.AddInput(cls.filename)
        node.AddInput(cls.preset)
        node.AddInput(cls.nodes)
        node.AddOutput(cls.out_filename)
        return node

    @staticmethod
    def Create():
        return ExportFbxWithPreset()

    @maya_main_thread
    def Process(self, data):
        import maya.cmds

        # Ensure that the fbx plugin is loaded.
        maya.cmds.loadPlugin("fbxmaya")

        # Get the filename to export to.
        filename = iograft.GetInput(self.filename, data)
        preset = iograft.GetInput(self.preset, data)
        nodes = iograft.GetInput(self.nodes, data)

        # If the nodes list is not empty, export ONLY those nodes. This
        # requires changing the current selection, so first save the
        # previous selection so it can be restored later.
        if nodes:
            saved_selection = maya.cmds.ls(sl=True)
            maya.cmds.select(nodes, replace=True)

        # Build the FBX export settings.
        maya.cmds.FBXResetExport()
        maya.cmds.FBXLoadExportPresetFile("-f", preset)

        export_args = []
        export_args.append("-f")
        export_args.append(filename)
        if nodes:
            export_args.append("-s")
        maya.cmds.FBXExport(*export_args)

        # Restore the previous selection.
        if nodes:
            maya.cmds.select(saved_selection, replace=True)

        # Finally, output the filename of the generated FBX file.
        iograft.SetOutput(self.out_filename, data, filename)


def LoadPlugin(plugin):
    node = ExportFbxWithPreset.GetDefinition()
    plugin.RegisterNode(node, ExportFbxWithPreset.Create)
