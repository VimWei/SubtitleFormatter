# 程序设计需求规范

## 1. 任务目标

为输入的文本添加必要的标点符号，并在合适的位置进行断行，以使每一行的长度适中，在保持原文的语义的同时，尽量提升可理解性。

## 2. 处理规则

总原则：完全保留原文内容，只关注格式化处理。

1. 关于内容：除了以下两点，对其余文字内容不做任何添删改操作。
    - 删除口语中经常出现的无意义的重复话语或停顿词，如"um、uh、well"等
    - 修正句首大小写
2. 关于格式化：包括智能断句和智能断行
    - 智能断句：基于spacy模型进行智能断句，在形式上体现为，仅在必要的位置添加标点符号，而不删除或更改已有的标点符号。
    - 智能断行：默认采用一句一行的格式；如果一行的字符数超过78个，则进一步分析句子的语法结构、习惯用法等语言特征，将其拆分为多行，使其每一行的字符长度适中、意群独立，并尽量保持原文的语义。


## 3. 处理案例

### 输入文本：
```
my name is Tom Seeley and I'm coming to
you on March 17 St. Patrick's Day and
2020 in my laboratory bee laboratory here
at Cornell University and I wish I could
be with you in person but thanks to the
coronavirus we're apart today
nevertheless well and sharing with you
the stock and I hope you will enjoy it
```

### 期望输出：
```
My name is Tom Seeley,
and I'm coming to you on March 17, St. Patrick's Day and 2020.
In my laboratory, bee laboratory, here at Cornell University,
I wish I could be with you in person.
But thanks to the coronavirus, we're apart today.
Nevertheless, well and sharing with you the stock,
and I hope you will enjoy it.

```

