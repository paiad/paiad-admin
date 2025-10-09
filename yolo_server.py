from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from ultralytics import YOLO
from pathlib import Path
from PIL import Image
import uuid, shutil, json, pymysql, logging
from datetime import datetime

# ==============================
# 日志配置
# ==============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ==============================
# FastAPI 初始化
# ==============================
app = FastAPI(title="YOLO Detection API with MySQL")

# ==============================
# 文件路径配置
# ==============================
UPLOAD_FOLDER = Path("./uploads")
RESULT_FOLDER = Path("./results")

UPLOAD_FOLDER.mkdir(exist_ok=True)
RESULT_FOLDER.mkdir(exist_ok=True)

# 静态资源挂载
app.mount("/yolo/files", StaticFiles(directory=RESULT_FOLDER, html=False), name="yolo-files")

# ==============================
# 数据库连接
# ==============================
def get_db_connection():
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="root",  # 修改此处
            database="paiad-admin",
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        logger.info("✅ 数据库连接成功")
        return conn
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")
        raise e

# ==============================
# 模型缓存
# ==============================
loaded_models = {}

def get_model(model_name: str):
    model_path = Path(f"./{model_name}")
    if model_name not in loaded_models:
        if not model_path.exists():
            raise FileNotFoundError(f"Model file '{model_name}' not found")
        logger.info(f"📦 正在加载模型: {model_name}")
        loaded_models[model_name] = YOLO(model_path.as_posix())
        logger.info(f"✅ 模型加载完成: {model_name}")
    else:
        logger.info(f"♻️ 使用已缓存的模型: {model_name}")
    return loaded_models[model_name]

# ==============================
# 上传并检测接口
# ==============================
@app.post("/yolo/upload")
async def upload_image(
    request: Request,
    image: UploadFile = File(...),
    conf: float = 0.25,
    model_name: str = "yolo11n.pt"
):
    logger.info(f"🟡 前端请求检测: 模型={model_name}, 置信度={conf}")
    image_id = uuid.uuid4().hex[:8]
    filename = f"{image_id}_{image.filename}"
    save_path = UPLOAD_FOLDER / filename

    # 保存上传图片
    with open(save_path, "wb") as f:
        f.write(await image.read())
    logger.info(f"📸 图片已保存: {save_path}")

    try:
        # 加载模型
        model = get_model(model_name)

        # 执行检测
        logger.info("🚀 开始YOLO检测...")
        detection_results = model.predict(
            source=save_path.as_posix(),
            save=True,
            save_txt=False,
            conf=conf,
            project=RESULT_FOLDER.as_posix(),
            name="predict",
            exist_ok=True
        )
        logger.info("✅ 检测完成")

        # 查找检测结果图片
        output_dir = RESULT_FOLDER / "predict"
        result_images = list(output_dir.glob("*.jpg")) + list(output_dir.glob("*.png"))
        if not result_images:
            raise FileNotFoundError("No output image found in YOLO results.")
        result_image_path = max(result_images, key=lambda x: x.stat().st_mtime)
        final_path = RESULT_FOLDER / result_image_path.name
        shutil.move(result_image_path, final_path)
        shutil.rmtree(output_dir, ignore_errors=True)
        logger.info(f"🖼 检测结果图片保存为: {final_path}")

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
        logger.info(f"📊 检测结果解析完成，共 {len(detections)} 个目标")

        img = Image.open(final_path)

        # 组装文件信息
        file_info = {
            "file_id": image_id,
            "file_name": final_path.name,
            "upload_time": datetime.now().isoformat(),
            "width": img.width,
            "height": img.height,
            "file_type": final_path.suffix[1:],
            "url": f"{str(request.base_url).rstrip('/')}/yolo/files/{final_path.name}",
            "file_details": detections
        }

        # 写入数据库
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO paiad_yolo
                (file_id, file_name, upload_time, width, height, file_type, url, file_details)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                file_info["file_id"],
                file_info["file_name"],
                file_info["upload_time"],
                file_info["width"],
                file_info["height"],
                file_info["file_type"],
                file_info["url"],
                json.dumps(file_info["file_details"], ensure_ascii=False)
            ))
        conn.commit()
        conn.close()
        logger.info(f"💾 数据已写入数据库: {file_info['file_id']}")

    except Exception as e:
        logger.error(f"❌ 检测失败: {e}")
        return JSONResponse({"code": 500, "msg": str(e)})

    return JSONResponse({
        "code": 200,
        "msg": "Upload & detection successful",
        "data": file_info
    })

# ==============================
# 历史记录接口
# ==============================
@app.get("/yolo/history")
async def list_history():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM paiad_yolo ORDER BY create_time DESC")
            records = cursor.fetchall()
        conn.close()

        # 转换字段格式
        for record in records:
            # 转换 datetime 为字符串
            for k, v in record.items():
                if isinstance(v, datetime):
                    record[k] = v.isoformat()

            # 转换 JSON 字段
            if record.get("file_details"):
                record["file_details"] = json.loads(record["file_details"])

        logger.info(f"📜 读取历史记录，共 {len(records)} 条")

        return JSONResponse({"code": 200, "msg": "Success", "data": records})
    except Exception as e:
        logger.error(f"❌ 获取历史记录失败: {e}")
        return JSONResponse({"code": 500, "msg": str(e)})


# ==============================
# 删除记录接口
# ==============================
@app.delete("/yolo/history/{file_id}")
async def delete_history(file_id: str):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT file_name FROM paiad_yolo WHERE file_id=%s", (file_id,))
            record = cursor.fetchone()

            if not record:
                return JSONResponse({"code": 404, "msg": "File not found"})

            file_path = RESULT_FOLDER / record["file_name"]
            if file_path.exists():
                file_path.unlink()

            cursor.execute("DELETE FROM paiad_yolo WHERE file_id=%s", (file_id,))
        conn.commit()
        conn.close()
        logger.info(f"🗑 已删除记录及文件: {file_id}")

        return JSONResponse({"code": 200, "msg": "Deleted successfully"})
    except Exception as e:
        logger.error(f"❌ 删除失败: {e}")
        return JSONResponse({"code": 500, "msg": str(e)})

# ==============================
# 获取结果接口
# ==============================
@app.get("/yolo/results/{file_id}")
async def get_results(file_id: str):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM paiad_yolo WHERE file_id=%s", (file_id,))
            record = cursor.fetchone()
        conn.close()

        if not record:
            return JSONResponse({"code": 404, "msg": "Task not found"})

        record["file_details"] = json.loads(record["file_details"]) if record.get("file_details") else []
        logger.info(f"📦 查询检测结果: {file_id}")
        return JSONResponse({"code": 200, "msg": "Success", "data": record})
    except Exception as e:
        logger.error(f"❌ 查询失败: {e}")
        return JSONResponse({"code": 500, "msg": str(e)})

# ==============================
# 启动服务
# ==============================
if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 YOLO FastAPI 服务启动中...")
    uvicorn.run(app, host="0.0.0.0", port=5000)
