import os
import tempfile
from pathlib import Path

from jinja2 import Template
from playwright.async_api import async_playwright


# Paths 
BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATE_PATH = (
    BASE_DIR
    / "templates"
    / "resume.html"
)


# Template
def load_resume_template() -> str:
    """
    Load the resume HTML template.
    """

    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(
            f"Resume template not found: {TEMPLATE_PATH}"
        )

    with open(
        TEMPLATE_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        template_content = file.read()

    if not template_content.strip():
        raise ValueError(
            "resume.html is empty."
        )

    return template_content


def render_resume_html(
    resume_data: dict,
) -> str:
    """
    Render resume.html using generated resume data.
    """

    template_content = load_resume_template()

    template = Template(
        template_content
    )

    html_content = template.render(
        **resume_data
    )

    if not html_content.strip():
        raise ValueError(
            "Rendered resume HTML is empty."
        )

    return html_content


# PDF Generation
async def generate_pdf(
    html_content: str,
    output_filename: str | None = None,
) -> str:
    """
    Generate a one-page PDF from rendered HTML.

    The resume template is preserved.
    The renderer dynamically scales the page only
    when necessary to prevent a second page.
    """

    if not html_content.strip():
        raise ValueError(
            "Cannot generate PDF because HTML is empty."
        )

    if output_filename is None:
        output_filename = (
            "tailored_resume.pdf"
        )

    output_path = os.path.join(
        tempfile.gettempdir(),
        output_filename,
    )

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page(
            viewport={
                "width": 816,
                "height": 1056,
            }
        )

        await page.set_content(
            html_content,
            wait_until="load",
        )

        await page.emulate_media(
            media="print"
        )

        await page.wait_for_timeout(
            300
        )

        # Check Body
        body_text = await page.locator(
            "body"
        ).inner_text()

        if not body_text.strip():
            await browser.close()

            raise ValueError(
                "Rendered resume HTML contains no visible text."
            )

         # One-page fitting
        fit_script = """
        () => {
            const body = document.body;
            const html = document.documentElement;

            const availableHeight =
                11 * 96 - (0.8 * 96);

            const contentHeight = Math.max(
                body.scrollHeight,
                body.offsetHeight,
                html.scrollHeight
            );

            return {
                contentHeight,
                availableHeight
            };
        }
        """

        dimensions = await page.evaluate(
            fit_script
        )

        content_height = dimensions[
            "contentHeight"
        ]

        available_height = dimensions[
            "availableHeight"
        ]

        # print(
        #     f"[PDF] Content height: "
        #     f"{content_height}px"
        # )

        # print(
        #     f"[PDF] Available height: "
        #     f"{available_height}px"
        # )

         # Dynamic scaling
        if content_height > available_height:

            required_scale = (
                available_height
                / content_height
            )

            # Never shrink below 85%.
            scale = max(
                required_scale,
                0.85,
            )

            # print(
            #     f"[PDF] Resume exceeds one page."
            # )

            # print(
            #     f"[PDF] Applying scale: "
            #     f"{scale:.3f}"
            # )

            await page.add_style_tag(
                content=f"""
                body {{
                    zoom: {scale};
                }}
                """
            )

            await page.wait_for_timeout(
                200
            )

        else:
            pass 

            # print(
            #     "[PDF] Resume already fits "
            #     "within one page."
            # )

         # Final page count check
 
        final_dimensions = await page.evaluate(
            fit_script
        )

        final_height = final_dimensions[
            "contentHeight"
        ]

        # print(
        #     f"[PDF] Final content height: "
        #     f"{final_height}px"
        # )

      
        # Generate PDF
        await page.pdf(
            path=output_path,
            format="Letter",
            margin={
                "top": "0.4in",
                "bottom": "0.4in",
                "left": "0.4in",
                "right": "0.4in",
            },
            print_background=True,
            prefer_css_page_size=True,
        )

        await browser.close()

    
    # Verify File
    if not os.path.exists(output_path):
        raise FileNotFoundError(
            f"PDF was not created: {output_path}"
        )

    file_size = os.path.getsize(
        output_path
    )

    # print(
    #     f"[PDF] Generated PDF size: "
    #     f"{file_size} bytes"
    # )

    if file_size == 0:
        raise ValueError(
            "Generated PDF is empty."
        )

    return output_path