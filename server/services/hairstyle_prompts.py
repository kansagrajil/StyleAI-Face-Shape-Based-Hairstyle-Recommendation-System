"""
Hairstyle Prompt Engineering Service.
Builds tailored, photorealistic single-image hairstyle editing prompts for each hairstyle
using its title, description, category, tags, hair length, hair types, and face shape.
Crafted specifically for single-image Image-to-Image editing (where ONLY the uploaded
portrait of the person is submitted to the AI model).
"""

import re
from typing import Any, Dict, Optional

# Pre-crafted specialized hairstyle styling profiles for catalog styles
STYLE_PROFILES: Dict[str, Dict[str, str]] = {
    "lob with face framing": {
        "cut_details": (
            "a collarbone-skimming long bob (lob) haircut with graduated, face-framing front layers "
            "that hit softly just below the chin line, creating vertical elongation"
        ),
        "styling_finish": (
            "smooth, natural inward-bending ends curving subtly around the jawline, a natural part, "
            "medium bounce, and healthy salon shine"
        )
    },
    "soft waves with side part": {
        "cut_details": (
            "medium-length cascading hair styled with an elegant deep side part, flowing into gentle, "
            "brushed-out touchable S-waves"
        ),
        "styling_finish": (
            "soft feminine movement, subtle root lift, and flowing waves that soften the angles of the jawline"
        )
    },
    "layered shag": {
        "cut_details": (
            "a modern layered shag haircut with lots of piecey, choppy layers throughout the crown and sides, "
            "paired with feathered edges and soft curtain bangs"
        ),
        "styling_finish": (
            "lived-in tousled texture, airy dimensional volume on top, and effortless modern separation"
        )
    },
    "classic bob": {
        "cut_details": (
            "a timeless, symmetrical chin-length classic bob with crisp, softly beveled ends "
            "curving gently inward toward the neck"
        ),
        "styling_finish": (
            "sleek, polished straight hair with a crisp parting, zero flyaways, and a smooth glossy finish"
        )
    },
    "textured pixie cut": {
        "cut_details": (
            "a bold, short cropped pixie cut with closely tapered sides and nape, and longer piecey layers on top"
        ),
        "styling_finish": (
            "textured, modern separation with natural lift at the crown, highlighting facial symmetry"
        )
    },
    "long side-swept layers": {
        "cut_details": (
            "long flowing hair with cascading graduated layers and a deep side-swept front section"
        ),
        "styling_finish": (
            "smooth, bouncy volume with diagonal movement that elongates and frames the face"
        )
    },
    "chin-length bob": {
        "cut_details": (
            "a chic, structured bob cut ending precisely at the chin line with slight under-beveling"
        ),
        "styling_finish": (
            "polished blowout with lateral fullness at the jawline and radiant hair gloss"
        )
    },
    "side-swept bangs": {
        "cut_details": (
            "medium-length hair paired with soft, wispy diagonal side-swept bangs gently crossing the forehead"
        ),
        "styling_finish": (
            "delicate feathered fringe blending seamlessly into soft side layers with light natural movement"
        )
    },
    "voluminous curls": {
        "cut_details": (
            "medium-to-long cascading voluminous curls with rounded shape, full body, and tapered ends"
        ),
        "styling_finish": (
            "springy, defined, frizz-free spiral curls with rich dimension and natural luster"
        )
    },
    "chin-length textured cut": {
        "cut_details": (
            "a contemporary textured cut ending at the chin with razored, piecey ends"
        ),
        "styling_finish": (
            "airy, slightly tousled texture with subtle waves providing flattering width at the jaw"
        )
    },
    "classic taper fade": {
        "cut_details": (
            "a crisp masculine taper fade with cleanly blended sides fading down to the neckline and ears, "
            "with neat length left on top"
        ),
        "styling_finish": (
            "barber-fresh styling with natural hair flow, clean temple lines, and sharp edges"
        )
    },
    "textured quiff": {
        "cut_details": (
            "a modern quiff haircut featuring short tapered sides and high-volume, textured hair on top "
            "swept upward and back"
        ),
        "styling_finish": (
            "matte textured volume with distinct strand separation, structural lift, and stylish hold"
        )
    },
    "side part pompadour": {
        "cut_details": (
            "a polished classic pompadour with a sharp side part, lifted high at the front and rolled smoothly back"
        ),
        "styling_finish": (
            "high-shine, neatly combed pomade finish with structured height and clean lines"
        )
    },
    "buzz cut": {
        "cut_details": (
            "an ultra-clean, uniform short buzz cut with clean-cut temple lines and a crisp natural hairline"
        ),
        "styling_finish": (
            "even, neat stubble-length hair showing clear scalp contours and sharp masculine precision"
        )
    },
    "medium curly top": {
        "cut_details": (
            "tapered shorter sides and back with a crown of natural, springy, medium-length curls on top"
        ),
        "styling_finish": (
            "hydrated, defined curl clumps with natural bounce, volume, and organic texture"
        )
    },
    "curtain bangs": {
        "cut_details": (
            "medium-to-long hair featuring center-parted, cheekbone-skimming curtain bangs that curve gently outward"
        ),
        "styling_finish": (
            "soft blowout volume with outward-flicked fringe and seamless blending into cascading lengths"
        )
    },
    "french bob": {
        "cut_details": (
            "a Parisian short cropped bob hitting near the cheekbone/lip line, paired with soft brow-skimming fringe"
        ),
        "styling_finish": (
            "effortless, slightly lived-in texture with subtle movement and Parisian chic elegance"
        )
    },
    "sleek high ponytail": {
        "cut_details": (
            "hair gathered smoothly into a high ponytail anchored securely at the crown"
        ),
        "styling_finish": (
            "ultra-smooth flyaway-free hair brushed back from the forehead with a straight, glossy tail"
        )
    },
    "beach waves": {
        "cut_details": (
            "shoulder-length or long hair cut with long subtle layers and piecey ends"
        ),
        "styling_finish": (
            "relaxed, sun-kissed bohemian beach waves with natural texture, subtle bends, and matte shine"
        )
    }
}


def _normalize_name(name: str) -> str:
    """Normalize a hairstyle name for key matching."""
    return re.sub(r'[^a-z0-9]+', ' ', (name or '').lower()).strip()


def build_hairstyle_prompt(hairstyle_doc: Any, face_shape: str = "") -> Dict[str, str]:
    """
    Build an explicit, photorealistic single-image hairstyle editing prompt for a given hairstyle.

    Args:
        hairstyle_doc: Dict or object containing hairstyle attributes (name, description,
                       hair_length, category, tags, hair_types).
        face_shape: Detected face shape (e.g. 'oval', 'round', 'square').

    Returns:
        dict: {'positive_prompt': str, 'negative_prompt': str}
    """
    if not isinstance(hairstyle_doc, dict):
        hs_name = str(getattr(hairstyle_doc, 'name', 'Hairstyle') or 'Hairstyle')
        hs_desc = str(getattr(hairstyle_doc, 'description', '') or '')
        length = str(getattr(hairstyle_doc, 'hair_length', 'medium') or 'medium')
        category = str(getattr(hairstyle_doc, 'category', 'modern') or 'modern')
        tags = getattr(hairstyle_doc, 'tags', [])
    else:
        hs_name = str(hairstyle_doc.get('name') or 'Hairstyle').strip()
        hs_desc = str(hairstyle_doc.get('description') or '').strip()
        length = str(hairstyle_doc.get('hair_length') or 'medium').strip()
        category = str(hairstyle_doc.get('category') or 'modern').strip()
        tags = hairstyle_doc.get('tags', [])

    if isinstance(tags, list):
        tags_str = ", ".join([str(t).strip() for t in tags if t])
    else:
        tags_str = str(tags or '')

    # Find matching profile by exact or fuzzy name match
    norm_name = _normalize_name(hs_name)
    matched_profile = None

    if norm_name in STYLE_PROFILES:
        matched_profile = STYLE_PROFILES[norm_name]
    else:
        for key, prof in STYLE_PROFILES.items():
            if key in norm_name or norm_name in key:
                matched_profile = prof
                break

    if matched_profile:
        cut_description = matched_profile["cut_details"]
        styling_finish = matched_profile["styling_finish"]
    else:
        # Dynamic fallback from document metadata
        cut_description = f"a {length}-length {category} haircut ({hs_name})"
        if hs_desc:
            cut_description += f": {hs_desc}"
        styling_finish = f"styled with {tags_str or 'natural movement and clean separation'}"

    # Face shape compatibility clause
    face_flatter = ""
    if face_shape and str(face_shape).lower() not in ("unknown", "none", ""):
        face_flatter = f" Designed to complement and flatter a {face_shape} face shape."

    positive_prompt = (
        f"Transform the hairstyle of the person in the photo into a photorealistic {hs_name}. "
        f"The new haircut is {cut_description}. "
        f"Finish: {styling_finish}.{face_flatter} "
        f"CRITICAL REQUIREMENTS: "
        f"1. Keep the exact same person, face, facial structure, skin tone, eyes, eyebrows, nose, mouth, lips, facial expression, age, head angle, clothing, lighting, and background 100% unchanged. "
        f"2. Modify ONLY the hair on top and around the head to realistically match the {hs_name} hairstyle. "
        f"3. Ensure the hairline blends seamlessly and naturally with the forehead and temples with realistic individual hair strands and natural hair volume."
    )

    negative_prompt = (
        "distorted face, changed facial features, altered identity, different person, modified eyes, altered nose, altered mouth, "
        "unnatural hairline, changed skin tone, blurry, cartoon, 3D render, bad anatomy, deformed eyes, extra face, low resolution, "
        "wig-like, plastic hair, disfigured, double head, artifacts"
    )

    return {
        "positive_prompt": positive_prompt,
        "negative_prompt": negative_prompt
    }
