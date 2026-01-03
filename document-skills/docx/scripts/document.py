#!/usr/bin/env python3
"""
用于处理Word文档的库：注释、修订记录和编辑功能。

使用方法：
    from skills.docx.scripts.document import Document

    # 初始化
    doc = Document('workspace/unpacked')
    doc = Document('workspace/unpacked', author="张三", initials="ZS")

    # 查找节点
    node = doc["word/document.xml"].get_node(tag="w:del", attrs={"w:id": "1"})
    node = doc["word/document.xml"].get_node(tag="w:p", line_number=10)

    # 添加注释
    doc.add_comment(start=node, end=node, text="注释内容")
    doc.reply_to_comment(parent_comment_id=0, text="回复内容")

    # 建议修订记录
    doc["word/document.xml"].suggest_deletion(node)  # 删除内容
    doc["word/document.xml"].revert_insertion(ins_node)  # 拒绝插入
    doc["word/document.xml"].revert_deletion(del_node)  # 拒绝删除

    # 保存
    doc.save()
"""

import html
import random
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from defusedxml import minidom
from ooxml.scripts.pack import pack_document
from ooxml.scripts.validation.docx import DOCXSchemaValidator
from ooxml.scripts.validation.redlining import RedliningValidator

from .utilities import XMLEditor

# 模板文件路径
TEMPLATE_DIR = Path(__file__).parent / "templates"


class DocxXMLEditor(XMLEditor):
    """XMLEditor的扩展类，自动为新元素应用RSID、作者和日期属性。

    在插入新内容时，自动为支持的元素添加属性：
    - w:rsidR, w:rsidRDefault, w:rsidP（用于w:p和w:r元素）
    - w:author和w:date（用于w:ins, w:del, w:comment元素）
    - w:id（用于w:ins和w:del元素）

    属性:
        dom (defusedxml.minidom.Document): 用于直接操作的DOM文档
    """

    def __init__(
        self, xml_path, rsid: str, author: str = "Claude", initials: str = "C"
    ):
        """使用必需的RSID和可选的作者信息初始化。

        参数:
            xml_path: 要编辑的XML文件路径
            rsid: 自动应用于新元素的RSID
            author: 修订记录和注释的作者名称（默认: "Claude"）
            initials: 作者缩写（默认: "C"）
        """
        super().__init__(xml_path)
        self.rsid = rsid
        self.author = author
        self.initials = initials

    def _get_next_change_id(self):
        """通过检查所有修订记录元素获取下一个可用的变更ID。"""
        max_id = -1
        for tag in ("w:ins", "w:del"):
            elements = self.dom.getElementsByTagName(tag)
            for elem in elements:
                change_id = elem.getAttribute("w:id")
                if change_id:
                    try:
                        max_id = max(max_id, int(change_id))
                    except ValueError:
                        pass
        return max_id + 1

    def _ensure_w16du_namespace(self):
        """确保在根元素上声明w16du命名空间。"""
        root = self.dom.documentElement
        if not root.hasAttribute("xmlns:w16du"):  # type: ignore
            root.setAttribute(  # type: ignore
                "xmlns:w16du",
                "http://schemas.microsoft.com/office/word/2023/wordml/word16du",
            )

    def _ensure_w16cex_namespace(self):
        """确保在根元素上声明w16cex命名空间。"""
        root = self.dom.documentElement
        if not root.hasAttribute("xmlns:w16cex"):  # type: ignore
            root.setAttribute(  # type: ignore
                "xmlns:w16cex",
                "http://schemas.microsoft.com/office/word/2018/wordml/cex",
            )

    def _ensure_w14_namespace(self):
        """确保在根元素上声明w14命名空间。"""
        root = self.dom.documentElement
        if not root.hasAttribute("xmlns:w14"):  # type: ignore
            root.setAttribute(  # type: ignore
                "xmlns:w14",
                "http://schemas.microsoft.com/office/word/2010/wordml",
            )

    def _inject_attributes_to_nodes(self, nodes):
        """将RSID、作者和日期属性注入到适用的DOM节点中。

        为支持的元素添加属性：
        - w:r: 添加w:rsidR（如果在w:del内部则添加w:rsidDel）
        - w:p: 添加w:rsidR, w:rsidRDefault, w:rsidP, w14:paraId, w14:textId
        - w:t: 如果文本有前导/尾随空白，则添加xml:space="preserve"
        - w:ins, w:del: 添加w:id, w:author, w:date, w16du:dateUtc
        - w:comment: 添加w:author, w:date, w:initials
        - w16cex:commentExtensible: 添加w16cex:dateUtc

        参数:
            nodes: 要处理的DOM节点列表
        """
        from datetime import datetime, timezone

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        def is_inside_deletion(elem):
            """检查元素是否在w:del元素内部。"""
            parent = elem.parentNode
            while parent:
                if parent.nodeType == parent.ELEMENT_NODE and parent.tagName == "w:del":
                    return True
                parent = parent.parentNode
            return False

        def add_rsid_to_p(elem):
            if not elem.hasAttribute("w:rsidR"):
                elem.setAttribute("w:rsidR", self.rsid)
            if not elem.hasAttribute("w:rsidRDefault"):
                elem.setAttribute("w:rsidRDefault", self.rsid)
            if not elem.hasAttribute("w:rsidP"):
                elem.setAttribute("w:rsidP", self.rsid)
            # 如果不存在，添加w14:paraId和w14:textId
            if not elem.hasAttribute("w14:paraId"):
                self._ensure_w14_namespace()
                elem.setAttribute("w14:paraId", _generate_hex_id())
            if not elem.hasAttribute("w14:textId"):
                self._ensure_w14_namespace()
                elem.setAttribute("w14:textId", _generate_hex_id())

        def add_rsid_to_r(elem):
            # 对于<w:del>内部的<w:r>使用w:rsidDel，否则使用w:rsidR
            if is_inside_deletion(elem):
                if not elem.hasAttribute("w:rsidDel"):
                    elem.setAttribute("w:rsidDel", self.rsid)
            else:
                if not elem.hasAttribute("w:rsidR"):
                    elem.setAttribute("w:rsidR", self.rsid)

        def add_tracked_change_attrs(elem):
            # 如果不存在，自动分配w:id
            if not elem.hasAttribute("w:id"):
                elem.setAttribute("w:id", str(self._get_next_change_id()))
            if not elem.hasAttribute("w:author"):
                elem.setAttribute("w:author", self.author)
            if not elem.hasAttribute("w:date"):
                elem.setAttribute("w:date", timestamp)
            # 为修订记录添加w16du:dateUtc（与w:date相同，因为我们生成UTC时间戳）
            if elem.tagName in ("w:ins", "w:del") and not elem.hasAttribute(
                "w16du:dateUtc"
            ):
                self._ensure_w16du_namespace()
                elem.setAttribute("w16du:dateUtc", timestamp)

        def add_comment_attrs(elem):
            if not elem.hasAttribute("w:author"):
                elem.setAttribute("w:author", self.author)
            if not elem.hasAttribute("w:date"):
                elem.setAttribute("w:date", timestamp)
            if not elem.hasAttribute("w:initials"):
                elem.setAttribute("w:initials", self.initials)

        def add_comment_extensible_date(elem):
            # 为注释可扩展元素添加w16cex:dateUtc
            if not elem.hasAttribute("w16cex:dateUtc"):
                self._ensure_w16cex_namespace()
                elem.setAttribute("w16cex:dateUtc", timestamp)

        def add_xml_space_to_t(elem):
            # 如果文本有前导/尾随空格，为w:t添加xml:space="preserve"
            if (
                elem.firstChild
                and elem.firstChild.nodeType == elem.firstChild.TEXT_NODE
            ):
                text = elem.firstChild.data
                if text and (text[0].isspace() or text[-1].isspace()):
                    if not elem.hasAttribute("xml:space"):
                        elem.setAttribute("xml:space", "preserve")

        for node in nodes:
            if node.nodeType != node.ELEMENT_NODE:
                continue

            # 处理节点本身
            if node.tagName == "w:p":
                add_rsid_to_p(node)
            elif node.tagName == "w:r":
                add_rsid_to_r(node)
            elif node.tagName == "w:t":
                add_xml_space_to_t(node)
            elif node.tagName in ("w:ins", "w:del"):
                add_tracked_change_attrs(node)
            elif node.tagName == "w:comment":
                add_comment_attrs(node)
            elif node.tagName == "w16cex:commentExtensible":
                add_comment_extensible_date(node)

            # 处理后代（getElementsByTagName不返回元素本身）
            for elem in node.getElementsByTagName("w:p"):
                add_rsid_to_p(elem)
            for elem in node.getElementsByTagName("w:r"):
                add_rsid_to_r(elem)
            for elem in node.getElementsByTagName("w:t"):
                add_xml_space_to_t(elem)
            for tag in ("w:ins", "w:del"):
                for elem in node.getElementsByTagName(tag):
                    add_tracked_change_attrs(elem)
            for elem in node.getElementsByTagName("w:comment"):
                add_comment_attrs(elem)
            for elem in node.getElementsByTagName("w16cex:commentExtensible"):
                add_comment_extensible_date(elem)

    def replace_node(self, elem, new_content):
        """替换节点并自动注入属性。"""
        nodes = super().replace_node(elem, new_content)
        self._inject_attributes_to_nodes(nodes)
        return nodes

    def insert_after(self, elem, xml_content):
        """在元素后插入并自动注入属性。"""
        nodes = super().insert_after(elem, xml_content)
        self._inject_attributes_to_nodes(nodes)
        return nodes

    def insert_before(self, elem, xml_content):
        """在元素前插入并自动注入属性。"""
        nodes = super().insert_before(elem, xml_content)
        self._inject_attributes_to_nodes(nodes)
        return nodes

    def append_to(self, elem, xml_content):
        """追加内容并自动注入属性。"""
        nodes = super().append_to(elem, xml_content)
        self._inject_attributes_to_nodes(nodes)
        return nodes

    def revert_insertion(self, elem):
        """通过将插入内容包装在删除标记中来拒绝插入操作。

        将w:ins内部的所有run包装在w:del中，并将w:t转换为w:delText。
        可以处理单个w:ins元素或包含多个w:ins的容器元素。

        参数:
            elem: 要处理的元素（w:ins, w:p, w:body等）

        返回:
            list: 包含处理后元素的列表

        异常:
            ValueError: 如果元素不包含w:ins元素

        示例:
            # 拒绝单个插入操作
            ins = doc["word/document.xml"].get_node(tag="w:ins", attrs={"w:id": "5"})
            doc["word/document.xml"].revert_insertion(ins)

            # 拒绝段落中的所有插入操作
            para = doc["word/document.xml"].get_node(tag="w:p", line_number=42)
            doc["word/document.xml"].revert_insertion(para)
        """
        # 收集插入内容
        ins_elements = []
        if elem.tagName == "w:ins":
            ins_elements.append(elem)
        else:
            ins_elements.extend(elem.getElementsByTagName("w:ins"))

        # 验证是否有要拒绝的插入内容
        if not ins_elements:
            raise ValueError(
                f"revert_insertion requires w:ins elements. "
                f"The provided element <{elem.tagName}> contains no insertions. "
            )

        # 处理所有插入内容 - 将所有子节点包装在w:del中
        for ins_elem in ins_elements:
            runs = list(ins_elem.getElementsByTagName("w:r"))
            if not runs:
                continue

            # 创建删除包装器
            del_wrapper = self.dom.createElement("w:del")

            # 处理每个运行
            for run in runs:
                # 转换w:t → w:delText和w:rsidR → w:rsidDel
                if run.hasAttribute("w:rsidR"):
                    run.setAttribute("w:rsidDel", run.getAttribute("w:rsidR"))
                    run.removeAttribute("w:rsidR")
                elif not run.hasAttribute("w:rsidDel"):
                    run.setAttribute("w:rsidDel", self.rsid)

                for t_elem in list(run.getElementsByTagName("w:t")):
                    del_text = self.dom.createElement("w:delText")
                    # 复制所有子节点（不仅仅是firstChild）以处理实体
                    while t_elem.firstChild:
                        del_text.appendChild(t_elem.firstChild)
                    for i in range(t_elem.attributes.length):
                        attr = t_elem.attributes.item(i)
                        del_text.setAttribute(attr.name, attr.value)
                    t_elem.parentNode.replaceChild(del_text, t_elem)

            # 将所有子节点从ins移动到del包装器
            while ins_elem.firstChild:
                del_wrapper.appendChild(ins_elem.firstChild)

            # 将del包装器添加回ins
            ins_elem.appendChild(del_wrapper)

            # 向删除包装器注入属性
            self._inject_attributes_to_nodes([del_wrapper])

        return [elem]

    def revert_deletion(self, elem):
        """通过重新插入已删除的内容来拒绝删除操作。

        在每个w:del之后创建w:ins元素，复制删除的内容并将w:delText转换回w:t。
        可以处理单个w:del元素或包含多个w:del的容器元素。

        参数:
            elem: 要处理的元素（w:del, w:p, w:body等）

        返回:
            list: 如果elem是w:del，返回[elem, new_ins]。否则返回[elem]。

        异常:
            ValueError: 如果元素不包含w:del元素

        示例:
            # 拒绝单个删除操作 - 返回 [w:del, w:ins]
            del_elem = doc["word/document.xml"].get_node(tag="w:del", attrs={"w:id": "3"})
            nodes = doc["word/document.xml"].revert_deletion(del_elem)

            # 拒绝段落中的所有删除操作 - 返回 [para]
            para = doc["word/document.xml"].get_node(tag="w:p", line_number=42)
            nodes = doc["word/document.xml"].revert_deletion(para)
        """
        # 首先收集删除内容 - 在修改DOM之前
        del_elements = []
        is_single_del = elem.tagName == "w:del"

        if is_single_del:
            del_elements.append(elem)
        else:
            del_elements.extend(elem.getElementsByTagName("w:del"))

        # 验证是否有要拒绝的删除内容
        if not del_elements:
            raise ValueError(
                f"revert_deletion requires w:del elements. "
                f"The provided element <{elem.tagName}> contains no deletions. "
            )

        # 跟踪创建的插入（仅当elem是单个w:del时相关）
        created_insertion = None

        # 处理所有删除内容 - 创建复制已删除内容的插入
        for del_elem in del_elements:
            # 克隆已删除的运行并将它们转换为插入
            runs = list(del_elem.getElementsByTagName("w:r"))
            if not runs:
                continue

            # 创建插入包装器
            ins_elem = self.dom.createElement("w:ins")

            for run in runs:
                # 克隆运行
                new_run = run.cloneNode(True)

                # 转换w:delText → w:t
                for del_text in list(new_run.getElementsByTagName("w:delText")):
                    t_elem = self.dom.createElement("w:t")
                    # 复制所有子节点（不仅仅是firstChild）以处理实体
                    while del_text.firstChild:
                        t_elem.appendChild(del_text.firstChild)
                    for i in range(del_text.attributes.length):
                        attr = del_text.attributes.item(i)
                        t_elem.setAttribute(attr.name, attr.value)
                    del_text.parentNode.replaceChild(t_elem, del_text)

                # 更新运行属性：w:rsidDel → w:rsidR
                if new_run.hasAttribute("w:rsidDel"):
                    new_run.setAttribute("w:rsidR", new_run.getAttribute("w:rsidDel"))
                    new_run.removeAttribute("w:rsidDel")
                elif not new_run.hasAttribute("w:rsidR"):
                    new_run.setAttribute("w:rsidR", self.rsid)

                ins_elem.appendChild(new_run)

            # 将新的插入添加到删除内容之后
            nodes = self.insert_after(del_elem, ins_elem.toxml())

            # 如果处理单个w:del，跟踪创建的插入
            if is_single_del and nodes:
                created_insertion = nodes[0]

        # 根据输入类型返回
        if is_single_del and created_insertion:
            return [elem, created_insertion]
        else:
            return [elem]

    @staticmethod
    def suggest_paragraph(xml_content: str) -> str:
        """转换段落XML以添加用于插入的修订记录包装。

        将run包装在<w:ins>中，并为编号列表在w:pPr的w:rPr中添加<w:ins/>。

        参数:
            xml_content: 包含<w:p>元素的XML字符串

        返回:
            str: 带有修订记录包装的转换后的XML
        """
        wrapper = f'<root xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">{xml_content}</root>'
        doc = minidom.parseString(wrapper)
        para = doc.getElementsByTagName("w:p")[0]

        # 确保w:pPr存在
        pPr_list = para.getElementsByTagName("w:pPr")
        if not pPr_list:
            pPr = doc.createElement("w:pPr")
            para.insertBefore(
                pPr, para.firstChild
            ) if para.firstChild else para.appendChild(pPr)
        else:
            pPr = pPr_list[0]

        # 确保w:pPr中存在w:rPr
        rPr_list = pPr.getElementsByTagName("w:rPr")
        if not rPr_list:
            rPr = doc.createElement("w:rPr")
            pPr.appendChild(rPr)
        else:
            rPr = rPr_list[0]

        # 向w:rPr添加<w:ins/>
        ins_marker = doc.createElement("w:ins")
        rPr.insertBefore(
            ins_marker, rPr.firstChild
        ) if rPr.firstChild else rPr.appendChild(ins_marker)

        # 将所有非pPr子节点包装在<w:ins>中
        ins_wrapper = doc.createElement("w:ins")
        for child in [c for c in para.childNodes if c.nodeName != "w:pPr"]:
            para.removeChild(child)
            ins_wrapper.appendChild(child)
        para.appendChild(ins_wrapper)

        return para.toxml()

    def suggest_deletion(self, elem):
        """使用修订记录标记w:r或w:p元素为已删除（原地DOM操作）。

        对于w:r：包装在<w:del>中，将<w:t>转换为<w:delText>，保留w:rPr
        对于w:p（普通段落）：将内容包装在<w:del>中，将<w:t>转换为<w:delText>
        对于w:p（编号列表）：在w:pPr的w:rPr中添加<w:del/>，将内容包装在<w:del>中

        参数:
            elem: 没有现有修订记录的w:r或w:p DOM元素

        返回:
            Element: 修改后的元素

        异常:
            ValueError: 如果元素已有修订记录或结构无效
        """
        if elem.nodeName == "w:r":
            # 检查是否存在w:delText
            if elem.getElementsByTagName("w:delText"):
                raise ValueError("w:r element already contains w:delText")

            # 转换w:t → w:delText
            for t_elem in list(elem.getElementsByTagName("w:t")):
                del_text = self.dom.createElement("w:delText")
                # 复制所有子节点（不仅仅是firstChild）以处理实体
                while t_elem.firstChild:
                    del_text.appendChild(t_elem.firstChild)
                # 保留xml:space等属性
                for i in range(t_elem.attributes.length):
                    attr = t_elem.attributes.item(i)
                    del_text.setAttribute(attr.name, attr.value)
                t_elem.parentNode.replaceChild(del_text, t_elem)

            # 更新运行属性：w:rsidR → w:rsidDel
            if elem.hasAttribute("w:rsidR"):
                elem.setAttribute("w:rsidDel", elem.getAttribute("w:rsidR"))
                elem.removeAttribute("w:rsidR")
            elif not elem.hasAttribute("w:rsidDel"):
                elem.setAttribute("w:rsidDel", self.rsid)

            # 包装在w:del中
            del_wrapper = self.dom.createElement("w:del")
            parent = elem.parentNode
            parent.insertBefore(del_wrapper, elem)
            parent.removeChild(elem)
            del_wrapper.appendChild(elem)

            # 向删除包装器注入属性
            self._inject_attributes_to_nodes([del_wrapper])

            return del_wrapper

        elif elem.nodeName == "w:p":
            # 检查是否存在现有的修订记录
            if elem.getElementsByTagName("w:ins") or elem.getElementsByTagName("w:del"):
                raise ValueError("w:p element already contains tracked changes")

            # 检查是否是编号列表项
            pPr_list = elem.getElementsByTagName("w:pPr")
            is_numbered = pPr_list and pPr_list[0].getElementsByTagName("w:numPr")

            if is_numbered:
                # 向w:pPr中的w:rPr添加<w:del/>
                pPr = pPr_list[0]
                rPr_list = pPr.getElementsByTagName("w:rPr")

                if not rPr_list:
                    rPr = self.dom.createElement("w:rPr")
                    pPr.appendChild(rPr)
                else:
                    rPr = rPr_list[0]

                # 添加<w:del/>标记
                del_marker = self.dom.createElement("w:del")
                rPr.insertBefore(
                    del_marker, rPr.firstChild
                ) if rPr.firstChild else rPr.appendChild(del_marker)

            # 在所有运行中将w:t → w:delText
            for t_elem in list(elem.getElementsByTagName("w:t")):
                del_text = self.dom.createElement("w:delText")
                # 复制所有子节点（不仅仅是firstChild）以处理实体
                while t_elem.firstChild:
                    del_text.appendChild(t_elem.firstChild)
                # 保留xml:space等属性
                for i in range(t_elem.attributes.length):
                    attr = t_elem.attributes.item(i)
                    del_text.setAttribute(attr.name, attr.value)
                t_elem.parentNode.replaceChild(del_text, t_elem)

            # 更新运行属性：w:rsidR → w:rsidDel
            for run in elem.getElementsByTagName("w:r"):
                if run.hasAttribute("w:rsidR"):
                    run.setAttribute("w:rsidDel", run.getAttribute("w:rsidR"))
                    run.removeAttribute("w:rsidR")
                elif not run.hasAttribute("w:rsidDel"):
                    run.setAttribute("w:rsidDel", self.rsid)

            # 将所有非pPr子节点包装在<w:del>中
            del_wrapper = self.dom.createElement("w:del")
            for child in [c for c in elem.childNodes if c.nodeName != "w:pPr"]:
                elem.removeChild(child)
                del_wrapper.appendChild(child)
            elem.appendChild(del_wrapper)

            # 向删除包装器注入属性
            self._inject_attributes_to_nodes([del_wrapper])

            return elem

        else:
            raise ValueError(f"Element must be w:r or w:p, got {elem.nodeName}")


def _generate_hex_id() -> str:
    """生成用于para/durable ID的随机8字符十六进制ID。

    根据OOXML规范，值必须小于0x7FFFFFFF：
    - paraId必须 < 0x80000000
    - durableId必须 < 0x7FFFFFFF
    我们对两者都使用更严格的约束(0x7FFFFFFF)。
    """
    return f"{random.randint(1, 0x7FFFFFFE):08X}"


def _generate_rsid() -> str:
    """生成随机8字符十六进制RSID（修订保存ID）。"""
    return "".join(random.choices("0123456789ABCDEF", k=8))


class Document:
    """管理已解压Word文档中的注释。"""

    def __init__(
        self,
        unpacked_dir,
        rsid=None,
        track_revisions=False,
        author="Claude",
        initials="C",
    ):
        """
        使用已解压Word文档目录的路径初始化。
        自动设置注释基础设施(people.xml, RSIDs)。

        参数:
            unpacked_dir: 已解压DOCX目录的路径（必须包含word/子目录）
            rsid: 用于所有注释元素的可选RSID。如果未提供，将生成一个。
            track_revisions: 如果为True，在settings.xml中启用修订记录（默认: False）
            author: 注释的默认作者名称（默认: "Claude"）
            initials: 注释的默认作者姓名首字母（默认: "C"）
        """
        self.original_path = Path(unpacked_dir)

        if not self.original_path.exists() or not self.original_path.is_dir():
            raise ValueError(f"Directory not found: {unpacked_dir}")

        # 创建临时目录，包含解压内容和基准的子目录
        self.temp_dir = tempfile.mkdtemp(prefix="docx_")
        self.unpacked_path = Path(self.temp_dir) / "unpacked"
        shutil.copytree(self.original_path, self.unpacked_path)

        # 将原始目录打包为临时.docx用于验证基准（在解压目录外）
        self.original_docx = Path(self.temp_dir) / "original.docx"
        pack_document(self.original_path, self.original_docx, validate=False)

        self.word_path = self.unpacked_path / "word"

        # 如果未提供，生成RSID
        self.rsid = rsid if rsid else _generate_rsid()
        print(f"Using RSID: {self.rsid}")

        # 设置默认作者和姓名首字母
        self.author = author
        self.initials = initials

        # 用于延迟加载编辑器的缓存
        self._editors = {}

        # 注释文件路径
        self.comments_path = self.word_path / "comments.xml"
        self.comments_extended_path = self.word_path / "commentsExtended.xml"
        self.comments_ids_path = self.word_path / "commentsIds.xml"
        self.comments_extensible_path = self.word_path / "commentsExtensible.xml"

        # 加载现有注释并确定下一个ID（在设置修改文件之前）
        self.existing_comments = self._load_existing_comments()
        self.next_comment_id = self._get_next_comment_id()

        # 方便访问document.xml编辑器（半私有）
        self._document = self["word/document.xml"]

        # 设置修订记录基础设施
        self._setup_tracking(track_revisions=track_revisions)

        # 向people.xml添加作者
        self._add_author_to_people(author)

    def __getitem__(self, xml_path: str) -> DocxXMLEditor:
        """
        获取或创建指定XML文件的DocxXMLEditor。

        使用方括号表示法启用延迟加载编辑器：
            node = doc["word/document.xml"].get_node(tag="w:p", line_number=42)

        参数:
            xml_path: XML文件的相对路径（例如，"word/document.xml"，"word/comments.xml"）

        返回:
            指定文件的DocxXMLEditor实例

        异常:
            ValueError: 如果文件不存在

        示例:
            # 从document.xml获取节点
            node = doc["word/document.xml"].get_node(tag="w:del", attrs={"w:id": "1"})

            # 从comments.xml获取节点
            comment = doc["word/comments.xml"].get_node(tag="w:comment", attrs={"w:id": "0"})
        """
        if xml_path not in self._editors:
            file_path = self.unpacked_path / xml_path
            if not file_path.exists():
                raise ValueError(f"XML file not found: {xml_path}")
            # 为所有编辑器使用带有RSID、作者和姓名首字母的DocxXMLEditor
            self._editors[xml_path] = DocxXMLEditor(
                file_path, rsid=self.rsid, author=self.author, initials=self.initials
            )
        return self._editors[xml_path]

    def add_comment(self, start, end, text: str) -> int:
        """
        添加一个从一个元素跨越到另一个元素的注释。

        参数:
            start: 起始点的DOM元素
            end: 结束点的DOM元素
            text: 注释内容

        返回:
            创建的注释ID

        示例:
            start_node = cm.get_document_node(tag="w:del", id="1")
            end_node = cm.get_document_node(tag="w:ins", id="2")
            cm.add_comment(start=start_node, end=end_node, text="解释")
        """
        comment_id = self.next_comment_id
        para_id = _generate_hex_id()
        durable_id = _generate_hex_id()
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # 立即向document.xml添加注释范围
        self._document.insert_before(start, self._comment_range_start_xml(comment_id))

        # 如果结束节点是段落，将注释标记附加在其内部
        # 否则在其后插入（对于运行级锚点）
        if end.tagName == "w:p":
            self._document.append_to(end, self._comment_range_end_xml(comment_id))
        else:
            self._document.insert_after(end, self._comment_range_end_xml(comment_id))

        # 立即添加到comments.xml
        self._add_to_comments_xml(
            comment_id, para_id, text, self.author, self.initials, timestamp
        )

        # 立即添加到commentsExtended.xml
        self._add_to_comments_extended_xml(para_id, parent_para_id=None)

        # 立即添加到commentsIds.xml
        self._add_to_comments_ids_xml(para_id, durable_id)

        # 立即添加到commentsExtensible.xml
        self._add_to_comments_extensible_xml(durable_id)

        # 更新existing_comments以便回复正常工作
        self.existing_comments[comment_id] = {"para_id": para_id}

        self.next_comment_id += 1
        return comment_id

    def reply_to_comment(
        self,
        parent_comment_id: int,
        text: str,
    ) -> int:
        """
        对现有注释添加回复。

        参数:
            parent_comment_id: 要回复的父注释的w:id
            text: 回复文本

        返回:
            为回复创建的注释ID

        示例:
            cm.reply_to_comment(parent_comment_id=0, text="我同意这个变更")
        """
        if parent_comment_id not in self.existing_comments:
            raise ValueError(f"Parent comment with id={parent_comment_id} not found")

        parent_info = self.existing_comments[parent_comment_id]
        comment_id = self.next_comment_id
        para_id = _generate_hex_id()
        durable_id = _generate_hex_id()
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # 立即向document.xml添加注释范围
        parent_start_elem = self._document.get_node(
            tag="w:commentRangeStart", attrs={"w:id": str(parent_comment_id)}
        )
        parent_ref_elem = self._document.get_node(
            tag="w:commentReference", attrs={"w:id": str(parent_comment_id)}
        )

        self._document.insert_after(
            parent_start_elem, self._comment_range_start_xml(comment_id)
        )
        parent_ref_run = parent_ref_elem.parentNode
        self._document.insert_after(
            parent_ref_run, f'<w:commentRangeEnd w:id="{comment_id}"/>'
        )
        self._document.insert_after(
            parent_ref_run, self._comment_ref_run_xml(comment_id)
        )

        # 立即添加到comments.xml
        self._add_to_comments_xml(
            comment_id, para_id, text, self.author, self.initials, timestamp
        )

        # 立即添加到commentsExtended.xml（带有父级）
        self._add_to_comments_extended_xml(
            para_id, parent_para_id=parent_info["para_id"]
        )

        # 立即添加到commentsIds.xml
        self._add_to_comments_ids_xml(para_id, durable_id)

        # 立即添加到commentsExtensible.xml
        self._add_to_comments_extensible_xml(durable_id)

        # 更新existing_comments以便回复正常工作
        self.existing_comments[comment_id] = {"para_id": para_id}

        self.next_comment_id += 1
        return comment_id

    def __del__(self):
        """删除对象时清理临时目录。"""
        if hasattr(self, "temp_dir") and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def validate(self) -> None:
        """
        根据XSD模式和修订记录规则验证文档。

        异常:
            ValueError: 如果验证失败。
        """
        # 使用当前状态创建验证器
        schema_validator = DOCXSchemaValidator(
            self.unpacked_path, self.original_docx, verbose=False
        )
        redlining_validator = RedliningValidator(
            self.unpacked_path, self.original_docx, verbose=False
        )

        # 运行验证
        if not schema_validator.validate():
            raise ValueError("Schema validation failed")
        if not redlining_validator.validate():
            raise ValueError("Redlining validation failed")

    def save(self, destination=None, validate=True) -> None:
        """
        将所有修改的XML文件保存到磁盘并复制到目标目录。

        这会持久化通过add_comment()和reply_to_comment()所做的所有更改。

        参数:
            destination: 保存的可选路径。如果为None，保存回原始目录。
            validate: 如果为True，在保存前验证文档（默认: True）。
        """
        # 仅当注释文件存在时才确保注释关系和内容类型
        if self.comments_path.exists():
            self._ensure_comment_relationships()
            self._ensure_comment_content_types()

        # 将所有修改的XML文件保存到临时目录
        for editor in self._editors.values():
            editor.save()

        # 默认进行验证
        if validate:
            self.validate()

        # 将内容从临时目录复制到目标目录（或原始目录）
        target_path = Path(destination) if destination else self.original_path
        shutil.copytree(self.unpacked_path, target_path, dirs_exist_ok=True)

    # ==================== Private: Initialization ====================

    def _get_next_comment_id(self):
        """获取下一个可用的注释ID。"""
        if not self.comments_path.exists():
            return 0

        editor = self["word/comments.xml"]
        max_id = -1
        for comment_elem in editor.dom.getElementsByTagName("w:comment"):
            comment_id = comment_elem.getAttribute("w:id")
            if comment_id:
                try:
                    max_id = max(max_id, int(comment_id))
                except ValueError:
                    pass
        return max_id + 1

    def _load_existing_comments(self):
        """从文件加载现有注释以启用回复功能。"""
        if not self.comments_path.exists():
            return {}

        editor = self["word/comments.xml"]
        existing = {}

        for comment_elem in editor.dom.getElementsByTagName("w:comment"):
            comment_id = comment_elem.getAttribute("w:id")
            if not comment_id:
                continue

            # 从注释内的w:p元素中查找para_id
            para_id = None
            for p_elem in comment_elem.getElementsByTagName("w:p"):
                para_id = p_elem.getAttribute("w14:paraId")
                if para_id:
                    break

            if not para_id:
                continue

            existing[int(comment_id)] = {"para_id": para_id}

        return existing

    # ==================== Private: Setup Methods ====================

    def _setup_tracking(self, track_revisions=False):
        """在已解压目录中设置注释基础设施。

        参数:
            track_revisions: 如果为True，在settings.xml中启用修订记录
        """
        # 创建或更新word/people.xml
        people_file = self.word_path / "people.xml"
        self._update_people_xml(people_file)

        # 更新XML文件
        self._add_content_type_for_people(self.unpacked_path / "[Content_Types].xml")
        self._add_relationship_for_people(
            self.word_path / "_rels" / "document.xml.rels"
        )

        # 始终向settings.xml添加RSID，可选启用trackRevisions
        self._update_settings(
            self.word_path / "settings.xml", track_revisions=track_revisions
        )

    def _update_people_xml(self, path):
        """如果people.xml不存在则创建它。"""
        if not path.exists():
            # 从模板复制
            shutil.copy(TEMPLATE_DIR / "people.xml", path)

    def _add_content_type_for_people(self, path):
        """如果尚未存在，将people.xml内容类型添加到[Content_Types].xml。"""
        editor = self["[Content_Types].xml"]

        if self._has_override(editor, "/word/people.xml"):
            return

        # 添加Override元素
        root = editor.dom.documentElement
        override_xml = '<Override PartName="/word/people.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.people+xml"/>'
        editor.append_to(root, override_xml)

    def _add_relationship_for_people(self, path):
        """如果尚未存在，将people.xml关系添加到document.xml.rels。"""
        editor = self["word/_rels/document.xml.rels"]

        if self._has_relationship(editor, "people.xml"):
            return

        root = editor.dom.documentElement
        root_tag = root.tagName  # type: ignore
        prefix = root_tag.split(":")[0] + ":" if ":" in root_tag else ""
        next_rid = editor.get_next_rid()

        # 创建关系条目
        rel_xml = f'<{prefix}Relationship Id="{next_rid}" Type="http://schemas.microsoft.com/office/2011/relationships/people" Target="people.xml"/>'
        editor.append_to(root, rel_xml)

    def _update_settings(self, path, track_revisions=False):
        """在settings.xml中添加RSID并可选地启用修订记录。

        参数:
            path: settings.xml的路径
            track_revisions: 如果为True，添加trackRevisions元素

        按照OOXML模式顺序放置元素：
        - trackRevisions: 早期（在defaultTabStop之前）
        - rsids: 晚期（在compat之后）
        """
        editor = self["word/settings.xml"]
        root = editor.get_node(tag="w:settings")
        prefix = root.tagName.split(":")[0] if ":" in root.tagName else "w"

        # 根据请求有条件地添加trackRevisions
        if track_revisions:
            track_revisions_exists = any(
                elem.tagName == f"{prefix}:trackRevisions"
                for elem in editor.dom.getElementsByTagName(f"{prefix}:trackRevisions")
            )

            if not track_revisions_exists:
                track_rev_xml = f"<{prefix}:trackRevisions/>"
                # 尝试在documentProtection、defaultTabStop之前或开始处插入
                inserted = False
                for tag in [f"{prefix}:documentProtection", f"{prefix}:defaultTabStop"]:
                    elements = editor.dom.getElementsByTagName(tag)
                    if elements:
                        editor.insert_before(elements[0], track_rev_xml)
                        inserted = True
                        break
                if not inserted:
                    # 作为settings的第一个子节点插入
                    if root.firstChild:
                        editor.insert_before(root.firstChild, track_rev_xml)
                    else:
                        editor.append_to(root, track_rev_xml)

        # 始终检查rsids部分是否存在
        rsids_elements = editor.dom.getElementsByTagName(f"{prefix}:rsids")

        if not rsids_elements:
            # 添加新的rsids部分
            rsids_xml = f'''<{prefix}:rsids>
  <{prefix}:rsidRoot {prefix}:val="{self.rsid}"/>
  <{prefix}:rsid {prefix}:val="{self.rsid}"/>
</{prefix}:rsids>'''

            # 尝试在compat之后、clrSchemeMapping之前或结束标签之前插入
            inserted = False
            compat_elements = editor.dom.getElementsByTagName(f"{prefix}:compat")
            if compat_elements:
                editor.insert_after(compat_elements[0], rsids_xml)
                inserted = True

            if not inserted:
                clr_elements = editor.dom.getElementsByTagName(
                    f"{prefix}:clrSchemeMapping"
                )
                if clr_elements:
                    editor.insert_before(clr_elements[0], rsids_xml)
                    inserted = True

            if not inserted:
                editor.append_to(root, rsids_xml)
        else:
            # 检查此rsid是否已存在
            rsids_elem = rsids_elements[0]
            rsid_exists = any(
                elem.getAttribute(f"{prefix}:val") == self.rsid
                for elem in rsids_elem.getElementsByTagName(f"{prefix}:rsid")
            )

            if not rsid_exists:
                rsid_xml = f'<{prefix}:rsid {prefix}:val="{self.rsid}"/>'
                editor.append_to(rsids_elem, rsid_xml)

    # ==================== Private: XML File Creation ====================

    def _add_to_comments_xml(
        self, comment_id, para_id, text, author, initials, timestamp
    ):
        """将单个注释添加到comments.xml。"""
        if not self.comments_path.exists():
            shutil.copy(TEMPLATE_DIR / "comments.xml", self.comments_path)

        editor = self["word/comments.xml"]
        root = editor.get_node(tag="w:comments")

        escaped_text = (
            text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )
        # 注意：w:p上的w:rsidR、w:rsidRDefault、w:rsidP，w:r上的w:rsidR,
        # and w:author, w:date, w:initials on w:comment are automatically added by DocxXMLEditor
        comment_xml = f'''<w:comment w:id="{comment_id}">
  <w:p w14:paraId="{para_id}" w14:textId="77777777">
    <w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:annotationRef/></w:r>
    <w:r><w:rPr><w:color w:val="000000"/><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr><w:t>{escaped_text}</w:t></w:r>
  </w:p>
</w:comment>'''
        editor.append_to(root, comment_xml)

    def _add_to_comments_extended_xml(self, para_id, parent_para_id):
        """将单个注释添加到commentsExtended.xml。"""
        if not self.comments_extended_path.exists():
            shutil.copy(
                TEMPLATE_DIR / "commentsExtended.xml", self.comments_extended_path
            )

        editor = self["word/commentsExtended.xml"]
        root = editor.get_node(tag="w15:commentsEx")

        if parent_para_id:
            xml = f'<w15:commentEx w15:paraId="{para_id}" w15:paraIdParent="{parent_para_id}" w15:done="0"/>'
        else:
            xml = f'<w15:commentEx w15:paraId="{para_id}" w15:done="0"/>'
        editor.append_to(root, xml)

    def _add_to_comments_ids_xml(self, para_id, durable_id):
        """将单个注释添加到commentsIds.xml。"""
        if not self.comments_ids_path.exists():
            shutil.copy(TEMPLATE_DIR / "commentsIds.xml", self.comments_ids_path)

        editor = self["word/commentsIds.xml"]
        root = editor.get_node(tag="w16cid:commentsIds")

        xml = f'<w16cid:commentId w16cid:paraId="{para_id}" w16cid:durableId="{durable_id}"/>'
        editor.append_to(root, xml)

    def _add_to_comments_extensible_xml(self, durable_id):
        """将单个注释添加到commentsExtensible.xml。"""
        if not self.comments_extensible_path.exists():
            shutil.copy(
                TEMPLATE_DIR / "commentsExtensible.xml", self.comments_extensible_path
            )

        editor = self["word/commentsExtensible.xml"]
        root = editor.get_node(tag="w16cex:commentsExtensible")

        xml = f'<w16cex:commentExtensible w16cex:durableId="{durable_id}"/>'
        editor.append_to(root, xml)

    # ==================== Private: XML Fragments ====================

    def _comment_range_start_xml(self, comment_id):
        """生成注释范围开始的XML。"""
        return f'<w:commentRangeStart w:id="{comment_id}"/>'

    def _comment_range_end_xml(self, comment_id):
        """生成带有引用运行的注释范围结束XML。

        注意：w:rsidR由DocxXMLEditor自动添加。
        """
        return f'''<w:commentRangeEnd w:id="{comment_id}"/>
<w:r>
  <w:rPr><w:rStyle w:val="CommentReference"/></w:rPr>
  <w:commentReference w:id="{comment_id}"/>
</w:r>'''

    def _comment_ref_run_xml(self, comment_id):
        """生成注释引用运行的XML。

        注意：w:rsidR由DocxXMLEditor自动添加。
        """
        return f'''<w:r>
  <w:rPr><w:rStyle w:val="CommentReference"/></w:rPr>
  <w:commentReference w:id="{comment_id}"/>
</w:r>'''

    # ==================== Private: Metadata Updates ====================

    def _has_relationship(self, editor, target):
        """检查是否存在具有给定目标的关系。"""
        for rel_elem in editor.dom.getElementsByTagName("Relationship"):
            if rel_elem.getAttribute("Target") == target:
                return True
        return False

    def _has_override(self, editor, part_name):
        """检查是否存在具有给定部件名称的覆盖。"""
        for override_elem in editor.dom.getElementsByTagName("Override"):
            if override_elem.getAttribute("PartName") == part_name:
                return True
        return False

    def _has_author(self, editor, author):
        """检查作者是否已存在于people.xml中。"""
        for person_elem in editor.dom.getElementsByTagName("w15:person"):
            if person_elem.getAttribute("w15:author") == author:
                return True
        return False

    def _add_author_to_people(self, author):
        """将作者添加到people.xml（初始化时调用）。"""
        people_path = self.word_path / "people.xml"

        # people.xml should already exist from _setup_tracking
        if not people_path.exists():
            raise ValueError("people.xml should exist after _setup_tracking")

        editor = self["word/people.xml"]
        root = editor.get_node(tag="w15:people")

        # 检查作者是否已存在
        if self._has_author(editor, author):
            return

        # 使用适当的XML转义添加作者以防止注入
        escaped_author = html.escape(author, quote=True)
        person_xml = f'''<w15:person w15:author="{escaped_author}">
  <w15:presenceInfo w15:providerId="None" w15:userId="{escaped_author}"/>
</w15:person>'''
        editor.append_to(root, person_xml)

    def _ensure_comment_relationships(self):
        """确保word/_rels/document.xml.rels包含注释关系。"""
        editor = self["word/_rels/document.xml.rels"]

        if self._has_relationship(editor, "comments.xml"):
            return

        root = editor.dom.documentElement
        root_tag = root.tagName  # type: ignore
        prefix = root_tag.split(":")[0] + ":" if ":" in root_tag else ""
        next_rid_num = int(editor.get_next_rid()[3:])

        # 添加关系元素
        rels = [
            (
                next_rid_num,
                "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments",
                "comments.xml",
            ),
            (
                next_rid_num + 1,
                "http://schemas.microsoft.com/office/2011/relationships/commentsExtended",
                "commentsExtended.xml",
            ),
            (
                next_rid_num + 2,
                "http://schemas.microsoft.com/office/2016/09/relationships/commentsIds",
                "commentsIds.xml",
            ),
            (
                next_rid_num + 3,
                "http://schemas.microsoft.com/office/2018/08/relationships/commentsExtensible",
                "commentsExtensible.xml",
            ),
        ]

        for rel_id, rel_type, target in rels:
            rel_xml = f'<{prefix}Relationship Id="rId{rel_id}" Type="{rel_type}" Target="{target}"/>'
            editor.append_to(root, rel_xml)

    def _ensure_comment_content_types(self):
        """确保[Content_Types].xml包含注释内容类型。"""
        editor = self["[Content_Types].xml"]

        if self._has_override(editor, "/word/comments.xml"):
            return

        root = editor.dom.documentElement

        # 添加Override元素
        overrides = [
            (
                "/word/comments.xml",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml",
            ),
            (
                "/word/commentsExtended.xml",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.commentsExtended+xml",
            ),
            (
                "/word/commentsIds.xml",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.commentsIds+xml",
            ),
            (
                "/word/commentsExtensible.xml",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.commentsExtensible+xml",
            ),
        ]

        for part_name, content_type in overrides:
            override_xml = (
                f'<Override PartName="{part_name}" ContentType="{content_type}"/>'
            )
            editor.append_to(root, override_xml)
