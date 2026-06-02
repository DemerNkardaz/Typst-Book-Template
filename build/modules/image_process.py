import io

import pikepdf
from PIL import Image, ImageCms
from pikepdf import Name


def convert_images(pdf: pikepdf.Pdf, icc_data: bytes, dst_channels: int) -> int:
    dst_profile = ImageCms.ImageCmsProfile(io.BytesIO(icc_data))
    dst_mode = "CMYK" if dst_channels == 4 else "RGB"

    converted = 0
    for page in pdf.pages:
        resources = page.get("/Resources")
        if not resources:
            continue
        xobjects = resources.get("/XObject")
        if not xobjects:
            continue
        for key in xobjects.keys():
            xobj = xobjects[key]
            if xobj.get("/Subtype") != "/Image":
                continue

            try:
                raw = bytes(xobj.read_bytes())
                width = int(xobj["/Width"])
                height = int(xobj["/Height"])
                cs = xobj.get("/ColorSpace")

                if isinstance(cs, pikepdf.Array) and str(cs[0]) == "/ICCBased":
                    src_icc = bytes(cs[1].read_bytes())
                    src_profile = ImageCms.ImageCmsProfile(io.BytesIO(src_icc))
                else:
                    src_profile = ImageCms.createProfile("sRGB")

                img = Image.frombytes("RGB", (width, height), raw)
            except Exception:
                continue

            img = img.convert("RGB")

            transform = ImageCms.buildTransform(
                src_profile,
                dst_profile,
                "RGB",
                dst_mode,
                renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,
            )
            out_img = ImageCms.applyTransform(img, transform)
            if out_img is None:
                continue

            buf = io.BytesIO()
            out_img.save(buf, format="JPEG", quality=95)
            new_data = buf.getvalue()

            xobj.write(new_data, filter=Name("/DCTDecode"))
            xobj["/ColorSpace"] = (
                Name("/DeviceCMYK") if dst_channels == 4 else Name("/DeviceRGB")
            )
            if dst_channels == 4:
                xobj["/Decode"] = pikepdf.Array([1, 0, 1, 0, 1, 0, 1, 0])
            converted += 1

    return converted
