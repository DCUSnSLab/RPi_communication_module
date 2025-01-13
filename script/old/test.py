import struct
flat_data = [1.0, 0.5, 9.8] # 임의로 테스트
packed = struct.pack(f"<{len(flat_data)}f", *flat_data)
print("Hex (LE):", packed.hex())
