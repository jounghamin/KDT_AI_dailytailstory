from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from rembg import remove
from PIL import Image
from PIL import ImageEnhance
from io import BytesIO
import base64
import tempfile
import os
from .models import FairyTale 
from django.views.decorators.http import require_POST, require_GET

# Create your views here.
def index(request):
    next_page = request.POST.get('next_page', '/default/')
    # 사용자 이름을 템플릿 컨텍스트에 추가합니다.
    context = {
        'username': request.user.username if request.user.is_authenticated else None,
        'next_page': next_page,
    }
    return render(request,'ft/image.html', context)

def capture_image(request):
    if request.method == 'POST':
        next_page =  request.POST.get('next_page', '/default/')
        
        # next_page = request.POST.get('next_page', '/default/')
        # 캡처한 이미지 받아오기
        image_data = request.POST['image']
        # 이미지를 파일로 저장
        image_data = base64.b64decode(image_data.split(',')[1])

        # 이미지를 원하는 비율로 자르기
        input_image = Image.open(BytesIO(image_data))
        width, height = input_image.size
        # 이미지의 가로 길이의 절반만큼 자르도록 설정 (세로 길이는 그대로 유지)
        output_image = input_image.crop((0, 0, width // 2, height))
        
        # 배경 제거
        output_image = remove(input_image, alpha_matting=True)
        
        # 이미지 품질 조정 (옵션으로 조절 가능)
        enhancer = ImageEnhance.Sharpness(output_image)
        output_image = enhancer.enhance(2.0)

        # 배경이 제거된 이미지를 저장할 폴더 경로
        output_image_dir = r'C:\Users\user\Desktop\project\project1\static\img'
        # 저장할 이미지 파일의 이름
        output_image_filename = 'removed_bg_image.png'
        # 저장할 이미지 파일의 전체 경로
        output_image_path = os.path.join(output_image_dir, output_image_filename)

        # 폴더가 없으면 생성
        os.makedirs(output_image_dir, exist_ok=True)

        # 배경이 제거된 이미지를 저장
        output_image.save(output_image_path)

        # 이미지를 이진 데이터로 변환
        with BytesIO() as output_buffer:
            output_image.save(output_buffer, format="PNG")
            image_binary = output_buffer.getvalue()
        
        base64_image = base64.b64encode(image_binary).decode('utf-8')

        # 클라이언트에게 전달할 이미지 경로
        image_url = '/static/img/' + output_image_filename

        # 임시 파일로 배경이 제거된 이미지 저장
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            output_image.save(temp_file)

        # HTML 페이지에 이미지 경로 전달
        return JsonResponse({'message': 'Image captured and background removed successfully.', 'image_url': image_url, 'image_data': base64_image, 'next_page': next_page})
    else:
        return JsonResponse({'error': 'Invalid request method or image data missing.'}, status=400)

def save_image(request):
    if request.method == 'POST' and 'image_data' in request.POST:
        image_data = request.POST.get('image_data')
        next_page = request.POST.get('next_page')

        if image_data:
            image_binary = base64.b64decode(image_data.split(',')[1])

            # 이미지 데이터를 BinaryField에 저장
            fairy_tale = FairyTale.objects.create(
                title='성냥팔이소녀',
                image=image_binary,  # 이미지 데이터를 BinaryField에 직접 저장
                user=request.user if request.user.is_authenticated else None
            )
            context = {'next_page': next_page}
            redirect_url = next_page

            return redirect(redirect_url)
        
        return JsonResponse({'error': 'Image data missing.'}, status=400)
    
    else:
        output_image_filename = 'removed_bg_image.png'
        image_url = 'static/img/' + output_image_filename

        next_page = request.GET.get('next_page')

        with open(image_url, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
        context = {'encoded_string': encoded_string, 'next_page': next_page}
        # return JsonResponse({'encoded_string': encoded_string, 'next_page': next_page} )
        return render(request, 'ft/save.html', context)
