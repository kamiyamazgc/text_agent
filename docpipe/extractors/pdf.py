from pathlib import Path
from typing import Any, Dict
import subprocess
import tempfile
import os
import shutil

try:
    import pypdfium2  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pypdfium2 = None  # type: ignore

try:
    import marker  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    marker = None  # type: ignore

from .base import BaseExtractor


class PDFExtractor(BaseExtractor):
    """Extractor for digital PDFs using marker with pypdfium2 fallback."""

    def can_handle(self, source: str) -> bool:
        """Check if the source is a PDF file"""
        return source.lower().endswith(".pdf")

    def extract(self, source: str, **kwargs: Any) -> Dict[str, Any]:
        """Extract text from a digital PDF with optional layout information."""
        pdf_path = Path(source)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {source}")

        # Try marker first
        try:
            # Create temporary directory for marker output
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir_path = Path(temp_dir)
                
                # Create a subdirectory for the PDF (marker expects a folder)
                pdf_folder = temp_dir_path / "pdf_input"
                pdf_folder.mkdir()
                
                # Copy PDF to the input folder
                shutil.copy2(pdf_path, pdf_folder / pdf_path.name)
                
                print(f"DEBUG: Created marker input folder: {pdf_folder}")
                print(f"DEBUG: Copied PDF: {pdf_folder / pdf_path.name}")
                
                # Run marker command
                cmd = [
                    "marker",
                    str(pdf_folder),
                    "--max_files", "1",
                    "--output_dir", str(temp_dir_path)
                ]
                
                print(f"DEBUG: Running marker command: {' '.join(cmd)}")
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minutes timeout
                    cwd=str(temp_dir_path)  # Set working directory to temp directory
                )
                
                print(f"DEBUG: Marker return code: {result.returncode}")
                print(f"DEBUG: Marker stdout: {result.stdout[:500]}...")
                print(f"DEBUG: Marker stderr: {result.stderr[:500]}...")
                
                if result.returncode == 0:
                    # List all files in temp directory
                    print(f"DEBUG: All files in temp directory:")
                    for file_path in temp_dir_path.rglob('*'):
                        print(f"DEBUG:   {file_path.relative_to(temp_dir_path)}")
                    
                    # Find the generated markdown file
                    md_files = list(temp_dir_path.glob("**/*.md"))
                    print(f"DEBUG: Found {len(md_files)} markdown files: {[f.name for f in md_files]}")
                    
                    if md_files:
                        with open(md_files[0], 'r', encoding='utf-8') as f:
                            text = f.read()
                        
                        print(f"DEBUG: Successfully read markdown file: {md_files[0]}")
                        print(f"DEBUG: Text length: {len(text)}")
                        
                        metadata = {
                            "source_type": "pdf",
                            "file_name": pdf_path.name,
                            "extractor": "marker",
                        }
                        return {"text": text, "metadata": metadata}
                    else:
                        print("Marker succeeded but no markdown file found")
                        
                        # Try to find files in the default marker output directory
                        marker_output_dir = Path("/Users/desesseintes/Downloads/VSCode/text_agent/venv311_py311/lib/python3.11/site-packages/conversion_results")
                        if marker_output_dir.exists():
                            print(f"DEBUG: Checking marker default output directory: {marker_output_dir}")
                            marker_md_files = list(marker_output_dir.glob("**/*.md"))
                            print(f"DEBUG: Found {len(marker_md_files)} markdown files in default directory: {[f.name for f in marker_md_files]}")
                            
                            # Look for a file that matches our PDF name
                            pdf_name = pdf_path.stem  # Get filename without extension
                            matching_md_files = [f for f in marker_md_files if pdf_name in f.name or f.parent.name == pdf_name]
                            
                            if matching_md_files:
                                # Use the matching file
                                md_file = matching_md_files[0]
                                with open(md_file, 'r', encoding='utf-8') as f:
                                    text = f.read()
                                
                                print(f"DEBUG: Successfully read matching markdown file: {md_file}")
                                print(f"DEBUG: Text length: {len(text)}")
                                
                                # Find and copy image files
                                pdf_output_dir = md_file.parent
                                if pdf_output_dir.exists():
                                    print(f"DEBUG: Found PDF output directory: {pdf_output_dir}")
                                    
                                    # Find image files
                                    image_files = list(pdf_output_dir.glob("*.jpeg")) + list(pdf_output_dir.glob("*.jpg")) + list(pdf_output_dir.glob("*.png"))
                                    print(f"DEBUG: Found {len(image_files)} image files: {[f.name for f in image_files]}")
                                    
                                    # Return image files info for copying
                                    metadata = {
                                        "source_type": "pdf",
                                        "file_name": pdf_path.name,
                                        "extractor": "marker",
                                        "marker_output_dir": str(pdf_output_dir),
                                        "image_files": [str(f) for f in image_files],
                                    }
                                else:
                                    metadata = {
                                        "source_type": "pdf",
                                        "file_name": pdf_path.name,
                                        "extractor": "marker",
                                    }
                                
                                return {"text": text, "metadata": metadata}
                            elif marker_md_files:
                                # If no matching file found, use the first available file but warn
                                print(f"WARNING: No matching file found for {pdf_name}, using first available file: {marker_md_files[0].name}")
                                with open(marker_md_files[0], 'r', encoding='utf-8') as f:
                                    text = f.read()
                                
                                print(f"DEBUG: Successfully read markdown file from default directory: {marker_md_files[0]}")
                                print(f"DEBUG: Text length: {len(text)}")
                                
                                # Find and copy image files
                                pdf_name = pdf_path.stem  # Get filename without extension
                                pdf_output_dir = marker_output_dir / pdf_name
                                if pdf_output_dir.exists():
                                    print(f"DEBUG: Found PDF output directory: {pdf_output_dir}")
                                    
                                    # Find image files
                                    image_files = list(pdf_output_dir.glob("*.jpeg")) + list(pdf_output_dir.glob("*.jpg")) + list(pdf_output_dir.glob("*.png"))
                                    print(f"DEBUG: Found {len(image_files)} image files: {[f.name for f in image_files]}")
                                    
                                    # Return image files info for copying
                                    metadata = {
                                        "source_type": "pdf",
                                        "file_name": pdf_path.name,
                                        "extractor": "marker",
                                        "marker_output_dir": str(pdf_output_dir),
                                        "image_files": [str(f) for f in image_files],
                                    }
                                else:
                                    metadata = {
                                        "source_type": "pdf",
                                        "file_name": pdf_path.name,
                                        "extractor": "marker",
                                    }
                                
                                return {"text": text, "metadata": metadata}
                else:
                    print(f"Marker failed: {result.stderr}")
                    
        except Exception as e:
            print(f"Marker extraction failed: {e}")
            import traceback
            traceback.print_exc()

        # Fallback to pypdfium2
        if pypdfium2 is None:
            raise ImportError(
                "Neither marker nor pypdfium2 is available for PDF extraction"
            )

        try:
            # Open PDF and extract text
            pdf = pypdfium2.PdfDocument(pdf_path)
            text_parts = []
            
            # Extract text from each page
            for page_index in range(len(pdf)):
                page = pdf[page_index]
                text_page = page.get_textpage()
                text_parts.append(text_page.get_text_range())
                text_page.close()
            
            text = "\n".join(text_parts)
            pdf.close()
            
        except Exception as e:  # pragma: no cover - passthrough any extraction errors
            raise RuntimeError(f"Failed to extract PDF: {e}")

        metadata = {
            "source_type": "pdf",
            "file_name": pdf_path.name,
            "extractor": "pypdfium2",
        }
        return {"text": text, "metadata": metadata}
