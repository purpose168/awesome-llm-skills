#!/usr/bin/env python3
"""
用于编辑OOXML文档的工具。

本模块提供XMLEditor，这是一个用于操作XML文件的工具，支持基于行号的节点查找和DOM操作。
在解析过程中，每个元素都会自动标注其在原始文件中的行号和列位置。

使用示例：
    editor = XMLEditor("document.xml")

    # 按行号或行范围查找节点
    elem = editor.get_node(tag="w:r", line_number=519)
    elem = editor.get_node(tag="w:p", line_number=range(100, 200))

    # 按文本内容查找节点
    elem = editor.get_node(tag="w:p", contains="specific text")

    # 按属性查找节点
    elem = editor.get_node(tag="w:r", attrs={"w:id": "target"})

    # 组合过滤器
    elem = editor.get_node(tag="w:p", line_number=range(1, 50), contains="text")

    # 替换、插入或操作节点
    new_elem = editor.replace_node(elem, "<w:r><w:t>new text</w:t></w:r>")
    editor.insert_after(new_elem, "<w:r><w:t>more</w:t></w:r>")

    # 保存更改
    editor.save()
"""

import html
from pathlib import Path
from typing import Optional, Union

import defusedxml.minidom
import defusedxml.sax


class XMLEditor:
    """
    用于操作OOXML XML文件的编辑器，支持基于行号的节点查找。

    该类解析XML文件并跟踪每个元素在原始文件中的行号和列位置。
    这使得可以通过原始文件中的行号查找节点，在使用Read工具输出时非常有用。

    属性：
        xml_path: 正在编辑的XML文件路径
        encoding: 检测到的XML文件编码（'ascii'或'utf-8'）
        dom: 解析后的DOM树，元素上带有parse_position属性
    """

    def __init__(self, xml_path):
        """
        使用XML文件路径初始化并使用行号跟踪进行解析。

        参数：
            xml_path: 要编辑的XML文件路径（str或Path）

        异常：
            ValueError: 如果XML文件不存在
        """
        self.xml_path = Path(xml_path)
        if not self.xml_path.exists():
            raise ValueError(f"未找到XML文件: {xml_path}")

        with open(self.xml_path, "rb") as f:
            header = f.read(200).decode("utf-8", errors="ignore")
        self.encoding = "ascii" if 'encoding="ascii"' in header else "utf-8"

        parser = _create_line_tracking_parser()
        self.dom = defusedxml.minidom.parse(str(self.xml_path), parser)

    def get_node(
        self,
        tag: str,
        attrs: Optional[dict[str, str]] = None,
        line_number: Optional[Union[int, range]] = None,
        contains: Optional[str] = None,
    ):
        """
        通过标签和标识符获取DOM元素。

        通过原始文件中的行号或匹配属性值查找元素。必须找到且只找到一个匹配项。

        参数：
            tag: XML标签名称（例如："w:del", "w:ins", "w:r"）
            attrs: 要匹配的属性名值对字典（例如：{"w:id": "1"}）
            line_number: 原始XML文件中的行号（int）或行范围（range）（从1开始索引）
            contains: 必须出现在元素内任何文本节点中的文本字符串。
                      同时支持实体表示法（&#8220;）和Unicode字符（\u201c）。

        返回：
            defusedxml.minidom.Element: 匹配的DOM元素

        异常：
            ValueError: 如果节点未找到或找到多个匹配项

        示例：
            elem = editor.get_node(tag="w:r", line_number=519)
            elem = editor.get_node(tag="w:r", line_number=range(100, 200))
            elem = editor.get_node(tag="w:del", attrs={"w:id": "1"})
            elem = editor.get_node(tag="w:p", attrs={"w14:paraId": "12345678"})
            elem = editor.get_node(tag="w:commentRangeStart", attrs={"w:id": "0"})
            elem = editor.get_node(tag="w:p", contains="特定文本")
            elem = editor.get_node(tag="w:t", contains="&#8220;协议")  # 实体表示法
            elem = editor.get_node(tag="w:t", contains="\u201c协议")   # Unicode字符
        """
        matches = []
        for elem in self.dom.getElementsByTagName(tag):
            # 检查行号过滤器
            if line_number is not None:
                parse_pos = getattr(elem, "parse_position", (None,))
                elem_line = parse_pos[0]

                # 处理单行号和行范围
                if isinstance(line_number, range):
                    if elem_line not in line_number:
                        continue
                else:
                    if elem_line != line_number:
                        continue

            # 检查属性过滤器
            if attrs is not None:
                if not all(
                    elem.getAttribute(attr_name) == attr_value
                    for attr_name, attr_value in attrs.items()
                ):
                    continue

            # 检查文本内容过滤器
            if contains is not None:
                elem_text = self._get_element_text(elem)
                # 规范化搜索字符串：将HTML实体转换为Unicode字符
                # 这允许同时搜索"&#8220;Rowan"和"Rowan"
                normalized_contains = html.unescape(contains)
                if normalized_contains not in elem_text:
                    continue

            # 如果所有适用的过滤器都通过，则匹配成功
            matches.append(elem)

        if not matches:
            # 构建描述性错误消息
            filters = []
            if line_number is not None:
                line_str = (
                    f"lines {line_number.start}-{line_number.stop - 1}"
                    if isinstance(line_number, range)
                    else f"line {line_number}"
                )
                filters.append(f"at {line_str}")
            if attrs is not None:
                filters.append(f"with attributes {attrs}")
            if contains is not None:
                filters.append(f"containing '{contains}'")

            filter_desc = " ".join(filters) if filters else ""
            base_msg = f"未找到节点: <{tag}> {filter_desc}".strip()

            # 根据使用的过滤器添加有用提示
            if contains:
                hint = "文本可能跨多个元素分割或使用不同措辞。"
            elif line_number:
                hint = "如果文档已修改，行号可能已更改。"
            elif attrs:
                hint = "请验证属性值是否正确。"
            else:
                hint = "尝试添加过滤器（attrs、line_number或contains）。"

            raise ValueError(f"{base_msg}. {hint}")
        if len(matches) > 1:
            raise ValueError(
                f"找到多个节点: <{tag}>. "
                f"请添加更多过滤器（attrs、line_number或contains）以缩小搜索范围。"
            )
        return matches[0]

    def _get_element_text(self, elem):
        """
        递归提取元素中的所有文本内容。

        跳过仅包含空白字符（空格、制表符、换行符）的文本节点，
        这些通常代表XML格式而非文档内容。

        参数：
            elem: 要提取文本的defusedxml.minidom.Element

        返回：
            str: 元素内所有非空白文本节点的连接文本
        """
        text_parts = []
        for node in elem.childNodes:
            if node.nodeType == node.TEXT_NODE:
                # 跳过仅包含空白字符的文本节点（XML格式）
                if node.data.strip():
                    text_parts.append(node.data)
            elif node.nodeType == node.ELEMENT_NODE:
                text_parts.append(self._get_element_text(node))
        return "".join(text_parts)

    def replace_node(self, elem, new_content):
        """
        用新的XML内容替换DOM元素。

        参数：
            elem: 要替换的defusedxml.minidom.Element
            new_content: 包含用于替换节点的XML的字符串

        返回：
            List[defusedxml.minidom.Node]: 所有插入的节点

        示例：
            new_nodes = editor.replace_node(old_elem, "<w:r><w:t>文本</w:t></w:r>")
        """
        parent = elem.parentNode
        nodes = self._parse_fragment(new_content)
        for node in nodes:
            parent.insertBefore(node, elem)
        parent.removeChild(elem)
        return nodes

    def insert_after(self, elem, xml_content):
        """
        在DOM元素后插入XML内容。

        参数：
            elem: 要在其后插入的defusedxml.minidom.Element
            xml_content: 包含要插入的XML的字符串

        返回：
            List[defusedxml.minidom.Node]: 所有插入的节点

        示例：
            new_nodes = editor.insert_after(elem, "<w:r><w:t>文本</w:t></w:r>")
        """
        parent = elem.parentNode
        next_sibling = elem.nextSibling
        nodes = self._parse_fragment(xml_content)
        for node in nodes:
            if next_sibling:
                parent.insertBefore(node, next_sibling)
            else:
                parent.appendChild(node)
        return nodes

    def insert_before(self, elem, xml_content):
        """
        在DOM元素前插入XML内容。

        参数：
            elem: 要在其前插入的defusedxml.minidom.Element
            xml_content: 包含要插入的XML的字符串

        返回：
            List[defusedxml.minidom.Node]: 所有插入的节点

        示例：
            new_nodes = editor.insert_before(elem, "<w:r><w:t>文本</w:t></w:r>")
        """
        parent = elem.parentNode
        nodes = self._parse_fragment(xml_content)
        for node in nodes:
            parent.insertBefore(node, elem)
        return nodes

    def append_to(self, elem, xml_content):
        """
        将XML内容作为DOM元素的子节点追加。

        参数：
            elem: 要追加到的defusedxml.minidom.Element
            xml_content: 包含要追加的XML的字符串

        返回：
            List[defusedxml.minidom.Node]: 所有插入的节点

        示例：
            new_nodes = editor.append_to(elem, "<w:r><w:t>文本</w:t></w:r>")
        """
        nodes = self._parse_fragment(xml_content)
        for node in nodes:
            elem.appendChild(node)
        return nodes

    def get_next_rid(self):
        """获取关系文件的下一个可用rId。"""
        max_id = 0
        for rel_elem in self.dom.getElementsByTagName("Relationship"):
            rel_id = rel_elem.getAttribute("Id")
            if rel_id.startswith("rId"):
                try:
                    max_id = max(max_id, int(rel_id[3:]))
                except ValueError:
                    pass
        return f"rId{max_id + 1}"

    def save(self):
        """
        将编辑后的XML保存回文件。

        序列化DOM树并将其写回原始文件路径，
        保留原始编码（ascii或utf-8）。
        """
        content = self.dom.toxml(encoding=self.encoding)
        self.xml_path.write_bytes(content)

    def _parse_fragment(self, xml_content):
        """
        解析XML片段并返回导入节点的列表。

        参数：
            xml_content: 包含XML片段的字符串

        返回：
            导入到该文档中的defusedxml.minidom.Node对象列表

        异常：
            AssertionError: 如果片段不包含任何元素节点
        """
        # 从根文档元素提取命名空间声明
        root_elem = self.dom.documentElement
        namespaces = []
        if root_elem and root_elem.attributes:
            for i in range(root_elem.attributes.length):
                attr = root_elem.attributes.item(i)
                if attr.name.startswith("xmlns"):  # type: ignore
                    namespaces.append(f'{attr.name}="{attr.value}"')  # type: ignore

        ns_decl = " ".join(namespaces)
        wrapper = f"<root {ns_decl}>{xml_content}</root>"
        fragment_doc = defusedxml.minidom.parseString(wrapper)
        nodes = [
            self.dom.importNode(child, deep=True)
            for child in fragment_doc.documentElement.childNodes  # type: ignore
        ]
        elements = [n for n in nodes if n.nodeType == n.ELEMENT_NODE]
        assert elements, "片段必须包含至少一个元素"
        return nodes


def _create_line_tracking_parser():
    """
    创建一个跟踪每个元素行号和列号的SAX解析器。

    猴子补丁SAX内容处理程序，将当前行和列位置
    从底层expat解析器存储到每个元素上，作为parse_position
    属性（行，列）元组。

    返回：
        defusedxml.sax.xmlreader.XMLReader: 配置好的SAX解析器
    """

    def set_content_handler(dom_handler):
        def startElementNS(name, tagName, attrs):
            orig_start_cb(name, tagName, attrs)
            cur_elem = dom_handler.elementStack[-1]
            cur_elem.parse_position = (
                parser._parser.CurrentLineNumber,  # type: ignore
                parser._parser.CurrentColumnNumber,  # type: ignore
            )

        orig_start_cb = dom_handler.startElementNS
        dom_handler.startElementNS = startElementNS
        orig_set_content_handler(dom_handler)

    parser = defusedxml.sax.make_parser()
    orig_set_content_handler = parser.setContentHandler
    parser.setContentHandler = set_content_handler  # type: ignore
    return parser
