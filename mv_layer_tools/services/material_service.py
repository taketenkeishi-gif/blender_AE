from ..repositories.material_repository import get_material, new_material


def build_image_material(image, alpha_mode="BLEND"):
    material_name = f"MVLT_MAT_{image.name}"
    material = get_material(material_name)
    if material is None:
        material = new_material(material_name)

    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (400, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (120, 0)
    image_node = nodes.new("ShaderNodeTexImage")
    image_node.location = (-220, 0)
    image_node.image = image

    links.new(image_node.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(image_node.outputs["Alpha"], bsdf.inputs["Alpha"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    material.blend_method = alpha_mode
    material.shadow_method = "NONE"
    return material
