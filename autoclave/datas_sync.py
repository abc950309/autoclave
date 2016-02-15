from autoclave import db
import autoclave.file_tools as file_tools
import os.path

if not db.datas_meta.find_one({
        "name": "layout_options",
        "hash": file_tools.md5_for_file(os.path.join(os.path.dirname(__file__), "datas", "layout_options.py")),
    }):
    
    print("Sync Layout Options")
    from autoclave.datas.layout_options import LAYOUT_OPTIONS
    for line in LAYOUT_OPTIONS:
        db.layouts.remove({"_id": line["_id"]})
        db.layouts.insert(line)
    
    db.datas_meta.remove({"name": "layout_options"})
    db.datas_meta.insert({
        "name": "layout_options",
        "hash": file_tools.md5_for_file(os.path.join(os.path.dirname(__file__), "datas", "layout_options.py")),
    })