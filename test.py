from paddleocr import PaddleOCR

ocr = PaddleOCR(
    use_angle_cls=True,
    lang="en"
)

result = ocr.ocr("sample.png.jpeg")


for page in result:
    for line in page:
        print(line[1][0])