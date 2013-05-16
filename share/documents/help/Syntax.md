# Syntax

Plume uses Markdown for document edition. It supports standard Markdown syntax along with some additional features
coming from the [PHP-Markdown][2] implementation.

If you are not familiar with Markdown or just want a little reminder about its syntax, please visit the official
[Markdown Syntax Documentation][1].

(?) A [Markdown Cheat Sheet](/help:MarkdownCheatSheet) is also available when editing documents.


## Additional features


### Extra syntax

When rendering documents, you can use some PHP-Markdown style syntaxes.


#### Strikethrough

Double `~` characters will be treated as delimiters for strikethrough texts, e.g. `this is ~~good~~ bad`.


#### Superscript

A simple `^` character will handle superscript, requiring complex values to be enclosed in parenthesis, e.g.
`this is the 2^(nd) time`


### URL auto-linking

Any Email address and URLs beginning with HTTP(S) and FTP protocols or with `www.` will automatically be turned into
HTML links.


### Fenced code blocks

Along with the traditional Markdown code block syntax using indented text, you can use 3 or more `~` or `backticks` to
handle PHP-Markdown style fenced code blocks.

If you want the code to be highlighted, an optional language name should be appended to the opening fence.


### Tables

For tables handling, which isn't part of the standard Markdown, you can use the [PHP-Markdown tables][3] syntax.


[1]: http://daringfireball.net/projects/markdown/syntax
[2]: http://michelf.ca/projects/php-markdown/
[3]: http://michelf.ca/projects/php-markdown/extra/#table
