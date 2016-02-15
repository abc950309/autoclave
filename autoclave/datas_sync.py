from autoclave import db
import autoclave.file_tools as file_tools
import autoclave.models as models
from autoclave.js_tools import jsmin
from csscompressor import compress
import os.path
import os

from bson.dbref import DBRef

def minfy_static_files(type, dealer):
    raw_list = os.listdir( os.path.join( os.path.dirname(__file__), "static", type))
    list = []
    for line in raw_list:
        if os.path.isdir( os.path.join( os.path.dirname(__file__), "static", type, line ) ):
            continue
        if ".min." in line:
            continue
        file = ".".join(line.split(".")[0:-1])
        path = os.path.join( os.path.dirname(__file__), "static", type, line )
        
        if not db.datas_meta.find_one({
                "name": type + "_minfy",
                "file": file,
                "hash": file_tools.md5_for_file( path ),
            }):
            
            print(("minfy " + type + " file " + file).title())
            
            minfy_path = os.path.join( os.path.dirname(__file__), "static", type, file + ".min." + type )
            
            with open(path, "r", encoding = "utf-8") as input_f:
                minfy_file = dealer(input_f.read())
            with open(minfy_path, "w", encoding = "utf-8") as output_f:
                output_f.write(minfy_file)
            
            db.datas_meta.update(
                {
                    "name": type + "_minfy",
                    "file": file,
                },
                {
                    "$set": {
                        "hash": file_tools.md5_for_file( path )
                    }
                },
                upsert = True
            )

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
    db.datas_meta.update(
        {
            'name': 'layout_options'
        },
        {
            "$set": {
                "hash": file_tools.md5_for_file(os.path.join(os.path.dirname(__file__), "datas", "layout_options.py")),
            }
        },
        upsert = True
    )


minfy_static_files("js", jsmin)
minfy_static_files("css", compress)
