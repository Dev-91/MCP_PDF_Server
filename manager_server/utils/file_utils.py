import os
import colorlog
import logging
# colorlog가 설치되어 있지 않다면: pip install colorlog
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'bold_red',
    }
))
logger = colorlog.getLogger('file_utils')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def get_folder_tree(root_path, rel_path=""):
    # 최상위 폴더는 항상 'datasheets'로 표시
    if rel_path == "":
        folder_name = "datasheets"
    else:
        folder_name = os.path.basename(root_path)
    tree = {
        "name": folder_name,
        "type": "folder",
        "relpath": rel_path,
        "children": []
    }
    try:
        logger.info(f"Building folder tree for: {root_path}")
        for entry in sorted(os.listdir(root_path)):
            # 숨김 파일/폴더 무시
            if entry.startswith('.'):
                continue
            full_path = os.path.join(root_path, entry)
            child_relpath = os.path.join(rel_path, entry) if rel_path else entry
            if os.path.isdir(full_path):
                tree["children"].append(get_folder_tree(full_path, child_relpath))
            elif os.path.isfile(full_path):
                tree["children"].append({
                    "name": entry,
                    "type": "file",
                    "relpath": child_relpath
                })
        logger.info(f"Folder tree built for: {root_path}")
    except Exception as e:
        logger.error(f"Error building folder tree for {root_path}: {str(e)}")
        tree["error"] = str(e)
    return tree 