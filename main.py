from fastapi import FastAPI, UploadFile, File, status
from fastapi.responses import JSONResponse, FileResponse
import time
import platform
import subprocess
import os
import tempfile

app = FastAPI()
start_time = time.time()

@app.get("/healthz")
async def healthz():
  current_time = time.time()
  return {
    "status": "OK",
    "uptime": current_time - start_time,
    "running-on": platform.version()
  }
  
@app.post("/compile")
async def compile(file: UploadFile = File(...)):
  if not file:
    return JSONResponse(
      status_code=status.HTTP_404_NOT_FOUND,
      content={ "error": "No file uploaded" }
    )
  
  try:
    tmp_dir = os.path.join(os.getcwd(), "tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    
    with tempfile.NamedTemporaryFile(dir=tmp_dir, suffix=f"_{file.filename}", delete=False) as temp_file:
      content = await file.read()
      temp_file.write(content)
      temp_file_path = temp_file.name

    output_file_name = f"output_{os.urandom(4).hex()}.out"
    output_file_path = os.path.join(tmp_dir, output_file_name)

    result = subprocess.run(
      ["g++-15", "-std=c++17", "-O2", temp_file_path, "-o", output_file_path],
      capture_output=True,
      text=True
    )

    os.unlink(temp_file_path)

    if result.returncode != 0:
      return JSONResponse(
        status_code=status.HTTP_418_IM_A_TEAPOT,
        content={ "error": "Compilation Failed", "details": result.stderr }
      )

    return FileResponse(
      path=output_file_path,
      media_type='application/octet-stream',
      filename=f"{os.path.splitext(file.filename)[0]}.out"
    )

  except Exception as e:
    return JSONResponse(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      content={ "error": f"Internal Server Error: {str(e)}" }
    )
    
@app.delete("/cleanup")
async def cleanup():
  try:
    tmp_dir = os.path.join(os.getcwd(), "tmp")
    if os.path.exists(tmp_dir):
      for filename in os.listdir(tmp_dir):
        file_path = os.path.join(tmp_dir, filename)
        if os.path.isfile(file_path):
          os.unlink(file_path)
    return { "status": "Cleanup successful" }
  except Exception as e:
    return JSONResponse(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      content={ "error": f"Cleanup Failed: {str(e)}" }
    )
  
if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=8080)