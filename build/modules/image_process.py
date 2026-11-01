import io

import pikepdf
from PIL import Image, ImageCms
from pikepdf import Name
import zlib

_DEVICE_COLORSPACES = {
    1: ("GRAY", "L", Name("/DeviceGray")),
    3: ("RGB ", "RGB", Name("/DeviceRGB")),
    4: ("CMYK", "CMYK", Name("/DeviceCMYK")),
}

def _object_key(obj: pikepdf.Object) -> tuple[int, int] | int:
    objgen = tuple(obj.objgen)
    return objgen if objgen != (0, 0) else id(obj)

def _image_xobjects(resources: pikepdf.Object, seen_forms: set) -> list[pikepdf.Object]:
    if not isinstance(resources, pikepdf.Dictionary):
        return []

    xobjects = resources.get("/XObject")
    if not isinstance(xobjects, pikepdf.Dictionary):
        return []

    images = []
    for xobject in xobjects.values():
        subtype = xobject.get("/Subtype")
        if subtype == Name("/Image"):
            images.append(xobject)
        elif subtype == Name("/Form"):
            key = _object_key(xobject)
            if key not in seen_forms:
                seen_forms.add(key)
                images.extend(
                    _image_xobjects(xobject.get("/Resources"), seen_forms)
                )

    return images

def _source_profile(image: pikepdf.PdfImage):
    if image.icc is not None:
        profile = image.icc
    elif image.colorspace == "/DeviceRGB":
        profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB"))
    else:
        return None

    source_space = profile.profile.xcolor_space
    if isinstance(source_space, bytes):
        source_space = source_space.decode("ascii", errors="replace")
    source_space = source_space[:4].ljust(4)

    expected_mode = {"GRAY": "L", "RGB ": "RGB", "CMYK": "CMYK"}.get(
        source_space
    )
    if expected_mode != image.mode:
        return None

    return profile

def convert_images(
    pdf: pikepdf.Pdf,
    icc_data: bytes,
    dst_channels: int,
) -> tuple[int, int]:
    destination = _DEVICE_COLORSPACES.get(dst_channels)
    if destination is None:
        raise ValueError(f"Unsupported ICC output channel count: {dst_channels}")

    dst_space, dst_mode, dst_color_space = destination
    dst_profile = ImageCms.ImageCmsProfile(io.BytesIO(icc_data))
    profile_space = dst_profile.profile.xcolor_space
    if isinstance(profile_space, bytes):
        profile_space = profile_space.decode("ascii", errors="replace")
    if profile_space[:4].ljust(4) != dst_space:
        raise ValueError(
            f"ICC profile color space {profile_space!r} does not match "
            f"{dst_channels} output channels"
        )

    converted = 0
    skipped = 0
    seen_forms: set = set()
    seen_images: set = set()

    for page in pdf.pages:
        resources = page.get("/Resources")
        for xobject in _image_xobjects(resources, seen_forms):
            key = _object_key(xobject)
            if key in seen_images:
                continue
            seen_images.add(key)

            if (
                xobject.get("/ImageMask", False)
                or xobject.get("/Mask") is not None
            ):
                skipped += 1
                continue

            try:
                source_image = pikepdf.PdfImage(xobject)
                if (
                    source_image.bits_per_component != 8
                    or source_image.indexed
                    or source_image.is_separation
                    or source_image.is_device_n
                    or source_image.mode not in {"L", "RGB", "CMYK"}
                ):
                    skipped += 1
                    continue

                src_profile = _source_profile(source_image)
                if src_profile is None:
                    skipped += 1
                    continue

                image = source_image.as_pil_image()
                if "A" in image.getbands():
                    skipped += 1
                    continue

                transform = ImageCms.buildTransform(
                    src_profile,
                    dst_profile,
                    image.mode,
                    dst_mode,
                    renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,
                )
                converted_image = ImageCms.applyTransform(image, transform)
            except Exception:
                skipped += 1
                continue

            xobject.write(
                zlib.compress(converted_image.tobytes()),
                filter=Name("/FlateDecode"),
            )
            xobject["/ColorSpace"] = dst_color_space
            xobject["/BitsPerComponent"] = 8
            if "/Decode" in xobject:
                del xobject["/Decode"]
            if "/DecodeParms" in xobject:
                del xobject["/DecodeParms"]
            converted += 1

    return converted, skipped
