from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from ultralytics import YOLO
from pathlib import Path
import uuid
import shutil
from datetime import datetime
from PIL import Image

# ==============================
# 基础配置
# ==============================
app = FastAPI(title="YOLO Detection API with History")

UPLOAD_FOLDER = Path("./uploads")
RESULT_FOLDER = Path("./results")

UPLOAD_FOLDER.mkdir(exist_ok=True)
RESULT_FOLDER.mkdir(exist_ok=True)

# 静态文件目录
app.mount("/yolo/files", StaticFiles(directory=RESULT_FOLDER, html=False), name="yolo-files")

# 模型缓存，避免重复加载
loaded_models = {}

def get_model(model_name: str):
    model_path = Path(f"./{model_name}")
    if model_name not in loaded_models:
        if not model_path.exists():
            raise FileNotFoundError(f"Model file '{model_name}' not found")
        loaded_models[model_name] = YOLO(model_path.as_posix())
    return loaded_models[model_name]

# 检测结果缓存
results_cache = {}

# 历史记录缓存
history_records = {}

# ==============================
# 上传并检测接口
# ==============================
@app.post("/yolo/upload")
async def upload_image(
    request: Request,
    image: UploadFile = File(...),
    conf: float = 0.25,  # 置信度阈值，前端可传
    model_name: str = "yolo11n.pt"  # 模型文件名，前端可传
):
    image_id = uuid.uuid4().hex[:8]
    filename = f"{image_id}_{image.filename}"
    save_path = UPLOAD_FOLDER / filename

    # 保存上传文件
    with open(save_path, "wb") as f:
        f.write(await image.read())

    try:
        # 加载模型（动态选择）
        model = get_model(model_name)

        # YOLO 检测
        detection_results = model.predict(
            source=save_path.as_posix(),
            save=True,
            save_txt=False,
            conf=conf,  # 应用前端置信度阈值
            project=RESULT_FOLDER.as_posix(),
            name="predict",
            exist_ok=True
        )

        # 找出 YOLO 输出的图片
        output_dir = RESULT_FOLDER / "predict"
        result_images = list(output_dir.glob("*.jpg")) + list(output_dir.glob("*.png"))
        if not result_images:
            raise FileNotFoundError("No output image found in YOLO results.")

        result_image_path = max(result_images, key=lambda x: x.stat().st_mtime)
        final_path = RESULT_FOLDER / result_image_path.name
        shutil.move(result_image_path, final_path)
        shutil.rmtree(output_dir, ignore_errors=True)

        # 解析检测结果
        detections = []
        for result in detection_results:
            for box in result.boxes:
                cls = model.names[int(box.cls)]
                conf_score = float(box.conf)
                xyxy = box.xyxy.tolist()[0]
                detections.append({
                    "class": cls,
                    "confidence": round(conf_score, 3),
                    "bbox": [round(x, 2) for x in xyxy]
                })

        # 保存结果缓存
        results_cache[image_id] = {
            "status": "completed",
            "result": detections,
            "result_image": final_path.name
        }

        # ===== 记录历史信息 =====
        img = Image.open(final_path)
        history_records[image_id] = {
            "file_id": image_id,
            "file_name": final_path.name,
            "upload_time": datetime.now().isoformat(),
            "width": img.width,
            "height": img.height,
            "file_type": final_path.suffix[1:],
            "url": f"{str(request.base_url).rstrip('/')}/yolo/files/{final_path.name}"
        }

    except Exception as e:
        results_cache[image_id] = {"status": "failed", "error": str(e)}
        return JSONResponse({"code": 500, "msg": str(e)})

    return JSONResponse({
        "code": 200,
        "msg": "Upload & detection successful",
        "data": {
            "taskId": image_id,
            "model": model_name,
            "confidence": conf
        }
    })


# ==============================
# 查询历史接口
# ==============================
@app.get("/yolo/history")
async def list_history():
    return JSONResponse({"code": 200, "msg": "Success", "data": list(history_records.values())})


# ==============================
# 删除历史图片
# ==============================
@app.delete("/yolo/history/{file_id}")
async def delete_history(file_id: str):
    record = history_records.get(file_id)
    if not record:
        return JSONResponse({"code": 404, "msg": "File not found"}, status_code=404)

    # 删除物理文件
    file_path = RESULT_FOLDER / record["file_name"]
    if file_path.exists():
        file_path.unlink()

    # 删除缓存
    history_records.pop(file_id, None)
    results_cache.pop(file_id, None)

    return JSONResponse({"code": 200, "msg": "Deleted successfully"})


# ==============================
# 获取检测结果
# ==============================
@app.get("/yolo/results/{task_id}")
async def get_results(request: Request, task_id: str):
    task = results_cache.get(task_id)
    if not task:
        return JSONResponse({"code": 404, "msg": "Task not found"}, status_code=404)
    if task["status"] != "completed":
        return JSONResponse({"code": 202, "msg": "Detection failed or incomplete"}, status_code=202)

    base_url = str(request.base_url).rstrip("/")
    result_image_url = f"{base_url}/yolo/files/{task['result_image']}"
    return JSONResponse({
        "code": 200,
        "msg": "Success",
        "data": {
            "taskId": task_id,
            "results": task["result"],
            "resultImage": result_image_url
        }
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
