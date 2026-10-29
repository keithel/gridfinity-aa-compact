"""FeatureScript code generator for the 2x2 Gridfinity AA Compact Battery Holder."""

from __future__ import annotations

from src.gridfinity_spec import DIMENSIONS, get_honeycomb_slots


def generate_feature_studio_code() -> str:
    """Return the complete FeatureScript source for Gridfinity AA Holder Generator."""
    slots = get_honeycomb_slots()
    aa_slots = [s for s in slots if s.kind == "AA"]
    grabber_slot = next(s for s in slots if s.kind == "GRABBER")

    aa_vectors_str = ",\n        ".join(
        f"vector({s.x_mm:.4f} * millimeter, {s.y_mm:.4f} * millimeter)" for s in aa_slots
    )

    return f"""FeatureScript 2411;
import(path : "onshape/std/geometry.fs", version : "2411.0");

function makeRoundedRectPrism(context is Context, id is Id, centerX is ValueWithUnits,
    centerY is ValueWithUnits, spanX is ValueWithUnits, spanY is ValueWithUnits,
    cornerRadius is ValueWithUnits, zMin is ValueWithUnits, zMax is ValueWithUnits)
{{
    var skPlane = plane(vector(0 * millimeter, 0 * millimeter, zMin), vector(0, 0, 1), vector(1, 0, 0));
    var sketch = newSketchOnPlane(context, id + "sketch", {{
        "sketchPlane" : skPlane
    }});
    skRectangle(sketch, "rect", {{
        "firstCorner" : vector(centerX - spanX / 2, centerY - spanY / 2),
        "secondCorner" : vector(centerX + spanX / 2, centerY + spanY / 2)
    }});
    skSolve(sketch);

    opExtrude(context, id + "extrude", {{
        "entities" : qSketchRegion(id + "sketch"),
        "direction" : vector(0, 0, 1),
        "endBound" : BoundingType.BLIND,
        "endDepth" : zMax - zMin
    }});

    if (cornerRadius > 0 * millimeter)
    {{
        opFillet(context, id + "fillet", {{
            "entities" : qNonCapEntity(id + "extrude", EntityType.EDGE),
            "radius" : cornerRadius
        }});
    }}

    opDeleteBodies(context, id + "deleteSketch", {{
        "entities" : qCreatedBy(id + "sketch", EntityType.BODY)
    }});
}}

function makeGridfinityFoot(context is Context, id is Id, centerX is ValueWithUnits,
    centerY is ValueWithUnits, zBase is ValueWithUnits)
{{
    // Lower foot section: zBase to zBase + 2.85 mm (37.20 x 37.20 mm, R1.60 mm) with 0.80 mm bottom 45-deg chamfer
    makeRoundedRectPrism(context, id + "lower", centerX, centerY,
        37.20 * millimeter, 37.20 * millimeter, 1.60 * millimeter,
        zBase, zBase + 2.85 * millimeter);

    opChamfer(context, id + "lowerChamfer", {{
        "entities" : qCapEntity(id + "lower" + "extrude", CapType.START, EntityType.EDGE),
        "chamferType" : ChamferType.EQUAL_OFFSETS,
        "width" : 0.80 * millimeter
    }});

    // Upper foot section: zBase + 2.60 mm to zBase + 5.00 mm (41.50 x 41.50 mm, R3.75 mm) with 2.15 mm bottom 45-deg chamfer
    makeRoundedRectPrism(context, id + "upper", centerX, centerY,
        41.50 * millimeter, 41.50 * millimeter, 3.75 * millimeter,
        zBase + 2.60 * millimeter, zBase + 5.00 * millimeter);

    opChamfer(context, id + "upperChamfer", {{
        "entities" : qCapEntity(id + "upper" + "extrude", CapType.START, EntityType.EDGE),
        "chamferType" : ChamferType.EQUAL_OFFSETS,
        "width" : 2.15 * millimeter
    }});

    opBoolean(context, id + "unionFoot", {{
        "tools" : qUnion([
            qCreatedBy(id + "upper", EntityType.BODY),
            qCreatedBy(id + "lower", EntityType.BODY)
        ]),
        "operationType" : BooleanOperationType.UNION
    }});
}}

function makeCylinderZ(context is Context, id is Id, centerX is ValueWithUnits,
    centerY is ValueWithUnits, diameter is ValueWithUnits,
    zMin is ValueWithUnits, zMax is ValueWithUnits)
{{
    fCylinder(context, id, {{
        "bottomCenter" : vector(centerX, centerY, zMin),
        "topCenter" : vector(centerX, centerY, zMax),
        "radius" : diameter / 2
    }});
}}

function makeFunnelConeZ(context is Context, id is Id, centerX is ValueWithUnits,
    centerY is ValueWithUnits, topDiameter is ValueWithUnits, chamferWidth is ValueWithUnits,
    zMin is ValueWithUnits, zMax is ValueWithUnits)
{{
    var skPlane = plane(vector(0 * millimeter, 0 * millimeter, zMin), vector(0, 0, 1), vector(1, 0, 0));
    var sketch = newSketchOnPlane(context, id + "sketch", {{
        "sketchPlane" : skPlane
    }});
    skCircle(sketch, "circle", {{
        "center" : vector(centerX, centerY),
        "radius" : topDiameter / 2
    }});
    skSolve(sketch);

    opExtrude(context, id + "extrude", {{
        "entities" : qSketchRegion(id + "sketch"),
        "direction" : vector(0, 0, 1),
        "endBound" : BoundingType.BLIND,
        "endDepth" : zMax - zMin
    }});

    opChamfer(context, id + "chamfer", {{
        "entities" : qCapEntity(id + "extrude", CapType.START, EntityType.EDGE),
        "chamferType" : ChamferType.EQUAL_OFFSETS,
        "width" : chamferWidth
    }});

    opDeleteBodies(context, id + "deleteSketch", {{
        "entities" : qCreatedBy(id + "sketch", EntityType.BODY)
    }});
}}

function makeBottomGrabberRingGroove(context is Context, id is Id, centerX is ValueWithUnits,
    centerY is ValueWithUnits, zSurface is ValueWithUnits, depth is ValueWithUnits)
{{
    // Concentric ring groove (ID 15.50 mm, OD 16.50 mm) around the Bottom Bin grabber funnel at Z = 56.00 mm,
    // clipped cleanly to the flat 77.60 x 77.60 mm shoulder so it never touches the stacking lip or AA pockets
    makeCylinderZ(context, id + "ringOuter", centerX, centerY,
        16.50 * millimeter, zSurface - depth, zSurface + 0.50 * millimeter);
    makeCylinderZ(context, id + "ringInner", centerX, centerY,
        15.50 * millimeter, zSurface - depth - 0.50 * millimeter, zSurface + 1.00 * millimeter);
    opBoolean(context, id + "ringTube", {{
        "tools" : qCreatedBy(id + "ringInner", EntityType.BODY),
        "targets" : qCreatedBy(id + "ringOuter", EntityType.BODY),
        "operationType" : BooleanOperationType.SUBTRACTION
    }});

    makeRoundedRectPrism(context, id + "shoulderClip", 0 * millimeter, 0 * millimeter,
        77.60 * millimeter, 77.60 * millimeter, 1.00 * millimeter,
        zSurface - depth - 0.50 * millimeter, zSurface + 1.00 * millimeter);
    opBoolean(context, id + "clipRingToShoulder", {{
        "tools" : qUnion([
            qCreatedBy(id + "ringOuter", EntityType.BODY),
            qCreatedBy(id + "shoulderClip", EntityType.BODY)
        ]),
        "operationType" : BooleanOperationType.INTERSECTION
    }});
}}

function makeTopGrabberMagnetIcon(context is Context, id is Id, centerX is ValueWithUnits,
    zSurface is ValueWithUnits, depth is ValueWithUnits)
{{
    // Debossed U-Magnet icon centered on the 6.99 mm front-right deck (Y in [-40.75, -35.75 mm], width 4.50 mm, height 5.00 mm, ~1.00 mm margin top & bottom)
    var zMin = zSurface - depth;
    var zMax = zSurface + 0.50 * millimeter;
    var archCenterY = -38.50 * millimeter;

    // 1. Semicircular bottom bend (R_out = 2.25 mm, R_in = 1.05 mm, stroke = 1.20 mm, Y <= -38.45 mm)
    makeCylinderZ(context, id + "archOuterCyl", centerX, archCenterY,
        4.50 * millimeter, zMin, zMax);
    makeCylinderZ(context, id + "archInnerCyl", centerX, archCenterY,
        2.10 * millimeter, zMin - 0.50 * millimeter, zMax + 0.50 * millimeter);
    opBoolean(context, id + "archRing", {{
        "tools" : qCreatedBy(id + "archInnerCyl", EntityType.BODY),
        "targets" : qCreatedBy(id + "archOuterCyl", EntityType.BODY),
        "operationType" : BooleanOperationType.SUBTRACTION
    }});

    fCuboid(context, id + "lowerHalfClip", {{
        "corner1" : vector(centerX - 3.00 * millimeter, -41.50 * millimeter, zMin - 0.50 * millimeter),
        "corner2" : vector(centerX + 3.00 * millimeter, -38.45 * millimeter, zMax + 0.50 * millimeter)
    }});
    opBoolean(context, id + "clipArchLowerHalf", {{
        "tools" : qUnion([
            qCreatedBy(id + "archOuterCyl", EntityType.BODY),
            qCreatedBy(id + "lowerHalfClip", EntityType.BODY)
        ]),
        "operationType" : BooleanOperationType.INTERSECTION
    }});

    // 2. Left and right straight vertical legs of the U-arch (Y in [-38.50, -36.95 mm])
    fCuboid(context, id + "leftLeg", {{
        "corner1" : vector(centerX - 2.25 * millimeter, archCenterY, zMin),
        "corner2" : vector(centerX - 1.05 * millimeter, -36.95 * millimeter, zMax)
    }});
    fCuboid(context, id + "rightLeg", {{
        "corner1" : vector(centerX + 1.05 * millimeter, archCenterY, zMin),
        "corner2" : vector(centerX + 2.25 * millimeter, -36.95 * millimeter, zMax)
    }});
    opBoolean(context, id + "unionUArch", {{
        "tools" : qUnion([
            qCreatedBy(id + "archOuterCyl", EntityType.BODY),
            qCreatedBy(id + "leftLeg", EntityType.BODY),
            qCreatedBy(id + "rightLeg", EntityType.BODY)
        ]),
        "operationType" : BooleanOperationType.UNION
    }});

    // 3. Left and right magnet pole tips (Y in [-36.55, -35.75 mm], separated from U-arch by a 0.40 mm ridge)
    fCuboid(context, id + "leftPoleTip", {{
        "corner1" : vector(centerX - 2.25 * millimeter, -36.55 * millimeter, zMin),
        "corner2" : vector(centerX - 1.05 * millimeter, -35.75 * millimeter, zMax)
    }});
    fCuboid(context, id + "rightPoleTip", {{
        "corner1" : vector(centerX + 1.05 * millimeter, -36.55 * millimeter, zMin),
        "corner2" : vector(centerX + 2.25 * millimeter, -35.75 * millimeter, zMax)
    }});
}}

annotation {{ "Feature Type Name" : "Bottom Bin (2x2 8U) Generator" }}
export const buildBottomBin = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {{
    }}
    {{
        // Main outer body + stacking lip outer envelope: 83.50 x 83.50 mm (R3.75 mm) from Z = 4.75 to 60.40 mm
        makeRoundedRectPrism(context, id + "bottomBinBody", 0 * millimeter, 0 * millimeter,
            {DIMENSIONS["outer_span_mm"]:.2f} * millimeter, {DIMENSIONS["outer_span_mm"]:.2f} * millimeter,
            {DIMENSIONS["outer_corner_radius_mm"]:.2f} * millimeter,
            4.75 * millimeter, {DIMENSIONS["bottom_bin_top_z_mm"]:.2f} * millimeter);

        var footOffsets = [-21.00 * millimeter, 21.00 * millimeter];
        var footIdx = 0;
        for (var fx in footOffsets)
        {{
            for (var fy in footOffsets)
            {{
                makeGridfinityFoot(context, id + ("foot" ~ footIdx), fx, fy, 0.00 * millimeter);
                footIdx += 1;
            }}
        }}

        // Solid floor core bridging inter-foot valley under pockets (z = 2.80 to 5.00 mm, leaving 1.20 mm floor below Z = 4.00 mm)
        makeRoundedRectPrism(context, id + "floorCore", 0 * millimeter, 0 * millimeter,
            79.20 * millimeter, 79.20 * millimeter, 1.60 * millimeter,
            2.80 * millimeter, 5.00 * millimeter);

        var addBodies = qUnion([
            qCreatedBy(id + "bottomBinBody", EntityType.BODY),
            qCreatedBy(id + "foot0", EntityType.BODY),
            qCreatedBy(id + "foot1", EntityType.BODY),
            qCreatedBy(id + "foot2", EntityType.BODY),
            qCreatedBy(id + "foot3", EntityType.BODY),
            qCreatedBy(id + "floorCore", EntityType.BODY)
        ]);

        opBoolean(context, id + "unionMain", {{
            "tools" : addBodies,
            "operationType" : BooleanOperationType.UNION
        }});

        // Subtract Gridfinity top stacking lip inner recess (Z = 56.00 to 60.40 mm)
        // Lower lip recess: 82.10 x 82.10 mm (R3.05 mm) with 1.90 mm bottom 45-deg bevel -> 78.30 x 78.30 mm (R1.15 mm) at Z = 56.00 mm
        makeRoundedRectPrism(context, id + "lipCutLower", 0 * millimeter, 0 * millimeter,
            82.10 * millimeter, 82.10 * millimeter, 3.05 * millimeter,
            56.00 * millimeter, 60.60 * millimeter);
        opChamfer(context, id + "lipCutLowerChamfer", {{
            "entities" : qCapEntity(id + "lipCutLower" + "extrude", CapType.START, EntityType.EDGE),
            "chamferType" : ChamferType.EQUAL_OFFSETS,
            "width" : 1.90 * millimeter
        }});

        // Upper lip 45-deg entry bevel: Z = 59.70 to 61.00 mm (83.30 x 83.30 mm, R3.65 mm) with 0.60 mm bottom chamfer
        makeRoundedRectPrism(context, id + "lipCutUpper", 0 * millimeter, 0 * millimeter,
            83.30 * millimeter, 83.30 * millimeter, 3.65 * millimeter,
            59.70 * millimeter, 61.00 * millimeter);
        opChamfer(context, id + "lipCutUpperChamfer", {{
            "entities" : qCapEntity(id + "lipCutUpper" + "extrude", CapType.START, EntityType.EDGE),
            "chamferType" : ChamferType.EQUAL_OFFSETS,
            "width" : 0.60 * millimeter
        }});

        var aaCenters = [
        {aa_vectors_str}
        ];

        var cutQueries = [
            qCreatedBy(id + "lipCutLower", EntityType.BODY),
            qCreatedBy(id + "lipCutUpper", EntityType.BODY)
        ];

        var aaIdx = 0;
        for (var pt in aaCenters)
        {{
            var holeId = id + ("aaPocket" ~ aaIdx);
            makeCylinderZ(context, holeId, pt[0], pt[1],
                {DIMENSIONS["aa_bore_diameter_mm"]:.2f} * millimeter,
                {DIMENSIONS["bottom_floor_z_mm"]:.2f} * millimeter,
                61.00 * millimeter);
            cutQueries = append(cutQueries, qCreatedBy(holeId, EntityType.BODY));
            aaIdx += 1;
        }}

        // Corner grabber blind receptacle at (+31.60, -27.36), Ø12.80 mm, floor Z = 4.00 mm to 56.00 mm + 1.00 mm x 45° funnel
        makeCylinderZ(context, id + "grabberBore",
            {grabber_slot.x_mm:.4f} * millimeter, {grabber_slot.y_mm:.4f} * millimeter,
            {DIMENSIONS["grabber_bore_diameter_mm"]:.2f} * millimeter,
            {DIMENSIONS["bottom_floor_z_mm"]:.2f} * millimeter,
            57.00 * millimeter);
        cutQueries = append(cutQueries, qCreatedBy(id + "grabberBore", EntityType.BODY));

        makeFunnelConeZ(context, id + "grabberFunnel",
            {grabber_slot.x_mm:.4f} * millimeter, {grabber_slot.y_mm:.4f} * millimeter,
            14.80 * millimeter, 1.00 * millimeter,
            55.00 * millimeter, 57.00 * millimeter);
        cutQueries = append(cutQueries, qCreatedBy(id + "grabberFunnel", EntityType.BODY));

        // Concentric target ring groove on Bottom Bin shoulder around grabber slot
        makeBottomGrabberRingGroove(context, id + "grabberRingGroove",
            {grabber_slot.x_mm:.4f} * millimeter, {grabber_slot.y_mm:.4f} * millimeter,
            56.00 * millimeter, 0.80 * millimeter);
        cutQueries = append(cutQueries, qCreatedBy(id + "grabberRingGroove", EntityType.BODY));

        opBoolean(context, id + "subtractPockets", {{
            "tools" : qUnion(cutQueries),
            "targets" : qCreatedBy(id + "bottomBinBody", EntityType.BODY),
            "operationType" : BooleanOperationType.SUBTRACTION
        }});

        setProperty(context, {{
            "entities" : qCreatedBy(id, EntityType.BODY),
            "propertyType" : PropertyType.NAME,
            "value" : "Bottom Bin"
        }});
        setProperty(context, {{
            "entities" : qCreatedBy(id, EntityType.BODY),
            "propertyType" : PropertyType.APPEARANCE,
            "value" : color(0.18, 0.36, 0.62)
        }});
    }});

annotation {{ "Feature Type Name" : "Top Bin (2x2 4U) Generator" }}
export const buildTopBin = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {{
    }}
    {{
        var zBase = {DIMENSIONS["top_bin_base_z_mm"]:.2f} * millimeter;
        var zTop = {DIMENSIONS["top_bin_top_z_mm"]:.2f} * millimeter;

        // Main low-profile body: 83.50 x 83.50 mm (R3.75 mm) from Z = 60.75 to 84.00 mm
        makeRoundedRectPrism(context, id + "topBinBody", 0 * millimeter, 0 * millimeter,
            {DIMENSIONS["outer_span_mm"]:.2f} * millimeter, {DIMENSIONS["outer_span_mm"]:.2f} * millimeter,
            {DIMENSIONS["outer_corner_radius_mm"]:.2f} * millimeter,
            zBase + 4.75 * millimeter, zTop);

        var footOffsets = [-21.00 * millimeter, 21.00 * millimeter];
        var footIdx = 0;
        for (var fx in footOffsets)
        {{
            for (var fy in footOffsets)
            {{
                makeGridfinityFoot(context, id + ("foot" ~ footIdx), fx, fy, zBase);
                footIdx += 1;
            }}
        }}

        // Solid floor core bridging inter-foot valley under pockets (zBase + 2.80 to zBase + 5.00 mm, leaving 1.20 mm floor below Z = 60.00 mm)
        makeRoundedRectPrism(context, id + "floorCore", 0 * millimeter, 0 * millimeter,
            79.20 * millimeter, 79.20 * millimeter, 1.60 * millimeter,
            zBase + 2.80 * millimeter, zBase + 5.00 * millimeter);

        var addBodies = qUnion([
            qCreatedBy(id + "topBinBody", EntityType.BODY),
            qCreatedBy(id + "foot0", EntityType.BODY),
            qCreatedBy(id + "foot1", EntityType.BODY),
            qCreatedBy(id + "foot2", EntityType.BODY),
            qCreatedBy(id + "foot3", EntityType.BODY),
            qCreatedBy(id + "floorCore", EntityType.BODY)
        ]);

        opBoolean(context, id + "unionMain", {{
            "tools" : addBodies,
            "operationType" : BooleanOperationType.UNION
        }});

        var aaCenters = [
        {aa_vectors_str}
        ];

        var cutQueries = [];
        var aaIdx = 0;
        for (var pt in aaCenters)
        {{
            var holeId = id + ("aaPocket" ~ aaIdx);
            makeCylinderZ(context, holeId, pt[0], pt[1],
                {DIMENSIONS["aa_bore_diameter_mm"]:.2f} * millimeter,
                {DIMENSIONS["top_floor_z_mm"]:.2f} * millimeter,
                zTop + 1.00 * millimeter);
            cutQueries = append(cutQueries, qCreatedBy(holeId, EntityType.BODY));
            aaIdx += 1;
        }}

        // Corner grabber pass-through hole at (+31.60, -27.36), Ø12.80 mm cutting completely through Z = 56.00 to 84.00 mm
        makeCylinderZ(context, id + "grabberThrough",
            {grabber_slot.x_mm:.4f} * millimeter, {grabber_slot.y_mm:.4f} * millimeter,
            {DIMENSIONS["grabber_bore_diameter_mm"]:.2f} * millimeter,
            zBase - 1.00 * millimeter,
            zTop + 1.00 * millimeter);
        cutQueries = append(cutQueries, qCreatedBy(id + "grabberThrough", EntityType.BODY));

        // 1.00 mm x 45° top entry funnel at Z = 84.00 mm
        makeFunnelConeZ(context, id + "grabberFunnel",
            {grabber_slot.x_mm:.4f} * millimeter, {grabber_slot.y_mm:.4f} * millimeter,
            14.80 * millimeter, 1.00 * millimeter,
            zTop - 1.00 * millimeter, zTop + 1.00 * millimeter);
        cutQueries = append(cutQueries, qCreatedBy(id + "grabberFunnel", EntityType.BODY));

        // Debossed U-Magnet icon on the front-right deck of the Top Bin
        makeTopGrabberMagnetIcon(context, id + "grabberMagnetIcon",
            {grabber_slot.x_mm:.4f} * millimeter, zTop, 0.80 * millimeter);
        cutQueries = append(cutQueries, qCreatedBy(id + "grabberMagnetIcon", EntityType.BODY));

        // Front and rear finger-lift grooves: 40.0 mm wide in X [-20, +20], 2.5 mm deep into Y = ±41.75 mm, Z in [72.0, 80.0 mm]
        fCuboid(context, id + "frontFingerGroove", {{
            "corner1" : vector(-20.00 * millimeter, -43.00 * millimeter, 72.00 * millimeter),
            "corner2" : vector(20.00 * millimeter, -39.25 * millimeter, 80.00 * millimeter)
        }});
        cutQueries = append(cutQueries, qCreatedBy(id + "frontFingerGroove", EntityType.BODY));

        fCuboid(context, id + "rearFingerGroove", {{
            "corner1" : vector(-20.00 * millimeter, 39.25 * millimeter, 72.00 * millimeter),
            "corner2" : vector(20.00 * millimeter, 43.00 * millimeter, 80.00 * millimeter)
        }});
        cutQueries = append(cutQueries, qCreatedBy(id + "rearFingerGroove", EntityType.BODY));

        opBoolean(context, id + "subtractTopPockets", {{
            "tools" : qUnion(cutQueries),
            "targets" : qCreatedBy(id + "topBinBody", EntityType.BODY),
            "operationType" : BooleanOperationType.SUBTRACTION
        }});

        setProperty(context, {{
            "entities" : qCreatedBy(id, EntityType.BODY),
            "propertyType" : PropertyType.NAME,
            "value" : "Top Bin"
        }});
        setProperty(context, {{
            "entities" : qCreatedBy(id, EntityType.BODY),
            "propertyType" : PropertyType.APPEARANCE,
            "value" : color(0.24, 0.60, 0.44)
        }});
    }});
"""
