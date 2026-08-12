import fitz  # PyMuPDF
from typing import Any



# Rectangle Utilities

def _intersection_area(
    rect1: fitz.Rect,
    rect2: fitz.Rect,
) -> float:
    """
    Return the intersection area between two rectangles.
    """

    intersection = rect1 & rect2

    if intersection.is_empty:
        return 0.0

    return intersection.get_area()


def _word_inside_link(
    word_rect: fitz.Rect,
    link_rect: fitz.Rect,
    min_overlap: float = 0.5,
) -> bool:
    """
    Check whether a PDF text word actually belongs
    to a hyperlink annotation.

    This uses rectangle overlap rather than nearby-text
    matching.

    Args:
        word_rect:
            Bounding rectangle of the PDF word.

        link_rect:
            Bounding rectangle of the hyperlink.

        min_overlap:
            Minimum percentage of the word's area that
            must overlap the hyperlink rectangle.

    Returns:
        True if the word belongs to the hyperlink.
    """

    word_area = word_rect.get_area()

    if word_area <= 0:
        return False

    overlap_area = _intersection_area(
        word_rect,
        link_rect,
    )

    overlap_ratio = (
        overlap_area / word_area
    )

    return overlap_ratio >= min_overlap


# Resume Text Extraction

def extract_text(
    file_path: str,
) -> str:
    """
    Extract all text from a PDF resume.

    Args:
        file_path:
            Path to the resume PDF.

    Returns:
        Extracted resume text as a single string.
    """

    doc = fitz.open(
        file_path
    )

    try:

        text = " ".join(
            page.get_text()
            for page in doc
        )

        return text

    finally:

        doc.close()


# Text ↔ Hyperlink Mapping
 
def extract_text_link_mappings(
    file_path: str,
) -> list[dict[str, Any]]:
    """
    Map the exact visible text covered by each
    PDF hyperlink annotation to its destination URL.

    Example:

        GitHub
            ↓
        https://github.com/prince0310

    The function does NOT search for nearby text.

    It only considers text whose bounding box overlaps
    the hyperlink annotation rectangle.

    Returns:

        [
            {
                "text": "GitHub",
                "url": "https://github.com/prince0310",
                "page": 1,
                "rect": {
                    "x0": 500.0,
                    "y0": 30.0,
                    "x1": 550.0,
                    "y1": 42.0
                }
            }
        ]
    """

    results: list[dict[str, Any]] = []

    doc = fitz.open(
        file_path
    )

    try:

        for page_number, page in enumerate(
            doc,
            start=1,
        ):

             # Extract words with coordinates
 
            words = page.get_text(
                "words"
            )

             # Extract hyperlink annotations
 
            for link in page.get_links():

                uri = link.get(
                    "uri"
                )

                if not uri:
                    continue

                link_from = link.get(
                    "from"
                )

                if not link_from:
                    continue

                link_rect = fitz.Rect(
                    link_from
                )

                matched_words = []

                 # Find words INSIDE hyperlink rectangle
 
                for word in words:

                    word_rect = fitz.Rect(
                        word[0],
                        word[1],
                        word[2],
                        word[3],
                    )

                    if _word_inside_link(
                        word_rect,
                        link_rect,
                    ):
                        matched_words.append(
                            word
                        )

                # --------------------------------------
                # Sort words in reading order
                # --------------------------------------

                matched_words.sort(
                    key=lambda word: (
                        word[1],  # y position
                        word[0],  # x position
                    )
                )

                # --------------------------------------
                # Build visible hyperlink text
                # --------------------------------------

                visible_text = " ".join(
                    word[4]
                    for word in matched_words
                ).strip()

                # --------------------------------------
                # Store mapping
                # --------------------------------------

                results.append(
                    {
                        "text": visible_text,
                        "url": uri.strip(),
                        "page": page_number,
                        "rect": {
                            "x0": link_rect.x0,
                            "y0": link_rect.y0,
                            "x1": link_rect.x1,
                            "y1": link_rect.y1,
                        },
                    }
                )

    finally:

        doc.close()

    return results


# ==========================================
# Normalize Displayed Link Text
# ==========================================

def _normalize_link_text(
    text: str,
) -> str:
    """
    Normalize the visible text of a hyperlink.

    Examples:

        "GitHub:"        -> "github"
        " GitHub "       -> "github"
        "LinkedIn |"     -> "linkedin"
    """

    normalized = (
        text
        .strip()
        .lower()
    )

    normalized = (
        normalized
        .replace(":", "")
        .replace("|", "")
        .strip()
    )

    return normalized


# ==========================================
# Contact Link Extraction
# ==========================================

def extract_contact_links(
    file_path: str,
) -> dict[str, str]:
    """
    Identify GitHub, LinkedIn and Portfolio links
    using the ACTUAL DISPLAYED TEXT of the hyperlink.

    Important:

    We do NOT infer portfolio from an unknown URL.

    We do NOT use nearby text.

    We do NOT use URL domains to identify portfolio.

    Only the text actually covered by the hyperlink
    annotation is used for classification.

    Returns:

        {
            "github": "...",
            "linkedin": "...",
            "portfolio": "..."
        }
    """

    result = {
        "github": "",
        "linkedin": "",
        "portfolio": "",
    }

    mappings = extract_text_link_mappings(
        file_path
    )

    for mapping in mappings:

        text = _normalize_link_text(
            mapping["text"]
        )

        url = (
            mapping["url"]
            .strip()
        )

        if not url:
            continue

        # ==========================================
        # GitHub
        # ==========================================

        if text in {
            "github",
            "github profile",
            "github.com",
        }:

            if not result["github"]:

                result["github"] = url

            continue

        # ==========================================
        # LinkedIn
        # ==========================================

        if text in {
            "linkedin",
            "linkedin profile",
            "linkedin.com",
        }:

            if not result["linkedin"]:

                result["linkedin"] = url

            continue

        # ==========================================
        # Portfolio
        # ==========================================

        if text in {
            "portfolio",
            "portfolio website",
            "personal website",
            "personal site",
        }:

            if not result["portfolio"]:

                result["portfolio"] = url

            continue

        # ==========================================
        # Unknown Link
        # ==========================================

        # IMPORTANT:
        #
        # Unknown links are intentionally ignored.
        #
        # We DO NOT assume:
        #
        # unknown URL -> portfolio
        #
        # This prevents incorrect mappings such as:
        #
        # mailto:... -> portfolio
        #
        # or any unrelated website -> portfolio.

    return result


# ==========================================
# Backward-Compatible Function
# ==========================================

def extract_urls(
    file_path: str,
) -> dict[str, str]:
    """
    Backward-compatible wrapper used by the existing
    resume generation pipeline.
    """

    return extract_contact_links(
        file_path
    )


# Debug / Standalone Test

# if __name__ == "__main__":

#     import json
#     import sys

#     if len(sys.argv) != 2:

#         print(
#             "Usage:"
#         )

#         print(
#             "python extraction_service.py "
#             "<resume.pdf>"
#         )

#         raise SystemExit(1)

#     pdf_path = sys.argv[1]

#     # ------------------------------------------
#     # Raw mappings
#     # ------------------------------------------

#     print(
#         "\n========== TEXT ↔ LINK MAPPINGS ==========\n"
#     )

#     mappings = extract_text_link_mappings(
#         pdf_path
#     )

#     print(
#         json.dumps(
#             mappings,
#             indent=2,
#             ensure_ascii=False,
#         )
#     )

#     # ------------------------------------------
#     # Contact mappings
#     # ------------------------------------------

#     print(
#         "\n========== CONTACT LINKS ==========\n"
#     )

#     contact_links = extract_contact_links(
#         pdf_path
#     )

#     print(
#         json.dumps(
#             contact_links,
#             indent=2,
#             ensure_ascii=False,
#         )
#     )