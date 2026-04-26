# Image Extraction Configuration

GraphFusion AI supports two modes for extracting knowledge from embedded images (diagrams, charts, flowcharts):

## Modes

### OCR Mode (Default)
Uses pytesseract for optical character recognition. Best for:
- Screenshots with text
- Scanned documents
- Cost-sensitive deployments
- Low-latency requirements

```env
IMAGE_EXTRACTION_MODE=ocr
```

**Dependencies:** `pytesseract`, `tesseract-ocr` (system package)

### VLM Mode (Vision Language Model)
Uses Azure OpenAI GPT-4o vision for structured entity/relationship extraction. Best for:
- Architecture diagrams
- Flowcharts and process diagrams
- Organizational charts
- Technical diagrams with visual relationships

```env
IMAGE_EXTRACTION_MODE=vlm
AZURE_OPENAI_VISION_MODEL=gpt-4o
```

**Dependencies:** `openai` (already included), Azure OpenAI with vision model access

## Configuration

Edit `.env`:

```env
# Choose extraction mode
IMAGE_EXTRACTION_MODE=ocr          # or "vlm"

# VLM settings (only if mode=vlm)
AZURE_OPENAI_VISION_MODEL=gpt-4o
```

## What Gets Extracted

### OCR Mode
```
Raw text from image:
"System Architecture
  Component A → Component B
  Database Layer"
```

### VLM Mode
```
Structured knowledge:
Entity: Component A (System Component) - Main processing unit
Entity: Component B (System Component) - Secondary processor  
Relationship: Component A --[SENDS_DATA_TO]--> Component B
Entity: Database Layer (Infrastructure) - Data storage
```

## Cost Comparison

| Mode | Cost per Image | Latency | Accuracy on Diagrams |
|------|---------------|---------|---------------------|
| OCR  | ~$0           | <1s     | Text only           |
| VLM  | ~$0.01-0.03   | 3-10s   | High (structure + relationships) |

## Installation

### OCR Mode
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Python package (already in requirements.txt)
pip install pytesseract
```

### VLM Mode
No additional installation. Ensure your Azure OpenAI deployment has:
- GPT-4o or other vision-capable model
- API access enabled

## Fallback Behavior

If VLM extraction fails (API error, JSON parse error), the pipeline automatically falls back to OCR.

## Example Pipeline Output

```
[LlamaIndex] Parsed 'architecture.pdf' (pdf, 3 images)
[LlamaIndex] VLM extracted 12 entities, 8 relationships from /tmp/arch_img0.png
[LlamaIndex] Appended VLM text from 3 images to document
[LlamaIndex] Stored 45 chunks in OpenSearch index 'graphfusion_chunks'
[LlamaIndex] Stored 156 entities, 89 relationships in Neo4j
```
