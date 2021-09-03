# Copyright (C) 2019-2021, TomTom (http://tomtom.com).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Test parsing brief and detailed descriptions from Doxygen XML."""

import xml.etree.ElementTree as ET

from asciidoxy.parser.doxygen.description_parser_v2 import (DescriptionElement,
                                                            NestedDescriptionElement,
                                                            parse_description)


def debug_print(element: DescriptionElement, prefix: str = "") -> None:
    print(f"{prefix}{repr(element)}")
    if isinstance(element, NestedDescriptionElement):
        for child in element.contents:
            debug_print(child, f"{prefix}  ")


def parse(input_xml):
    output = parse_description(ET.fromstring(input_xml))
    debug_print(output)
    return output


def test_parse_styles():
    input_xml = """\
        <detaileddescription>
<para>Description with all kinds of Doxygen styles.</para>
<para>Several <emphasis>words</emphasis> in this <emphasis>sentence</emphasis> are <emphasis>italic</emphasis>.</para>
<para>Several <bold>words</bold> in this <bold>sentence</bold> are <bold>bold</bold>.</para>
<para>Also a <computeroutput>some</computeroutput> words in <computeroutput>monotype</computeroutput>. </para>
        </detaileddescription>
"""
    output = parse(input_xml)
    assert output.to_asciidoc() == """\
Description with all kinds of Doxygen styles.

Several __words__ in this __sentence__ are __italic__.

Several **words** in this **sentence** are **bold**.

Also a ``some`` words in ``monotype``."""


def test_parse_lists():
    input_xml = """\
    <detaileddescription>
<para>Description with some Doxygen lists.</para>
<para><itemizedlist>
<listitem><para><computeroutput>AlignLeft</computeroutput> left alignment. </para>
</listitem>
<listitem><para><computeroutput>AlignCenter</computeroutput> center alignment. </para>
</listitem>
<listitem><para><computeroutput>AlignRight</computeroutput> right alignment</para>
</listitem>
</itemizedlist>
Another list:</para>
<para><itemizedlist>
<listitem><para><bold>Bold</bold>. </para>
</listitem>
<listitem><para><emphasis>Italic</emphasis>. </para>
</listitem>
<listitem><para><computeroutput>Monotype</computeroutput>. </para>
</listitem>
</itemizedlist>
</para>
    </detaileddescription>
"""
    output = parse(input_xml)
    assert output.to_asciidoc() == """\
Description with some Doxygen lists.

* ``AlignLeft`` left alignment.

* ``AlignCenter`` center alignment.

* ``AlignRight`` right alignment

Another list:

* **Bold**.

* __Italic__.

* ``Monotype``."""


def test_parse_code_blocks():
    input_xml = """\
    <detaileddescription>
<para>Description with some code blocks.</para>
<para>Python example:</para>
<para><programlisting filename=".py"><codeline><highlight class="normal">class<sp/>Python:</highlight></codeline>
<codeline><highlight class="normal"><sp/><sp/><sp/><sp/></highlight><highlight class="keywordflow">pass</highlight></codeline>
</programlisting></para>
<para>C++ example:</para>
<para><programlisting filename=".cpp"><codeline><highlight class="keyword">class<sp/></highlight><highlight class="normal">Cpp<sp/>{};</highlight></codeline>
</programlisting></para>
<para>Unparsed code:</para>
<para><programlisting filename=".unparsed"><codeline><highlight class="normal">Show<sp/>this<sp/>as-is<sp/>please</highlight></codeline>
</programlisting></para>
<para>That&apos;s all folks! </para>
    </detaileddescription>
"""
    output = parse(input_xml)
    assert output.to_asciidoc() == """\
Description with some code blocks.

Python example:

[source]
----
class Python:
    pass
----

C++ example:

[source]
----
class Cpp {};
----

Unparsed code:

[source]
----
Show this as-is please
----

That's all folks!"""


def test_parse_diagrams():
    input_xml = """\
    <detaileddescription>
<para>Description with several diagrams.</para>
<para>Class relations expressed via an inline dot graph: <dot>
digraph example {
    node [shape=record, fontname=Helvetica, fontsize=10];
    b [ label=&quot;class B&quot; URL=&quot;\ref DoxygenList&quot;];
    c [ label=&quot;class C&quot; URL=&quot;\ref CodeBlock&quot;];
    b -&gt; c [ arrowhead=&quot;open&quot;, style=&quot;dashed&quot; ];
}
</dot>
 Note that the classes in the above graph are clickable (in the HTML output).</para>
<para>Receiver class. Can be used to receive and execute commands. After execution of a command, the receiver will send an acknowledgment <plantuml>  Receiver&lt;-Sender  : Command()
  Receiver--&gt;Sender : Ack()</plantuml>
 </para>
    </detaileddescription>
"""
    output = parse(input_xml)
    assert output.to_asciidoc() == """\
Description with several diagrams.

Class relations expressed via an inline dot graph:

[dot]
....
digraph example {
    node [shape=record, fontname=Helvetica, fontsize=10];
    b [ label="class B" URL="
ef DoxygenList"];
    c [ label="class C" URL="
ef CodeBlock"];
    b -> c [ arrowhead="open", style="dashed" ];
}
....

Note that the classes in the above graph are clickable (in the HTML output).

Receiver class. Can be used to receive and execute commands. After execution of a command, the receiver will send an acknowledgment

[plantuml]
....
  Receiver<-Sender  : Command()
  Receiver-->Sender : Ack()
...."""


def test_parse_sections():
    input_xml = """\
    <detaileddescription>
<para>This class demonstrates how all sections supported by Doxygen are handled. <simplesect kind="author"><para>Rob van der Most </para>
</simplesect>
<simplesect kind="attention"><para>Be carefull with this class. It <bold>could</bold> blow up. </para>
</simplesect>
<xrefsect id="bug_1_bug000001"><xreftitle>Bug</xreftitle><xrefdescription><para>Not all sections may be rendered correctly. </para>
</xrefdescription></xrefsect><simplesect kind="copyright"><para>MIT license. </para>
</simplesect>
<simplesect kind="date"><para>28 August 2021 </para>
</simplesect>
<xrefsect id="deprecated_1_deprecated000001"><xreftitle>Deprecated</xreftitle><xrefdescription><para>This empty class should no longer be used. </para>
</xrefdescription></xrefsect><simplesect kind="note"><para>Don&apos;t forget about <computeroutput>this!</computeroutput> </para>
</simplesect>
<simplesect kind="pre"><para>The class should not exist yet. </para>
</simplesect>
<simplesect kind="post"><para>The class suddenly exists. </para>
</simplesect>
<simplesect kind="remark"><para>This class does not make much sense. </para>
</simplesect>
<simplesect kind="since"><para>0.7.6 </para>
</simplesect>
<xrefsect id="todo_1_todo000001"><xreftitle>Todo</xreftitle><xrefdescription><para>Create some content here. </para>
</xrefdescription></xrefsect><simplesect kind="warning"><para>Do not use this class ever! </para>
</simplesect>
</para>
    </detaileddescription>
"""
    output = parse(input_xml)
    assert output.to_asciidoc() == """\
This class demonstrates how all sections supported by Doxygen are handled.

.Author
[NOTE]
====
Rob van der Most
====

[CAUTION]
====
Be carefull with this class. It **could** blow up.
====

.Bug
[NOTE]
====
Not all sections may be rendered correctly.
====

.Copyright
[NOTE]
====
MIT license.
====

.Date
[NOTE]
====
28 August 2021
====

.Deprecated
[NOTE]
====
This empty class should no longer be used.
====

[NOTE]
====
Don't forget about ``this!``
====

.Pre
[NOTE]
====
The class should not exist yet.
====

.Post
[NOTE]
====
The class suddenly exists.
====

[NOTE]
====
This class does not make much sense.
====

.Since
[NOTE]
====
0.7.6
====

.Todo
[NOTE]
====
Create some content here.
====

[WARNING]
====
Do not use this class ever!
===="""


def test_parse_function():
    input_xml = """\
        <detaileddescription>
<para>Complete documentation for a function or method.</para>
<para><parameterlist kind="param"><parameteritem>
<parameternamelist>
<parametername direction="in">first</parametername>
</parameternamelist>
<parameterdescription>
<para>The first parameter. </para>
</parameterdescription>
</parameteritem>
<parameteritem>
<parameternamelist>
<parametername direction="out">second</parametername>
</parameternamelist>
<parameterdescription>
<para>The second parameter. </para>
</parameterdescription>
</parameteritem>
<parameteritem>
<parameternamelist>
<parametername direction="inout">third</parametername>
</parameternamelist>
<parameterdescription>
<para>The third parameter. </para>
</parameterdescription>
</parameteritem>
</parameterlist>
<simplesect kind="return"><para>A status code </para>
</simplesect>
<parameterlist kind="retval"><parameteritem>
<parameternamelist>
<parametername>0</parametername>
</parameternamelist>
<parameterdescription>
<para>All is ok. </para>
</parameterdescription>
</parameteritem>
<parameteritem>
<parameternamelist>
<parametername>1</parametername>
</parameternamelist>
<parameterdescription>
<para>Something went wrong. </para>
</parameterdescription>
</parameteritem>
</parameterlist>
<parameterlist kind="exception"><parameteritem>
<parameternamelist>
<parametername>std::logic_error</parametername>
</parameternamelist>
<parameterdescription>
<para>Something is wrong with the logic. </para>
</parameterdescription>
</parameteritem>
</parameterlist>
<parameterlist kind="templateparam"><parameteritem>
<parameternamelist>
<parametername>Type</parametername>
</parameternamelist>
<parameterdescription>
<para>The type to do something with. </para>
</parameterdescription>
</parameteritem>
</parameterlist>
</para>
        </detaileddescription>
"""
    output = parse(input_xml)

    templateparam_section = output.pop_section("templateparam")
    assert templateparam_section is not None
    assert templateparam_section.name == "templateparam"
    assert len(templateparam_section.contents) == 1
    assert templateparam_section.contents[0].name == "Type"
    assert not templateparam_section.contents[0].direction
    assert templateparam_section.contents[0].to_asciidoc() == "The type to do something with."

    exception_section = output.pop_section("exception")
    assert exception_section is not None
    assert exception_section.name == "exception"
    assert len(exception_section.contents) == 1
    assert exception_section.contents[0].name == "std::logic_error"
    assert not exception_section.contents[0].direction
    assert exception_section.contents[0].to_asciidoc() == "Something is wrong with the logic."

    retval_section = output.pop_section("retval")
    assert retval_section is not None
    assert retval_section.name == "retval"
    assert len(retval_section.contents) == 2
    assert retval_section.contents[0].name == "0"
    assert not retval_section.contents[0].direction
    assert retval_section.contents[0].to_asciidoc() == "All is ok."
    assert retval_section.contents[1].name == "1"
    assert not retval_section.contents[1].direction
    assert retval_section.contents[1].to_asciidoc() == "Something went wrong."

    return_section = output.pop_section("return")
    assert return_section is not None
    assert return_section.name == "return"
    assert len(return_section.contents) == 1
    assert return_section.contents[0].to_asciidoc() == "A status code"

    param_section = output.pop_section("param")
    assert param_section is not None
    assert param_section.name == "param"
    assert len(param_section.contents) == 3
    assert param_section.contents[0].name == "first"
    assert param_section.contents[0].direction == "in"
    assert param_section.contents[0].to_asciidoc() == "The first parameter."
    assert param_section.contents[1].name == "second"
    assert param_section.contents[1].direction == "out"
    assert param_section.contents[1].to_asciidoc() == "The second parameter."
    assert param_section.contents[2].name == "third"
    assert param_section.contents[2].direction == "inout"
    assert param_section.contents[2].to_asciidoc() == "The third parameter."

    assert output.to_asciidoc() == """\
Complete documentation for a function or method."""


def test_parse_links():
    input_xml = """\
    <detaileddescription>
<para><ref refid="classasciidoxy_1_1descriptions_1_1_links" kindref="compound">Links</ref> to other elements.</para>
<para>Some other test classes are: <itemizedlist>
<listitem><para><ref refid="classasciidoxy_1_1descriptions_1_1_code_block" kindref="compound">CodeBlock</ref> for code blocks. </para>
</listitem>
<listitem><para><ref refid="classasciidoxy_1_1descriptions_1_1_diagrams" kindref="compound">Diagrams</ref> for plantUML and Dot. </para>
</listitem>
<listitem><para><ref refid="classasciidoxy_1_1descriptions_1_1_sections" kindref="compound">Sections</ref> for all kinds of sections.</para>
</listitem>
</itemizedlist>
Of course there is also <ref refid="descriptions_8hpp_1ac2b05985028362b43839a108f8b30a24" kindref="member">FunctionDocumentation()</ref>. </para>
    </detaileddescription>
"""
    output = parse(input_xml)
    assert output.to_asciidoc() == """\
<<classasciidoxy_1_1descriptions_1_1_links,Links>> to other elements.

Some other test classes are:

* <<classasciidoxy_1_1descriptions_1_1_code_block,CodeBlock>> for code blocks.

* <<classasciidoxy_1_1descriptions_1_1_diagrams,Diagrams>> for plantUML and Dot.

* <<classasciidoxy_1_1descriptions_1_1_sections,Sections>> for all kinds of sections.

Of course there is also <<descriptions_8hpp_1ac2b05985028362b43839a108f8b30a24,FunctionDocumentation()>>."""
