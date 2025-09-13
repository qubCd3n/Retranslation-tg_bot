import os
import io
from PIL import Image, ExifTags
from exifread import process_file
import logging

logger = logging.getLogger(__name__)

class MetadataCleaner:
    """Класс для очистки метаданных из медиафайлов"""
    
    @staticmethod
    def clean_image_metadata(image_path: str, output_path: str = None) -> str:
        """
        Очищает EXIF данные из изображения
        
        Args:
            image_path: Путь к исходному изображению
            output_path: Путь для сохранения очищенного изображения
            
        Returns:
            Путь к очищенному файлу
        """
        if output_path is None:
            output_path = image_path
        
        try:
            with Image.open(image_path) as img:
                # Создаем новое изображение без EXIF данных
                data = list(img.getdata())
                image_without_exif = Image.new(img.mode, img.size)
                image_without_exif.putdata(data)
                
                # Сохраняем без EXIF
                image_without_exif.save(output_path, format=img.format, quality=95)
                
            logger.info(f"Metadata cleaned from image: {image_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error cleaning metadata from {image_path}: {e}")
            return image_path
    
    @staticmethod
    def has_exif_data(file_path: str) -> bool:
        """
        Проверяет наличие EXIF данных в файле
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            True если есть EXIF данные, False иначе
        """
        try:
            with open(file_path, 'rb') as f:
                tags = process_file(f, details=False)
                return len(tags) > 0
        except Exception as e:
            logger.error(f"Error checking EXIF data in {file_path}: {e}")
            return False
    
    @staticmethod
    def clean_file_metadata(file_path: str, output_path: str = None) -> str:
        """
        Очищает метаданные из файла (универсальный метод)
        
        Args:
            file_path: Путь к исходному файлу
            output_path: Путь для сохранения очищенного файла
            
        Returns:
            Путь к очищенному файлу
        """
        if output_path is None:
            output_path = file_path
        
        # Проверяем тип файла
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
            return MetadataCleaner.clean_image_metadata(file_path, output_path)
        else:
            # Для других типов файлов просто копируем
            try:
                with open(file_path, 'rb') as src, open(output_path, 'wb') as dst:
                    dst.write(src.read())
                logger.info(f"File copied without metadata cleaning: {file_path}")
                return output_path
            except Exception as e:
                logger.error(f"Error copying file {file_path}: {e}")
                return file_path
