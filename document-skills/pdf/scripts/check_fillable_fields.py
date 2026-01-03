import sys
from pypdf import PdfReader


# 用于Claude运行的脚本，用于确定PDF是否有可填写的表单字段。请参见forms.md。


reader = PdfReader(sys.argv[1])
if (reader.get_fields()):
    print("该PDF有可填写的表单字段")
else:
    print("该PDF没有可填写的表单字段；您需要直观地确定在哪里输入数据")
