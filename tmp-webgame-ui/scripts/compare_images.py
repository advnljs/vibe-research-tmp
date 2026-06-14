#!/usr/bin/env python3
import pathlib
import struct
import sys
import zlib


def read_png_rgb(path: pathlib.Path):
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG file")

    offset = 8
    width = height = color_type = None
    compressed = bytearray()

    while offset < len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_type = data[offset + 4 : offset + 8]
        chunk = data[offset + 8 : offset + 8 + length]
        offset += length + 12
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, _, _, _ = struct.unpack(">IIBBBBB", chunk)
            if bit_depth != 8 or color_type not in (2, 6):
                raise ValueError("Only 8-bit RGB/RGBA PNG files are supported")
        elif chunk_type == b"IDAT":
            compressed.extend(chunk)
        elif chunk_type == b"IEND":
            break

    channels = 3 if color_type == 2 else 4
    stride = width * channels
    raw = zlib.decompress(compressed)
    rows = []
    previous = bytearray(stride)
    index = 0

    for _ in range(height):
        filter_type = raw[index]
        index += 1
        scanline = bytearray(raw[index : index + stride])
        index += stride
        reconstructed = bytearray(stride)
        for column, value in enumerate(scanline):
            left = reconstructed[column - channels] if column >= channels else 0
            up = previous[column]
            upper_left = previous[column - channels] if column >= channels else 0
            if filter_type == 0:
                result = value
            elif filter_type == 1:
                result = (value + left) & 255
            elif filter_type == 2:
                result = (value + up) & 255
            elif filter_type == 3:
                result = (value + ((left + up) // 2)) & 255
            elif filter_type == 4:
                estimate = left + up - upper_left
                distances = (abs(estimate - left), abs(estimate - up), abs(estimate - upper_left))
                predictor = (left, up, upper_left)[distances.index(min(distances))]
                result = (value + predictor) & 255
            else:
                raise ValueError(f"Unsupported PNG filter type: {filter_type}")
            reconstructed[column] = result
        rows.append(bytes(reconstructed))
        previous = reconstructed

    rgb = bytearray()
    for row in rows:
        for offset in range(0, len(row), channels):
            rgb.extend(row[offset : offset + 3])
    return width, height, bytes(rgb)


def main():
    reference_path = pathlib.Path(sys.argv[1])
    screenshot_path = pathlib.Path(sys.argv[2])
    ref_width, ref_height, reference = read_png_rgb(reference_path)
    shot_width, shot_height, screenshot = read_png_rgb(screenshot_path)
    if (ref_width, ref_height) != (shot_width, shot_height):
        raise SystemExit(
            f"size_mismatch reference={ref_width}x{ref_height} screenshot={shot_width}x{shot_height}"
        )

    absolute_error = 0
    max_error = 0
    changed_channels = 0
    for expected, actual in zip(reference, screenshot):
        difference = abs(expected - actual)
        absolute_error += difference
        max_error = max(max_error, difference)
        changed_channels += difference != 0

    channel_count = len(reference)
    print(f"dimensions={ref_width}x{ref_height}")
    print(f"mean_absolute_error={absolute_error / channel_count:.6f}")
    print(f"max_channel_error={max_error}")
    print(f"changed_channels={changed_channels}/{channel_count}")
    if changed_channels:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
