"""
用于验证Word文档XML文件是否符合XSD模式的验证器。
"""

import re
import tempfile
import zipfile

import lxml.etree

from .base import BaseSchemaValidator


class DOCXSchemaValidator(BaseSchemaValidator):
    """用于验证Word文档XML文件是否符合XSD模式的验证器。"""

    # Word特定的命名空间
    WORD_2006_NAMESPACE = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

    # Word特定的元素到关系类型的映射
    # 初始化为空映射 - 随着发现新情况添加特定案例
    ELEMENT_RELATIONSHIP_TYPES = {}

    def validate(self):
        """运行所有验证检查，如果全部通过则返回True。"""
        # 测试0：XML格式良好性
        if not self.validate_xml():
            return False

        # 测试1：命名空间声明
        all_valid = True
        if not self.validate_namespaces():
            all_valid = False

        # 测试2：唯一ID
        if not self.validate_unique_ids():
            all_valid = False

        # 测试3：关系和文件引用验证
        if not self.validate_file_references():
            all_valid = False

        # 测试4：内容类型声明
        if not self.validate_content_types():
            all_valid = False

        # 测试5：XSD模式验证
        if not self.validate_against_xsd():
            all_valid = False

        # 测试6：空白字符保留
        if not self.validate_whitespace_preservation():
            all_valid = False

        # 测试7：删除验证
        if not self.validate_deletions():
            all_valid = False

        # 测试8：插入验证
        if not self.validate_insertions():
            all_valid = False

        # 测试9：关系ID引用验证
        if not self.validate_all_relationship_ids():
            all_valid = False

        # 计算并比较段落数
        self.compare_paragraph_counts()

        return all_valid

    def validate_whitespace_preservation(self):
        """
        验证带有空白字符的w:t元素是否设置了xml:space='preserve'属性。
        """
        errors = []

        for xml_file in self.xml_files:
            # 仅检查document.xml文件
            if xml_file.name != "document.xml":
                continue

            try:
                root = lxml.etree.parse(str(xml_file)).getroot()

                # Find all w:t elements
                for elem in root.iter(f"{{{self.WORD_2006_NAMESPACE}}}t"):
                    if elem.text:
                        text = elem.text
                        # 检查文本是否以空白字符开头或结尾
                        if re.match(r"^\s.*", text) or re.match(r".*\s$", text):
                            # 检查是否存在xml:space="preserve"属性
                            xml_space_attr = f"{{{self.XML_NAMESPACE}}}space"
                            if (
                                xml_space_attr not in elem.attrib
                                or elem.attrib[xml_space_attr] != "preserve"
                            ):
                                # 显示文本预览
                                text_preview = (
                                    repr(text)[:50] + "..."
                                    if len(repr(text)) > 50
                                    else repr(text)
                                )
                                errors.append(
                                    f"  {xml_file.relative_to(self.unpacked_dir)}: "
                                    f"Line {elem.sourceline}: w:t element with whitespace missing xml:space='preserve': {text_preview}"
                                )

            except (lxml.etree.XMLSyntaxError, Exception) as e:
                errors.append(
                    f"  {xml_file.relative_to(self.unpacked_dir)}: Error: {e}"
                )

        if errors:
            print(f"失败 - 发现{len(errors)}个空白字符保留违规：")
            for error in errors:
                print(error)
            return False
        else:
            if self.verbose:
                print("通过 - 所有空白字符都被正确保留")
            return True

    def validate_deletions(self):
        """
        验证w:t元素不在w:del元素内。
        由于某些原因，XSD验证无法捕获此问题，因此我们手动进行验证。
        """
        errors = []

        for xml_file in self.xml_files:
            # Only check document.xml files
            if xml_file.name != "document.xml":
                continue

            try:
                root = lxml.etree.parse(str(xml_file)).getroot()

                # 查找所有作为w:del元素后代的w:t元素
                namespaces = {"w": self.WORD_2006_NAMESPACE}
                xpath_expression = ".//w:del//w:t"
                problematic_t_elements = root.xpath(
                    xpath_expression, namespaces=namespaces
                )
                for t_elem in problematic_t_elements:
                    if t_elem.text:
                        # Show a preview of the text
                        text_preview = (
                            repr(t_elem.text)[:50] + "..."
                            if len(repr(t_elem.text)) > 50
                            else repr(t_elem.text)
                        )
                        errors.append(
                            f"  {xml_file.relative_to(self.unpacked_dir)}: "
                            f"Line {t_elem.sourceline}: <w:t> found within <w:del>: {text_preview}"
                        )

            except (lxml.etree.XMLSyntaxError, Exception) as e:
                errors.append(
                    f"  {xml_file.relative_to(self.unpacked_dir)}: Error: {e}"
                )

        if errors:
            print(f"失败 - 发现{len(errors)}个删除验证违规：")
            for error in errors:
                print(error)
            return False
        else:
            if self.verbose:
                print("通过 - 未在w:del元素内发现w:t元素")
            return True

    def count_paragraphs_in_unpacked(self):
        """计算解压文档中的段落数量。"""
        count = 0

        for xml_file in self.xml_files:
            # Only check document.xml files
            if xml_file.name != "document.xml":
                continue

            try:
                root = lxml.etree.parse(str(xml_file)).getroot()
                # 计算所有w:p元素
                paragraphs = root.findall(f".//{{{self.WORD_2006_NAMESPACE}}}p")
                count = len(paragraphs)
            except Exception as e:
                print(f"Error counting paragraphs in unpacked document: {e}")

        return count

    def count_paragraphs_in_original(self):
        """计算原始docx文件中的段落数量。"""
        count = 0

        try:
            # 创建临时目录来解压原始文件
            with tempfile.TemporaryDirectory() as temp_dir:
                # 解压原始docx
                with zipfile.ZipFile(self.original_file, "r") as zip_ref:
                    zip_ref.extractall(temp_dir)

                # 解析document.xml
                doc_xml_path = temp_dir + "/word/document.xml"
                root = lxml.etree.parse(doc_xml_path).getroot()

                # Count all w:p elements
                paragraphs = root.findall(f".//{{{self.WORD_2006_NAMESPACE}}}p")
                count = len(paragraphs)

        except Exception as e:
            print(f"Error counting paragraphs in original document: {e}")

        return count

    def validate_insertions(self):
        """
        验证w:delText元素不在w:ins元素内。
        只有当w:delText嵌套在w:del元素内时，才允许其出现在w:ins元素中。
        """
        errors = []

        for xml_file in self.xml_files:
            if xml_file.name != "document.xml":
                continue

            try:
                root = lxml.etree.parse(str(xml_file)).getroot()
                namespaces = {"w": self.WORD_2006_NAMESPACE}

                # 查找不在w:del内的w:ins中的w:delText元素
                invalid_elements = root.xpath(
                    ".//w:ins//w:delText[not(ancestor::w:del)]",
                    namespaces=namespaces
                )

                for elem in invalid_elements:
                    text_preview = (
                        repr(elem.text or "")[:50] + "..."
                        if len(repr(elem.text or "")) > 50
                        else repr(elem.text or "")
                    )
                    errors.append(
                        f"  {xml_file.relative_to(self.unpacked_dir)}: "
                        f"Line {elem.sourceline}: <w:delText> within <w:ins>: {text_preview}"
                    )

            except (lxml.etree.XMLSyntaxError, Exception) as e:
                errors.append(
                    f"  {xml_file.relative_to(self.unpacked_dir)}: Error: {e}"
                )

        if errors:
            print(f"失败 - 发现{len(errors)}个插入验证违规：")
            for error in errors:
                print(error)
            return False
        else:
            if self.verbose:
                print("通过 - 未在w:ins元素内发现w:delText元素")
            return True

    def compare_paragraph_counts(self):
        """比较原始文档和新文档之间的段落数量。"""
        original_count = self.count_paragraphs_in_original()
        new_count = self.count_paragraphs_in_unpacked()

        diff = new_count - original_count
        diff_str = f"+{diff}" if diff > 0 else str(diff)
        print(f"\n段落数: {original_count} → {new_count} ({diff_str})")


if __name__ == "__main__":
    raise RuntimeError("This module should not be run directly.")
