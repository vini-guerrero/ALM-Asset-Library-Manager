bl_info = {
    "name": "Asset Library Manager",
    "description": "Asset Library Manager",
    "author": "Vinicius Guerrero & Matthias Stöckli",
    "version": (1, 0, 0),
    "blender": (2, 82, 0),
    "location": "3D View > Tools",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Asset Library Manager"
}

import bpy
import glob
import os

from bpy.props import (StringProperty, PointerProperty, BoolProperty, EnumProperty)
from bpy.types import (Panel, Menu, Operator, PropertyGroup)
from mathutils import Matrix, Vector, Euler

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

def console_get():
    for area in bpy.context.screen.areas:
        if area.type == 'CONSOLE':
            for space in area.spaces:
                if space.type == 'CONSOLE':
                    return area, space
    return None, None

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

def console_write(text):
    area, space = console_get()
    if space is None:
        return
    text = str(text)
    context = bpy.context.copy()
    context.update(dict(space=space,area=area))
    for line in text.split("\n"):
        bpy.ops.console.scrollback_append(context, text=line, type='OUTPUT')

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

def getAssetsFileTypes(self, context):
    scene = context.scene
    tool = scene.asset_library_manager
    fileTypes = []
    # Load File Types
    if tool.load_fbx: fileTypes.append(".fbx")
    if tool.load_gltf: fileTypes.append(".gltf")
    if tool.load_glb: fileTypes.append(".glb")
    if tool.load_dae: fileTypes.append(".dae")
    if tool.load_obj: fileTypes.append(".obj")
    return fileTypes

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

def populateAssetsFolders(self, context):
    scene = context.scene
    tool = scene.asset_library_manager
    root_folder = tool.root_folder
    assetsFolders = []
    fileTypes = getAssetsFileTypes(self, context)
    # Load File Types
    for root, subdirs, files in os.walk(root_folder):
        for file in files:
            if file.endswith((tuple(fileTypes))):
                fileNameWithExtension = file
                fileName = os.path.splitext(file)[0]
                fileExtension = os.path.splitext(file)[1]
                fileFullPath = os.path.join(root, file)
                folderFullPath = os.path.dirname(fileFullPath)
                fileFolder = os.path.basename(folderFullPath)
                item = (folderFullPath, fileFolder, "")
                if item not in assetsFolders:
                    assetsFolders.append(item)
    return assetsFolders

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

def populateAssetsInFolder(self, context):
    assetsInFolder = []
    scene = context.scene
    tool = scene.asset_library_manager
    root_folder = tool.root_folder
    asset_folders = tool.asset_folders
    if asset_folders:
        fileTypes = getAssetsFileTypes(self, context)
        assets = []
        for file in os.listdir(asset_folders):
            fileExtension = os.path.splitext(file)[1]
            if fileExtension in fileTypes:
                fileFullPath = os.path.join(asset_folders, file)
                asset = (fileFullPath, file , "")
                assetsInFolder.append(asset)
    return assetsInFolder

# ------------------------------------------------------------------------
#    Addon Scene Properties
# ------------------------------------------------------------------------

class AddonProperties(PropertyGroup):

    # Supported File Types To Load
    load_fbx: BoolProperty(name="FBX", description="Enable or Disable Extension", default=True)
    load_gltf: BoolProperty(name="GLTF", description="Enable or Disable Extension", default=True)
    load_glb: BoolProperty(name="GLB", description="Enable or Disable Extension", default=True)
    load_dae: BoolProperty(name="DAE", description="Enable or Disable Extension", default=True)
    load_obj: BoolProperty(name="OBJ", description="Enable or Disable Extension", default=True)
    # Add-On Internal Properties
    asset_to_save: PointerProperty(name="Asset", description="Select the asset you wish to save to library", type=bpy.types.Object)
    asset_collection_to_save: PointerProperty(name="Collection", description="Type in the desired collection to export assets from", type=bpy.types.Collection)
    root_folder: StringProperty(name="Root Folder", description="Select the desired path to root folder of assets", subtype="DIR_PATH")
    asset_folders: EnumProperty(name="Assets Folders", description="Available assets folders", items=populateAssetsFolders, default=None, options={'ANIMATABLE'}, update=None, get=None, set=None)
    current_asset: EnumProperty(name="Assets", description="Current assets in folder", items=populateAssetsInFolder, default=None, options={'ANIMATABLE'}, update=None, get=None, set=None)

# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------

class OT_ASSET_LIBRARY_MANAGER_IMPORT_ASSET_OT(Operator):
    bl_idname = "wm_alm.asset_library_manager_import_asset"
    bl_label = "Import Asset"
    bl_description = "Import selected asset from library folders"

    def execute(self, context):
        scene = context.scene
        tool = scene.asset_library_manager
        current_asset = tool.current_asset
        if current_asset:
            fileFullPath = current_asset
            fileName = os.path.splitext(fileFullPath)[0]
            fileExtension = os.path.splitext(fileFullPath)[1]
            fileTypes = getAssetsFileTypes(self, context)
            if fileExtension in fileTypes:
                if fileExtension == ".fbx": console_write("Load " + fileName + " as .fbx")
                elif fileExtension == ".gltf": console_write("Load " + fileName + " as .gltf")
                elif fileExtension == ".glb": console_write("Load " + fileName + " as .glb")
                elif fileExtension == ".dae": console_write("Load " + fileName + " as .dae")
                elif fileExtension == ".obj": console_write("Load " + fileName + " as .obj")
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class OT_ASSET_LIBRARY_MANAGER_SAVE_ASSET_OT(Operator):
    bl_idname = "wm_alm.asset_library_manager_save_asset"
    bl_label = "Save Asset"
    bl_description = "Saves selected asset into library folder"

    def execute(self, context):
        scene = context.scene
        tool = scene.asset_library_manager
        asset_to_save = tool.asset_to_save
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class OT_ASSET_LIBRARY_MANAGER_BATCH_SAVE_ASSETS_OT(Operator):
    bl_idname = "wm_alm.asset_library_manager_batch_save_assets"
    bl_label = "Save Asset Collection"
    bl_description = "Saves collection selected of asset into library folder"

    def execute(self, context):
        scene = context.scene
        tool = scene.asset_library_manager
        asset_to_save = tool.asset_to_save
        return {'FINISHED'}

# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------

class PT_ASSET_LIBRARY_MANAGER_MAIN_PANEL_PT(Panel):
    bl_idname = "obj_alm.game_assets_manager_main_panel"
    bl_label = "Asset Library Manager"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Asset Library Manager"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        tool = scene.asset_library_manager
        # File Type Box
        fileTypesBox = layout.box()
        fileTypesBox.label(text="File Types", icon='OUTLINER_OB_GROUP_INSTANCE')
        fileTypesRow = fileTypesBox.row()
        fileTypesRow.prop(tool, "load_fbx")
        fileTypesRow.prop(tool, "load_gltf")
        fileTypesRow.prop(tool, "load_glb")
        fileTypesRow.prop(tool, "load_dae")
        fileTypesRow.prop(tool, "load_obj")
        # Load Assets Box
        loadAssetsBox = layout.box()
        loadAssetsBox.label(text="Load Asset", icon='OUTLINER_OB_GROUP_INSTANCE')
        loadAssetsRow = loadAssetsBox.row()
        loadAssetsRow.prop(tool, "root_folder")
        loadAssetsRow = loadAssetsBox.row()
        loadAssetsRow.prop(tool, "asset_folders")
        loadAssetsRow = loadAssetsBox.row()
        loadAssetsRow.prop(tool, "current_asset")
        loadAssetsBox.operator("wm_alm.asset_library_manager_import_asset", icon="IMPORT")
        # Save Assets Box
        saveAssetsBox = layout.box()
        saveAssetsBox.label(text="Save Asset", icon='OUTLINER_OB_GROUP_INSTANCE')
        saveAssetsRow = saveAssetsBox.row()
        saveAssetsRow.prop(tool, "asset_to_save")
        saveAssetsRow = saveAssetsBox.row()
        saveAssetsRow.operator("wm_alm.asset_library_manager_save_asset", icon="EXPORT")
        saveAssetsRow = saveAssetsBox.row()
        saveAssetsRow.prop(tool, "asset_collection_to_save")
        saveAssetsRow = saveAssetsBox.row()
        saveAssetsRow.operator("wm_alm.asset_library_manager_batch_save_assets", icon="EXPORT")


# ------------------------------------------------------------------------
#    Addon Registration
# ------------------------------------------------------------------------

classes = (
    AddonProperties,
    PT_ASSET_LIBRARY_MANAGER_MAIN_PANEL_PT,
    OT_ASSET_LIBRARY_MANAGER_IMPORT_ASSET_OT,
    OT_ASSET_LIBRARY_MANAGER_SAVE_ASSET_OT,
    OT_ASSET_LIBRARY_MANAGER_BATCH_SAVE_ASSETS_OT
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.asset_library_manager = PointerProperty(type=AddonProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.asset_library_manager

if __name__ == "__main__":
    register()
