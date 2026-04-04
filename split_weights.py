import os

FILE_PATH = r"C:\Users\ashfi\.deepface\weights\age_model_weights.h5"
OUTPUT_DIR = r"C:\Users\ashfi\Downloads\Computervison\backend\weights_chunks"
CHUNK_SIZE = 49 * 1024 * 1024  # 49 MB per chunk to safely bypass the 50-100MB Github limit

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Splitting the DeepFace Age Model...")
with open(FILE_PATH, 'rb') as f:
    chunk_index = 0
    while True:
        chunk = f.read(CHUNK_SIZE)
        if not chunk:
            break
        
        output_file = os.path.join(OUTPUT_DIR, f"age_model_weights.part{chunk_index:03d}")
        with open(output_file, 'wb') as chunk_file:
            chunk_file.write(chunk)
            
        print(f"Wrote {output_file}")
        chunk_index += 1

print("Done! Split into", chunk_index, "chunks.")
