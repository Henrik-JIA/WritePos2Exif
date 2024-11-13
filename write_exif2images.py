from PIL import Image
import piexif
from fractions import Fraction
import os
from PyQt5.QtWidgets import QMessageBox
from concurrent.futures import ThreadPoolExecutor

def convert_to_dms(degree_float):
    degrees = int(degree_float)
    minutes = int((degree_float - degrees) * 60)
    seconds = (degree_float - degrees - minutes/60) * 3600.00
    return degrees, minutes, seconds

def _to_rational(number):
    """Convert a number to a rational tuple (numerator, denominator)."""
    f = Fraction.from_float(number).limit_denominator(10000)  # Increased denominator limit for higher precision
    return (f.numerator, f.denominator)

def set_info(img, lat, lng, alt, settings):
    # Convert string inputs to float if they are not None
    lat = float(lat) if lat is not None else None
    lng = float(lng) if lng is not None else None
    alt = float(alt) if alt is not None else None

    exif_dict = piexif.load(img.info['exif']) if 'exif' in img.info else {'0th': {}, 'Exif': {}, 'GPS': {}, '1st': {}}

    gps_info = {}
    if lat is not None and lng is not None:
        lat_deg = convert_to_dms(lat)
        lng_deg = convert_to_dms(lng)
        gps_info.update({
            piexif.GPSIFD.GPSLatitude: tuple(map(_to_rational, lat_deg)),
            piexif.GPSIFD.GPSLongitude: tuple(map(_to_rational, lng_deg)),
            piexif.GPSIFD.GPSLatitudeRef: 'N' if lat >= 0 else 'S',
            piexif.GPSIFD.GPSLongitudeRef: 'E' if lng >= 0 else 'W',
        })

    if alt is not None:
        altitude_rational = _to_rational(alt)
        gps_info.update({
            piexif.GPSIFD.GPSAltitude: altitude_rational,
            piexif.GPSIFD.GPSAltitudeRef: 0 if alt >= 0 else 1,
        })

    if gps_info:
        exif_dict['GPS'] = gps_info

    # Process additional settings
    for key, value in settings.items():
        if value is not None:
            if key == 'camera_manufacturer':
                manufacturer_bytes = value.encode('utf-8').strip()
                exif_dict['0th'][piexif.ImageIFD.Make] = manufacturer_bytes
            elif key == "camera_model":
                model_bytes = value.encode('utf-8').strip()
                exif_dict['0th'][piexif.ImageIFD.Model] = model_bytes
            elif key == "aperture_value":
                aperture_value_rational = _to_rational(float(value))
                exif_dict['Exif'][piexif.ExifIFD.FNumber] = aperture_value_rational
            elif key == "exposure_time":
                exposure_time_rational = _to_rational(float(value))
                exif_dict['Exif'][piexif.ExifIFD.ExposureTime] = exposure_time_rational
            elif key == "iso_speed":
                iso_speed_rational = int(value)
                exif_dict['Exif'][piexif.ExifIFD.ISOSpeedRatings] = iso_speed_rational
            elif key == "exposure_compensation":
                exposure_compensation_rational = _to_rational(float(value))
                exif_dict['Exif'][piexif.ExifIFD.ExposureBiasValue] = exposure_compensation_rational
            elif key == 'focal_length':
                focal_length_rational = _to_rational(float(value))
                exif_dict['Exif'][piexif.ExifIFD.FocalLength] = focal_length_rational
            elif key == "max_aperture":
                max_aperture_rational = _to_rational(float(value))
                exif_dict['Exif'][piexif.ExifIFD.MaxApertureValue] = max_aperture_rational
            elif key == "metering_mode":
                metering_mode_rational = int(value)
                exif_dict['Exif'][piexif.ExifIFD.MeteringMode] = metering_mode_rational
            elif key == 'subject_distance':
                subject_distance_rational = _to_rational(float(value))
                exif_dict['Exif'][piexif.ExifIFD.SubjectDistance] = subject_distance_rational
            elif key == "flash_mode":
                flash_mode_rational = int(value)
                exif_dict['Exif'][piexif.ExifIFD.Flash] = flash_mode_rational
            elif key == "flash_energy":
                flash_energy_rational = _to_rational(float(value))
                exif_dict['Exif'][piexif.ExifIFD.FlashEnergy] = flash_energy_rational
            elif key == "focal_length35mm":
                focal_length35mm_rational = int(value)
                exif_dict['Exif'][piexif.ExifIFD.FocalLengthIn35mmFilm] = focal_length35mm_rational
            # Add more settings processing here as needed

    # Convert EXIF dictionary to bytes
    exif_bytes = piexif.dump(exif_dict)

    # Return the modified EXIF data
    return exif_bytes

# #一张一张处理：
# def write_exif_to_images(output_folder, matched_info, focal_length, success_count ,fail_count ,progress_dialog ,parent_widget):
#     for index, (image_path, data) in enumerate(matched_info):
#         if progress_dialog.wasCanceled():
#             break
#         try:
#             with Image.open(image_path) as img:
#                 exif_bytes = set_gps_info(img, data['纬度'], data['经度'], data['高度'])
#                 # 保存图片时指定质量为最高
#                 img.save(os.path.join(output_folder, os.path.basename(image_path)), quality=95, exif=exif_bytes)
#                 success_count += 1
#         except Exception as e:
#             print(f"Error processing {image_path}: {e}")
#             fail_count += 1

#         progress_dialog.setValue(success_count + fail_count)  # Update the progress dialog here
        
#     if fail_count == 0:
#         QMessageBox.information(parent_widget, "处理完成", f"所有图片处理成功，共处理{success_count}张图片。", QMessageBox.Ok)
#     else:
#         QMessageBox.warning(parent_widget, "处理完成", f"图片处理完成，成功{success_count}张，失败{fail_count}张。", QMessageBox.Ok)

#多张同事处理
def process_image(image_path, data, settings, output_folder):
    try:
        with Image.open(image_path) as img:
            # Check if latitude, longitude, and altitude are provided
            lat = data.get('纬度')
            lng = data.get('经度')
            alt = data.get('高度')
            exif_bytes = set_info(img, lat, lng, alt, settings)
            img.save(os.path.join(output_folder, os.path.basename(image_path)), quality=settings['save_quality'], exif=exif_bytes)
            return image_path, None
    except Exception as e:
        return image_path, e

def write_exif_to_images(output_folder, matched_info, settings, success_count ,fail_count ,progress_dialog ,parent_widget):
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_image, image_path, data, settings, output_folder) for image_path, data in matched_info]

        for index, future in enumerate(futures):
            if progress_dialog.wasCanceled():
                executor.shutdown(wait=False)
                break

            result = future.result()  # Wait for the result before updating the progress
            image_path, error = result
            if error:
                print(f"Error processing {image_path}: {error}")
                fail_count += 1
            else:
                success_count += 1
            
            progress_dialog.setValue(success_count + fail_count)  # Update the progress dialog here
        
    if fail_count == 0:
        QMessageBox.information(parent_widget, "处理完成", f"所有图片处理成功，共处理{success_count}张图片。", QMessageBox.Ok)
    else:
        QMessageBox.warning(parent_widget, "处理完成", f"图片处理完成，成功{success_count}张，失败{fail_count}张。", QMessageBox.Ok)

