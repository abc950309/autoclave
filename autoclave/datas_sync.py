from autoclave import db
import autoclave.file_tools as file_tools
import autoclave.models as models
import os.path

from bson.dbref import DBRef

if not db.datas_meta.find_one({
        "name": "layout_options",
        "hash": file_tools.md5_for_file(os.path.join(os.path.dirname(__file__), "datas", "layout_options.py")),
    }):
    
    print("Sync Layout Options")
    from autoclave.datas.layout_options import LAYOUT_OPTIONS
    for line in LAYOUT_OPTIONS:
        db.layouts.remove({"_id": line["_id"]})
        db.layouts.insert(line)
        result = db.layouts.update_one(
            {"_id": line["_id"]},
            {
                "$set": {"display": DBRef("images", models.Image.new4layout(layout = DBRef("layouts", line["_id"]))._id)},
                "$currentDate": {"lastModified": True}
            }
        )
    
    
    db.datas_meta.remove({"name": "layout_options"})
    db.datas_meta.insert({
        "name": "layout_options",
        "hash": file_tools.md5_for_file(os.path.join(os.path.dirname(__file__), "datas", "layout_options.py")),
    })

