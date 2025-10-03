import asyncio
from app.services.ocr_service import OCRService

async def test():
    ocr = OCRService()
    
    # Test raw extraction without parsing
    from pdf2image import convert_from_path
    import pytesseract
    
    images = convert_from_path("test_answer_sheet.pdf")
    
    for i, image in enumerate(images):
        raw_text = pytesseract.image_to_string(image)
        print(f"\n=== Page {i+1} Raw OCR Output ===")
        print(raw_text)
        print("=" * 50)
    
    # Now test with parsing
    result = await ocr.extract_answers("test_answer_sheet.pdf")
    print(f"\n=== Parsed Result ===")
    print(result)

asyncio.run(test())