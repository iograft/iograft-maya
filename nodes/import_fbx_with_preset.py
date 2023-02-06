# Copyright 2023 Fabrica Software, LLC

import iograft
import iobasictypes

from iogmaya_threading import maya_main_thread


class ImportFbxWithPreset(iograft.Node):
    """
    Import the objects from the given FBX file using the settings found in
    the `preset_path`. The `preset_path` must point to a preset file (i.e.
    *.fbximportpreset) containing the import settings. If a take number is
    provided, animation for that take is imported. If the take number is
    set to 0 (the default), no animation is imported.
    """
    filename = iograft.InputDefinition("filename", iobasictypes.Path())
    preset = iograft.InputDefinition("preset_path", iobasictypes.Path())
    take = iograft.InputDefinition("take", iobasictypes.Int(),
                                   default_value=0)

    @classmethod
    def GetDefinition(cls):
        node = iograft.NodeDefinition("import_fbx_with_preset")
        node.SetNamespace("maya")
        node.SetMenuPath("Maya/FBX")
        node.AddInput(cls.filename)
        node.AddInput(cls.preset)
        node.AddInput(cls.take)
        return node

    @staticmethod
    def Create():
        return ImportFbxWithPreset()

    @maya_main_thread
    def Process(self, data):
        import maya.cmds

        # Ensure that the fbx plugin is loaded.
        maya.cmds.loadPlugin("fbxmaya")

        # Get the filename to import from.
        filename = iograft.GetInput(self.filename, data)
        preset = iograft.GetInput(self.preset, data)
        take = iograft.GetInput(self.take, data)

        # Build the FBX import settings.
        maya.cmds.FBXResetImport()
        maya.cmds.FBXLoadImportPresetFile("-f", preset)

        import_args = []
        import_args.append("-f")
        import_args.append(filename)
        import_args.append("-t")
        import_args.append(take)
        maya.cmds.FBXImport(*import_args)


def LoadPlugin(plugin):
    node = ImportFbxWithPreset.GetDefinition()
    plugin.RegisterNode(node, ImportFbxWithPreset.Create)
