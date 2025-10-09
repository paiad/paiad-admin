from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from ultralytics import YOLO
from pathlib import Path
import uuid

# ==============================
# 基础配置
# ==============================
app = FastAPI(title="YOLO Detection API (Minimal)")

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 可改为前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = Path("./uploads")
RESULT_FOLDER = Path("./results")
MODEL_PATH = Path("./yolo11n.pt")

UPLOAD_FOLDER.mkdir(exist_ok=True)
RESULT_FOLDER.mkdir(exist_ok=True)

# 静态文件目录（用于访问检测结果图像）
app.mount("/yolo/files", StaticFiles(directory=RESULT_FOLDER, html=False), name="yolo-files")

# 加载 YOLO 模型
model = YOLO(MODEL_PATH.as_posix())

# 存储检测结果
results_cache = {}

# ==============================
# 上传并检测接口 /yolo/upload
# ==============================
@app.post("/yolo/upload")
async def upload_image(request: Request, image: UploadFile = File(...)):
    image_id = str(uuid.uuid4())
    filename = f"{image_id}_{image.filename}"
    save_path = UPLOAD_FOLDER / filename

    # 保存上传的文件
    with open(save_path, "wb") as f:
        f.write(await image.read())

    # 执行检测
    try:
        detection_results = model.predict(
            source=save_path.as_posix(),
            save=True,
            save_txt=False,
            project=RESULT_FOLDER.as_posix(),
            name=image_id
        )

        detections = []
        for result in detection_results:
            for box in result.boxes:
                cls = model.names[int(box.cls)]
                conf = float(box.conf)
                xyxy = box.xyxy.tolist()[0]
                detections.append({
                    "class": cls,
                    "confidence": round(conf, 3),
                    "bbox": [round(x, 2) for x in xyxy]
                })

        results_cache[image_id] = {
            "status": "completed",
            "result": detections,
            "filename": filename
        }

    except Exception as e:
        results_cache[image_id] = {
            "status": "failed",
            "error": str(e)
        }

    return JSONResponse({
        "code": 200,
        "msg": "Upload & detection successful",
        "data": {"taskId": image_id}
    })


# ==============================
# 获取检测结果接口 /yolo/results/{taskId}
# ==============================
@app.get("/yolo/results/{task_id}")
async def get_results(request: Request, task_id: str):
    task = results_cache.get(task_id)
    if not task:
        return JSONResponse({"code": 404, "msg": "Task not found"}, status_code=404)

    if task["status"] != "completed":
        return JSONResponse({"code": 202, "msg": "Detection failed or incomplete"}, status_code=202)

    # 构建完整可访问 URL
    base_url = str(request.base_url).rstrip("/")  # http://localhost:5000
    result_image_url = f"{base_url}/yolo/files/{task_id}/{task['filename']}"

    return JSONResponse({
        "code": 200,
        "msg": "Success",
        "data": {
            "taskId": task_id,
            "results": task["result"],
            "resultImage": result_image_url
        }
    })


# ==============================
# 启动服务
# ==============================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
