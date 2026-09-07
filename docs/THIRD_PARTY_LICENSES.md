# 第三方依赖版权与许可证说明

核对日期：2026-09-07。适用 cn-stock-mcp 0.2.3 的 Windows CPython 3.13 固定运行时。

本项目核心代码采用 MIT。下面的依赖分别受各自许可证约束；它们的代码许可不授予股票、行情或其他数据内容的使用权。数据用途限制见 [数据权限核对](DATA_RIGHTS_REGISTER.md)。

## 本次分发方式

wheel / sdist 包含 cn-stock-mcp 自身代码、文档、可选 Skill 和本页的许可证附件，不打包第三方依赖实现或市场数据集。依赖由客户按固定约束从 PyPI 分别安装，原安装包的许可证和通知随各依赖保留。

本页整理 69 项实际 Windows 运行依赖。包版本与原文来源记录在 [机器可读清单](../third_party_licenses/manifest.json)，附件保留原字节及 SHA256；同一个包内相同文本去重并保留所有来源路径。发行工具、pip 本身和未进入实际运行依赖图的约束项不列为产品运行依赖。

## 分发义务与审阅重点

- MIT、BSD、ISC、PSF 等组件应保留其版权、许可和免责声明；禁止擅自使用作者姓名为产品背书的条件以原文为准。
- Apache 2.0 组件应保留许可证与适用通知，修改其代码时标明修改。对应 NOTICE 和附带文本一并保留在附件中。
- certifi、orjson、tqdm 涉及 MPL 2.0。相关通知和完整 MPL 文本已随附件提供；若以后分发或修改这些组件，需满足其适用源代码形式及获取要求。
- numpy、pywin32 等包还附有内部组件许可证、例外与版权声明。不能把包级元数据的单个名称视为所有内含文件都使用同一许可证；附件保留这些原始文本，包括 pywin32 内 adodbapi 的 LGPL 及 numpy 所附运行库条款。
- 本次没有重新分发或修改依赖实现。今后若增加离线依赖包、便携运行时、合并可执行文件或供应商代码修改，应按实际分发内容重审源代码、重链接及通知等义务。

这是一份针对本次制品组成的许可与通知核对记录，不是对第三方数据、商标或任何用途的授权书。

## 固定版本清单

| 依赖 | 固定版本 | 声明的许可证 | 原文 / 通知 |
| --- | --- | --- | --- |
| [akshare](https://pypi.org/project/akshare/1.18.84/) | 1.18.84 | MIT | [1](../third_party_licenses/akshare-1.18.84-01-LICENSE.txt) |
| [annotated-doc](https://pypi.org/project/annotated-doc/0.0.5/) | 0.0.5 | MIT | [1](../third_party_licenses/annotated-doc-0.0.5-01-LICENSE.txt) |
| [annotated-types](https://pypi.org/project/annotated-types/0.8.0/) | 0.8.0 | MIT | [1](../third_party_licenses/annotated-types-0.8.0-01-LICENSE.txt) |
| [anyio](https://pypi.org/project/anyio/4.14.2/) | 4.14.2 | MIT | [1](../third_party_licenses/anyio-4.14.2-01-LICENSE.txt) |
| [attrs](https://pypi.org/project/attrs/26.1.0/) | 26.1.0 | MIT | [1](../third_party_licenses/attrs-26.1.0-01-LICENSE.txt) |
| [beautifulsoup4](https://pypi.org/project/beautifulsoup4/4.15.0/) | 4.15.0 | MIT License | [1](../third_party_licenses/beautifulsoup4-4.15.0-01-AUTHORS.txt)、[2](../third_party_licenses/beautifulsoup4-4.15.0-02-LICENSE.txt) |
| [cachetools](https://pypi.org/project/cachetools/7.1.7/) | 7.1.7 | MIT | [1](../third_party_licenses/cachetools-7.1.7-01-LICENSE.txt) |
| [certifi](https://pypi.org/project/certifi/2026.7.22/) | 2026.7.22 | MPL-2.0 | [1](../third_party_licenses/certifi-2026.7.22-01-LICENSE.txt) |
| [cffi](https://pypi.org/project/cffi/2.1.1/) | 2.1.1 | MIT-0 | [1](../third_party_licenses/cffi-2.1.1-01-LICENSE.txt) |
| [charset-normalizer](https://pypi.org/project/charset-normalizer/3.5.0/) | 3.5.0 | MIT | [1](../third_party_licenses/charset-normalizer-3.5.0-01-LICENSE.txt) |
| [click](https://pypi.org/project/click/8.4.2/) | 8.4.2 | BSD-3-Clause | [1](../third_party_licenses/click-8.4.2-01-LICENSE.txt.txt) |
| [colorama](https://pypi.org/project/colorama/0.4.6/) | 0.4.6 | License :: OSI Approved :: BSD License | [1](../third_party_licenses/colorama-0.4.6-01-LICENSE.txt.txt) |
| [cryptography](https://pypi.org/project/cryptography/50.0.0/) | 50.0.0 | Apache-2.0 OR BSD-3-Clause | [1](../third_party_licenses/cryptography-50.0.0-01-LICENSE.txt)、[2](../third_party_licenses/cryptography-50.0.0-02-LICENSE.APACHE.txt)、[3](../third_party_licenses/cryptography-50.0.0-03-LICENSE.BSD.txt) |
| [curl-cffi](https://pypi.org/project/curl-cffi/0.16.0/) | 0.16.0 | MIT | [1](../third_party_licenses/curl-cffi-0.16.0-01-LICENSE.txt) |
| [decorator](https://pypi.org/project/decorator/5.3.1/) | 5.3.1 | BSD-2-Clause | [1](../third_party_licenses/decorator-5.3.1-01-LICENSE.txt.txt) |
| [et-xmlfile](https://pypi.org/project/et-xmlfile/2.0.0/) | 2.0.0 | MIT | [1](../third_party_licenses/et-xmlfile-2.0.0-01-LICENCE.python.txt)、[2](../third_party_licenses/et-xmlfile-2.0.0-02-LICENCE.rst.txt) |
| [h11](https://pypi.org/project/h11/0.16.0/) | 0.16.0 | MIT | [1](../third_party_licenses/h11-0.16.0-01-LICENSE.txt.txt) |
| [html5lib](https://pypi.org/project/html5lib/1.1/) | 1.1 | MIT License | [1](../third_party_licenses/html5lib-1.1-01-LICENSE.txt) |
| [httpcore](https://pypi.org/project/httpcore/1.0.9/) | 1.0.9 | BSD-3-Clause | [1](../third_party_licenses/httpcore-1.0.9-01-LICENSE.md.txt) |
| [httpcore2](https://pypi.org/project/httpcore2/2.10.0/) | 2.10.0 | BSD-3-Clause | [1](../third_party_licenses/httpcore2-2.10.0-01-LICENSE.md.txt) |
| [httpx](https://pypi.org/project/httpx/0.28.1/) | 0.28.1 | BSD-3-Clause | [1](../third_party_licenses/httpx-0.28.1-01-LICENSE.md.txt) |
| [httpx2](https://pypi.org/project/httpx2/2.10.0/) | 2.10.0 | BSD-3-Clause | [1](../third_party_licenses/httpx2-2.10.0-01-LICENSE.md.txt) |
| [idna](https://pypi.org/project/idna/3.18/) | 3.18 | BSD-3-Clause | [1](../third_party_licenses/idna-3.18-01-LICENSE.md.txt) |
| [jsonpath](https://pypi.org/project/jsonpath/0.82.2/) | 0.82.2 | MIT | [1](../third_party_licenses/jsonpath-0.82.2-01-jsonpath.py-license-header.txt) |
| [jsonschema](https://pypi.org/project/jsonschema/4.26.0/) | 4.26.0 | MIT | [1](../third_party_licenses/jsonschema-4.26.0-01-COPYING.txt) |
| [jsonschema-specifications](https://pypi.org/project/jsonschema-specifications/2025.9.1/) | 2025.9.1 | MIT | [1](../third_party_licenses/jsonschema-specifications-2025.9.1-01-COPYING.txt) |
| [lxml](https://pypi.org/project/lxml/6.1.1/) | 6.1.1 | BSD-3-Clause | [1](../third_party_licenses/lxml-6.1.1-01-LICENSE.txt.txt)、[2](../third_party_licenses/lxml-6.1.1-02-LICENSES.txt.txt) |
| [markdown-it-py](https://pypi.org/project/markdown-it-py/4.2.0/) | 4.2.0 | License :: OSI Approved :: MIT License | [1](../third_party_licenses/markdown-it-py-4.2.0-01-LICENSE.txt)、[2](../third_party_licenses/markdown-it-py-4.2.0-02-LICENSE.markdown-it.txt) |
| [mcp](https://pypi.org/project/mcp/2.0.0/) | 2.0.0 | MIT | [1](../third_party_licenses/mcp-2.0.0-01-LICENSE.txt) |
| [mcp-types](https://pypi.org/project/mcp-types/2.0.0/) | 2.0.0 | MIT | [1](../third_party_licenses/mcp-types-2.0.0-01-LICENSE.txt) |
| [mdurl](https://pypi.org/project/mdurl/0.1.2/) | 0.1.2 | License :: OSI Approved :: MIT License | [1](../third_party_licenses/mdurl-0.1.2-01-LICENSE.txt) |
| [mini-racer](https://pypi.org/project/mini-racer/0.14.1/) | 0.14.1 | ISC | [1](../third_party_licenses/mini-racer-0.14.1-01-AUTHORS.md.txt)、[2](../third_party_licenses/mini-racer-0.14.1-02-LICENSE.txt) |
| [numpy](https://pypi.org/project/numpy/2.5.2/) | 2.5.2 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | [1](../third_party_licenses/numpy-2.5.2-01-LICENSE.txt.txt)、[2](../third_party_licenses/numpy-2.5.2-02-LICENSE.txt.txt)、[3](../third_party_licenses/numpy-2.5.2-03-COPYING.txt)、[4](../third_party_licenses/numpy-2.5.2-04-LICENSE.txt)、[5](../third_party_licenses/numpy-2.5.2-05-dragon4_LICENSE.txt.txt)、[6](../third_party_licenses/numpy-2.5.2-06-LICENSE.md.txt)、[7](../third_party_licenses/numpy-2.5.2-07-LICENSE.txt)、[8](../third_party_licenses/numpy-2.5.2-08-LICENSE.md.txt)、[9](../third_party_licenses/numpy-2.5.2-09-LICENSE.txt.txt)、[10](../third_party_licenses/numpy-2.5.2-10-LICENSE.txt)、[11](../third_party_licenses/numpy-2.5.2-11-LICENSE.md.txt)、[12](../third_party_licenses/numpy-2.5.2-12-LICENSE.md.txt)、[13](../third_party_licenses/numpy-2.5.2-13-LICENSE.md.txt)、[14](../third_party_licenses/numpy-2.5.2-14-LICENSE.md.txt)、[15](../third_party_licenses/numpy-2.5.2-15-LICENSE.md.txt)、[16](../third_party_licenses/numpy-2.5.2-16-LICENSE.md.txt)、[17](../third_party_licenses/numpy-2.5.2-17-LICENSE.md.txt) |
| [openpyxl](https://pypi.org/project/openpyxl/3.1.5/) | 3.1.5 | MIT | [1](../third_party_licenses/openpyxl-3.1.5-01-LICENCE.rst.txt) |
| [opentelemetry-api](https://pypi.org/project/opentelemetry-api/1.44.0/) | 1.44.0 | Apache-2.0 | [1](../third_party_licenses/opentelemetry-api-1.44.0-01-LICENSE.txt) |
| [orjson](https://pypi.org/project/orjson/3.11.9/) | 3.11.9 | MPL-2.0 AND (Apache-2.0 OR MIT) | [1](../third_party_licenses/orjson-3.11.9-01-LICENSE-APACHE.txt)、[2](../third_party_licenses/orjson-3.11.9-02-LICENSE-MIT.txt)、[3](../third_party_licenses/orjson-3.11.9-03-LICENSE-MPL-2.0.txt) |
| [packaging](https://pypi.org/project/packaging/26.3/) | 26.3 | Apache-2.0 OR BSD-2-Clause | [1](../third_party_licenses/packaging-26.3-01-LICENSE.txt)、[2](../third_party_licenses/packaging-26.3-02-LICENSE.APACHE.txt)、[3](../third_party_licenses/packaging-26.3-03-LICENSE.BSD.txt) |
| [pandas](https://pypi.org/project/pandas/3.0.5/) | 3.0.5 | BSD 3-Clause License | [1](../third_party_licenses/pandas-3.0.5-01-LICENSE.txt) |
| [pycparser](https://pypi.org/project/pycparser/3.0/) | 3.0 | BSD-3-Clause | [1](../third_party_licenses/pycparser-3.0-01-LICENSE.txt) |
| [pydantic](https://pypi.org/project/pydantic/2.13.4/) | 2.13.4 | MIT | [1](../third_party_licenses/pydantic-2.13.4-01-LICENSE.txt) |
| [pydantic-core](https://pypi.org/project/pydantic-core/2.46.4/) | 2.46.4 | MIT | [1](../third_party_licenses/pydantic-core-2.46.4-01-LICENSE.txt) |
| [pydantic-settings](https://pypi.org/project/pydantic-settings/2.15.0/) | 2.15.0 | MIT | [1](../third_party_licenses/pydantic-settings-2.15.0-01-LICENSE.txt) |
| [pygments](https://pypi.org/project/pygments/2.20.0/) | 2.20.0 | BSD-2-Clause | [1](../third_party_licenses/pygments-2.20.0-01-AUTHORS.txt)、[2](../third_party_licenses/pygments-2.20.0-02-LICENSE.txt) |
| [pyjwt](https://pypi.org/project/pyjwt/2.13.0/) | 2.13.0 | MIT | [1](../third_party_licenses/pyjwt-2.13.0-01-AUTHORS.rst.txt)、[2](../third_party_licenses/pyjwt-2.13.0-02-LICENSE.txt) |
| [python-dateutil](https://pypi.org/project/python-dateutil/2.9.0.post0/) | 2.9.0.post0 | Dual License | [1](../third_party_licenses/python-dateutil-2.9.0.post0-01-LICENSE.txt) |
| [python-dotenv](https://pypi.org/project/python-dotenv/1.2.2/) | 1.2.2 | BSD-3-Clause | [1](../third_party_licenses/python-dotenv-1.2.2-01-LICENSE.txt) |
| [python-multipart](https://pypi.org/project/python-multipart/0.0.32/) | 0.0.32 | Apache-2.0 | [1](../third_party_licenses/python-multipart-0.0.32-01-LICENSE.txt.txt) |
| [pywin32](https://pypi.org/project/pywin32/312/) | 312 | PSF | [1](../third_party_licenses/pywin32-312-01-license.txt.txt)、[2](../third_party_licenses/pywin32-312-02-License.txt.txt)、[3](../third_party_licenses/pywin32-312-03-LICENSE.txt.txt)、[4](../third_party_licenses/pywin32-312-04-License.txt.txt)、[5](../third_party_licenses/pywin32-312-05-LICENSE.txt)、[6](../third_party_licenses/pywin32-312-06-README.txt.txt)、[7](../third_party_licenses/pywin32-312-07-License.txt.txt)、[8](../third_party_licenses/pywin32-312-08-NOTICE.md.txt) |
| [referencing](https://pypi.org/project/referencing/0.37.0/) | 0.37.0 | MIT | [1](../third_party_licenses/referencing-0.37.0-01-COPYING.txt) |
| [requests](https://pypi.org/project/requests/2.34.2/) | 2.34.2 | Apache-2.0 | [1](../third_party_licenses/requests-2.34.2-01-LICENSE.txt)、[2](../third_party_licenses/requests-2.34.2-02-NOTICE.txt) |
| [rich](https://pypi.org/project/rich/15.0.0/) | 15.0.0 | MIT | [1](../third_party_licenses/rich-15.0.0-01-LICENSE.txt) |
| [rpds-py](https://pypi.org/project/rpds-py/2026.6.3/) | 2026.6.3 | MIT | [1](../third_party_licenses/rpds-py-2026.6.3-01-LICENSE.txt) |
| [shellingham](https://pypi.org/project/shellingham/1.5.4/) | 1.5.4 | ISC License | [1](../third_party_licenses/shellingham-1.5.4-01-LICENSE.txt) |
| [six](https://pypi.org/project/six/1.17.0/) | 1.17.0 | MIT | [1](../third_party_licenses/six-1.17.0-01-LICENSE.txt) |
| [soupsieve](https://pypi.org/project/soupsieve/2.9.2/) | 2.9.2 | MIT | [1](../third_party_licenses/soupsieve-2.9.2-01-LICENSE.md.txt) |
| [sse-starlette](https://pypi.org/project/sse-starlette/3.4.8/) | 3.4.8 | BSD-3-Clause | [1](../third_party_licenses/sse-starlette-3.4.8-01-AUTHORS.txt)、[2](../third_party_licenses/sse-starlette-3.4.8-02-LICENSE.txt) |
| [starlette](https://pypi.org/project/starlette/1.6.0/) | 1.6.0 | BSD-3-Clause | [1](../third_party_licenses/starlette-1.6.0-01-LICENSE.md.txt) |
| [tabulate](https://pypi.org/project/tabulate/0.10.0/) | 0.10.0 | MIT | [1](../third_party_licenses/tabulate-0.10.0-01-LICENSE.txt) |
| [tenacity](https://pypi.org/project/tenacity/9.1.4/) | 9.1.4 | Apache 2.0 | [1](../third_party_licenses/tenacity-9.1.4-01-LICENSE.txt) |
| [tqdm](https://pypi.org/project/tqdm/4.70.0/) | 4.70.0 | MPL-2.0 AND MIT | [1](../third_party_licenses/tqdm-4.70.0-01-LICENCE.txt) |
| [truststore](https://pypi.org/project/truststore/0.10.4/) | 0.10.4 | MIT | [1](../third_party_licenses/truststore-0.10.4-01-LICENSE.txt) |
| [typer](https://pypi.org/project/typer/0.27.1/) | 0.27.1 | MIT | [1](../third_party_licenses/typer-0.27.1-01-LICENSE.txt)、[2](../third_party_licenses/typer-0.27.1-02-LICENSE.txt.txt) |
| [typing-extensions](https://pypi.org/project/typing-extensions/4.16.0/) | 4.16.0 | PSF-2.0 | [1](../third_party_licenses/typing-extensions-4.16.0-01-LICENSE.txt) |
| [typing-inspection](https://pypi.org/project/typing-inspection/0.4.4/) | 0.4.4 | MIT | [1](../third_party_licenses/typing-inspection-0.4.4-01-LICENSE.txt) |
| [tzdata](https://pypi.org/project/tzdata/2026.3/) | 2026.3 | Apache-2.0 | [1](../third_party_licenses/tzdata-2026.3-01-LICENSE.txt)、[2](../third_party_licenses/tzdata-2026.3-02-LICENSE_APACHE.txt) |
| [urllib3](https://pypi.org/project/urllib3/2.7.0/) | 2.7.0 | MIT | [1](../third_party_licenses/urllib3-2.7.0-01-LICENSE.txt.txt) |
| [uvicorn](https://pypi.org/project/uvicorn/0.52.1/) | 0.52.1 | BSD-3-Clause | [1](../third_party_licenses/uvicorn-0.52.1-01-LICENSE.md.txt) |
| [webencodings](https://pypi.org/project/webencodings/0.5.1/) | 0.5.1 | BSD | [1](../third_party_licenses/webencodings-0.5.1-01-LICENSE.txt) |
| [xlrd](https://pypi.org/project/xlrd/2.0.2/) | 2.0.2 | BSD | [1](../third_party_licenses/xlrd-2.0.2-01-LICENSE.txt) |

## 两个旧包的原文补齐

- jsonpath 0.82.2：PyPI 固定源码包 SHA256 为 d87ef2bcbcded68ee96bc34c1809b69457ecec9b0c4dd471658a12bd391002d1。许可证位于 jsonpath.py 文件头；附件仅摘取完整版权和 MIT 许可注释，不分发实现代码。
- webencodings 0.5.1：其 wheel 和 sdist 元数据声明 BSD，源码头明确引用 LICENSE，但发行包遗漏独立文件。附件来自官方仓库 v0.5.1 标签，且该标签的模块与 PyPI 固定 sdist 中模块逐字节一致；许可证为 BSD 三条款，原文 SHA256 为 f23bae6ada76095610a77137fb92aec7342723900211c5826d54b4c57907ca56。

约束版本变更后应重新生成实际依赖图并复核对应原文，不能沿用本清单宣称新版本完成审核。
