import os
import zipfile

file_name = "app.zip"

zf = zipfile.ZipFile(file_name, "w", zipfile.ZIP_DEFLATED, compresslevel=9)

zf.write("aws_post.py")
zf.write(".env")

os.chdir("Lib\site-packages")
for dirname, subdirs, files in os.walk("./"):
    zf.write(dirname)
    if "./pip" in dirname:
        print (dirname)
    else:
        for filename in files:
            zf.write(os.path.join(dirname, filename))